import re
import numpy as np
import pandas as pd
import hashlib
import config
import json
import os
from sklearn.ensemble import RandomForestClassifier
from database import get_summary_features, connect
import itertools

def get_top_features(data, time_col, X_cols, y_col, district, X_categories=None, features=['all']):

    """ Try other model params later and return the one with best accuracy """

    rf_very_best_dict = {
        'clf': RandomForestClassifier,
        'param_dict': {
            'n_estimators': [50],
            'criterion': ['entropy'],
            'max_features': [None],
            'max_depth': [3],
            'bootstrap': [True],
            'random_state': [0],
            'n_jobs': [-1],
            }
        }

    clf = generate_models([rf_very_best_dict])[0]

    """ Not sure how to include category data at this point """

    # if X_categories is not None:
    #     print X_categories.head()
    #     # Determine the unique feature categories.
    #     unique_categories = X_categories['feature_category_primary'].unique()
    #     # Drop feature categories that should not be used for modeling.
    #     categories_to_drop = np.array(['id', 'attendance', 'coursework', 'demographic', 'school'])
    #     unique_categories = np.array(list(set(x for x in unique_categories.tolist()).difference(set(x for x in categories_to_drop.tolist()))))
    #     # Add single feature categories to the feature sets.
    #     feat_sets.extend([[x] for x in unique_categories])
    #     # Add all but single feature categories to the feature sets.
    #     feat_sets.extend(list(itertools.combinations(unique_categories, len(unique_categories)-1)))
    #     # Add all categories to the feature sets.
    #     feat_sets.extend(list(itertools.combinations(unique_categories, len(unique_categories))))


    clf_name = str(clf)[:str(clf).index('(')]
    smoted = ''
    subsampled = ''
    train_year = [2013]
    test_year = [2014]
    train_and_test = data[(data['cohort'] <= train_year) | (data['cohort'] >= test_year)]
    X_cols_filtered_by_grade = X_cols
    grade = 11
    highest_grade = 12

    higher_grade_regex = '^(?!' # negation
    for higher_grade in range(grade+1, highest_grade+1):
        higher_grade_regex += r"{time_col}_{grade_level}|".format(time_col=str(time_col),
                                                                          grade_level=str(higher_grade)
                                                                          )
        higher_grade_regex = higher_grade_regex[:-1] # remove last '|'
        higher_grade_regex = higher_grade_regex + ').*'
        regex = re.compile(higher_grade_regex)
        # The regex should select all columns except those prefixed by a higher grade level.
        X_cols_filtered_by_grade = filter(lambda i: regex.search(i), X_cols_filtered_by_grade)


    if X_categories is not None:
        # Filter to only columns/features to be used for modeling.
        filtered_feats = X_categories.loc[X_categories['exclude_when_modeling'] == 0]
        # Filter to only columns/features in the selected feature categories.
        filtered_feats = filtered_feats['feature_name'].loc[filtered_feats['feature_category_primary'].isin(features)]
        category_regex = '('
        for feat in filtered_feats:
            category_regex += r"{feat}|".format(feat=str(feat))
        category_regex = category_regex[:-1] # remove last '|'
        category_regex = category_regex + ')'
        regex = re.compile(category_regex)
        # The regex should select all columns that are a member of each selected feature category.
        X_cols_filtered_by_grade_and_category = filter(lambda i: regex.search(i), X_cols_filtered_by_grade)

        print("  %i features." % (len(X_cols_filtered_by_grade_and_category)))
        x_cols_filtered_by_grade_and_category = X_cols_filtered_by_grade

    # Set training/testing labels (train = 0, test = 1).
    kf_labels = np.where((train_and_test['cohort'] >= test_year), 1, 0)
    train, test = [(np.where(kf_labels == 0)[0], np.where(kf_labels == 1)[0])]
    x = train_and_test[x_cols_filtered_by_grade_and_category].as_matrix()
    y = train_and_test[y_col].as_matrix()
    x_train, y_train = x[train], y[train]

    # Copy the training data and testing feature data before modifications.
    y_train_t = np.copy(y_train)
    cpy_x_train = np.copy(x_train)
    x_train_t = pd.DataFrame(cpy_x_train).fillna(pd.DataFrame(cpy_x_train).mean().fillna(0)).as_matrix()

    # See if this model has already been calculated
    summary_hash = str(hashlib.sha1(json.dumps((str(grade),
                            str(test),
                            str(train),
                            str(clf_name),
                            str(clf.get_params()),
                            str(', '.join(features)),
                            str(subsampled),
                            str(smoted)),
                            sort_keys=True)).hexdigest())

    settings = config.settings['general']['database']
    summary = get_summary_features(settings, summary_hash, district)

    # If model exists, return its top features. Else calculate, and maybe and write to db.
    if summary:
        return str(summary['features'])

    else:
        # Generate "probabilities" for the current hold-out sample being predicted.
        fitted_clf = clf.fit(x_train_t, y_train_t)
        features_list = train_and_test[X_cols_filtered_by_grade_and_category].columns.values

        # Fit a random forest with (mostly) default parameters to determine feature importance
        feature_importance = fitted_clf.feature_importances_

        # make importances relative to max importance
        feature_importance = 100.0 * (feature_importance / feature_importance.max())

        # A threshold below which to drop features from the final data set. Specifically, this number
        # represents the percentage of the most important feature's importance value.
        # Get all features above this importance
        fi_threshold = 1
        important_idx = np.where(feature_importance > fi_threshold)[0]
        important_features = features_list[important_idx]
        sorted_idx = np.argsort(feature_importance[important_idx])[::-1]

        features = zip(important_features[sorted_idx], feature_importance[important_idx][sorted_idx])

        """ Should be writing results to the summary table here """
        return str(features)

def fetch_data(district=None, from_pickle=False, pickle_filename=None, unit_col='student_id', time_col='grade_level'):
    if from_pickle == True and pickle_filename is not None:
        print("Reading pickle file.")
        data = pd.read_pickle(pickle_filename + '.pkl')
        if os.path.isfile(pickle_filename + '_cats' + '.pkl'):
            feature_categories = pd.read_pickle(pickle_filename + '_cats' + '.pkl')
        feature_categories = None
    else:
        # Retrieve time-invariant features, time-variant features, and outcome labels.
        cohorts, features_constant, features_by_time, feature_categories, labels = extract_data(district)
        features_by_time = features_by_time.drop(['cohort', 'academic_year'], 1)

        # Extract features.
        features = extract_features(features_constant, # time-invariant features
                                    features_by_time, # time-variant features
                                    unit_col=unit_col, # instance identifier column
                                    time_col=time_col, # time unit column
                                    )

        # Extract outcome labels.
        labels = labels[['student_id', 'outcome_label']]
        labels = labels.dropna()

        # Extract instance-level data. Each instance has an identifier, one or more features, and a label.
        data = extract_instances(features, labels, unit_col='student_id')

        if pickle_filename is not None:
            data.to_pickle(pickle_filename + '.pkl')
            if feature_categories is not None:
                feature_categories.to_pickle(pickle_filename + '_cats.pkl')

    return data, feature_categories


def extract_instances(features, labels, unit_col):
    # The outcome label is assumed to be the last column in labels.
    labels = labels.rename(columns={labels.columns[-1]: 'label'})

    # Merge all data (identifier, feature(s), and label). Each instance should have one or more features and a label.
    data = pd.merge(features, labels, how='inner', on=[unit_col])

    return data

def extract_features(features_constant, features_by_time, unit_col, time_col, columns_to_dummy=None):
    def flatten_multi_index(df):
        mi = df.columns
        suffixes, prefixes = mi.levels
        col_names = []
        for (i_s, i_p) in zip(*mi.labels):
            col_names.append("{time_col}_{prefix}_{suffix}".format(time_col=str(time_col),
                                                                   prefix=str(prefixes[i_p]),
                                                                   suffix=str(suffixes[i_s]),
                                                                   ))
        df.columns = col_names
        return df

    # If a student has repeated a grade, take only the last record.
    features_by_time.drop_duplicates(subset=[unit_col, time_col], take_last=True, inplace=True)

    # Reshape the features by time so that there is one instance per identifier.
    features_by_time = flatten_multi_index(features_by_time.pivot(index=unit_col, columns=time_col)).reset_index()

    # Merge all feature data.
    features = pd.merge(features_constant, features_by_time, how='outer', on=[unit_col])

    # Encode nominal features to conform with scikit-learn.
    if columns_to_dummy is not None or isinstance(features, pd.Series):
        # Encode only specified feature columns.
        features = pd.get_dummies(features, columns=columns_to_dummy)
    else:
        # Encode all 'object' type feature columns.
        dummy_cols = [features.columns[i] for i, tp in enumerate(features.dtypes) if tp == 'object']
        for col in dummy_cols:
            #print('Encoding feature \"' + col + '\" ...')
            #print('Old dataset shape: ' + str(features.shape))
            temp = pd.get_dummies(features[col], prefix=col)
            features = pd.concat([features, temp], axis=1).drop(col, axis=1)
            #print('New dataset shape: ' + str(features.shape))
            #unique_vals, X[col] = np.unique(X[col], return_inverse=True)

    return features

def extract_data(district):
    engine = connect(config.settings['general']['database'])

    if district == 'wcpss':
        # Data that maps student IDs to cohorts.
        cohort_selection_query = ('''SELECT *
            FROM wake._cohort
            ORDER BY student_id
            ;''')

        # Student-level features that are time-invariant.
        features_constant_selection_query = ('''SELECT *
            FROM wake._cohort_feature
            ORDER BY student_id
            ;''')

        # Student-level features that are time-variant.
        features_by_time_selection_query = ('''SELECT *
            FROM wake._cohort_by_year_feature
            ORDER BY student_id
            ;''')

        # Student-level feature categories.
        #features_categories_selection_query = ('''SELECT *
        #    FROM wake._feature_category
        #    ;''')

        # Student-level outcome labels.
        labels_selection = ('''SELECT *
            FROM  wake._label
            ORDER BY student_id
            ;''')
    elif district == 'vps':
        # Data that maps student IDs to cohorts.
        cohort_selection_query = ('''SELECT *
            FROM vancouver._cohort
            ORDER BY student_id
            ;''')

        # Student-level features that are time-invariant.
        features_constant_selection_query = ('''SELECT *
            FROM vancouver._cohort_feature
            ORDER BY student_id
            ;''')

        # Student-level features that are time-variant.
        features_by_time_selection_query = ('''SELECT *
            FROM vancouver._cohort_by_year_feature
            ORDER BY student_id
            ;''')

        # Student-level feature categories.
        features_categories_selection_query = ('''SELECT *
            FROM vancouver._feature_category
            ;''')

        # Student-level outcome labels.
        labels_selection = ('''SELECT *
            FROM  vancouver._label
            ORDER BY student_id
            ;''')

    cohorts = pd.read_sql(sql=cohort_selection_query, con=engine)
    features_constant = pd.read_sql(sql=features_constant_selection_query, con=engine)
    features_by_time = pd.read_sql(sql=features_by_time_selection_query, con=engine)
    # feature_categories = pd.read_sql(sql=features_categories_selection_query, con=engine)
    feature_categories = None
    labels = pd.read_sql(sql=labels_selection, con=engine)

    return cohorts, features_constant, features_by_time, feature_categories, labels


def generate_models(clf_library):
    """
    This function returns a list of classifiers with all combinations of
    hyperparameters specified in the dictionary of hyperparameter lists.
    usage example:
        lr_dict = {
            'clf': LogisticRegression,
            'param_dict': {
                'C': [0.001, 0.1, 1, 10],
                'penalty': ['l1', 'l2']
                }
            }
        sgd_dict = {
            'clf': SGDClassifier,
            'param_dict': {
                'alpha': [0.0001, 0.001, 0.01, 0.1],
                'penalty': ['l1', 'l2']
                }
            }
        clf_library = [lr_dict, sgd_dict]
        generate_models(clf_library)
    """
    clf_list = []
    for i in clf_library:
        param_dict = i['param_dict']
        dict_list = [dict(itertools.izip_longest(param_dict, v)) for v in itertools.product(*param_dict.values())]
        clf_list = clf_list+[i['clf'](**param_set) for param_set in dict_list]
    return clf_list

def parse_and_order(feat_string):
    top_feats = []
    feat_string = feat_string[2:-2]
    features = re.split('(?:\) *, *\()', feat_string)
    for f in features:
        feat_name, importance = f.split(',')
        importance = float(importance)
        top_feats.append([feat_name, importance])
    return sorted(top_feats, key=lambda x: x[1])
