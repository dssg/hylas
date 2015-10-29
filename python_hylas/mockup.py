#!/usr/bin/env python

from flask import Flask
from flask import jsonify
from flask import request
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from features import get_top_features, fetch_data, parse_and_order

N_ROWS = 100
N_COLS = 10
N_CLASSES = 2

M = np.random.random((N_ROWS, N_COLS))
labels = np.random.randint(N_CLASSES, size=N_ROWS)
feature_names = ['f{}'.format(i) for i in xrange(N_COLS)]
feature_name_back_idx = {name: i for i, name in enumerate(feature_names)}

split = N_ROWS / 2
M_train = M[:split]
labels_train = labels[:split]
M_test = M[split:]
labels_test = labels[:split]

clf = RandomForestClassifier()
clf.fit(M_train, labels_train)

pred_proba = clf.predict_proba(M_test)
top_feature_cols = [feature_names[idx] for idx in 
                np.argsort(clf.feature_importances_)[::-1]]
app = Flask(__name__)


@app.route('/top_features', methods=['GET'])
def top_features():
    n = int(request.args.get('n', '10'))

    unit_col = 'student_id'
    time_col = 'grade_level'
    label_col = 'label'
    district = 'vps'

    data, x_categories = fetch_data(district=district,
                                    unit_col=unit_col,
                                    time_col=time_col
                                    )

    if district == 'wcpss':
        data = data.drop(['age_first_entered_wcpss'], 1)
        data = data.drop(['age_entered_into_us'], 1)

    x_cols = data.columns[(data.columns != label_col) & (data.columns != unit_col) & (data.columns != time_col)]
    y_col = label_col

    top_feature_str = get_top_features(data, time_col, x_cols, y_col, district, x_categories)

    top_n_features = parse_and_order(top_feature_str)[:n]

    return jsonify(data=top_n_features)


@app.route('/top_units', methods=['GET'])
def top_units():
    n = int(request.args.get('n', '10'))
    cols = request.args.get('cols', 'row_num,pred_proba')
    category = int(request.args.get('category', '1'))
    pred_proba_col = pred_proba[:,category]
    sorted_idxs = np.argsort(pred_proba_col)[::-1]
    return_idxs = sorted_idxs[:n]
    ret = {}
    for col in cols.split(','):
        if col == 'row_num':
            ret[col] = return_idxs.tolist()
        elif col == 'pred_proba':
            ret[col] = pred_proba_col[return_idxs].tolist()
        else:
            ret[col] = M_test[return_idxs,feature_name_back_idx[col]].tolist()
    return jsonify(data=ret)

@app.route('/distribution', methods=['GET'])
def distribution():
    col = request.args['col']
    return jsonify(data=list(M_test[::2,feature_name_back_idx[col]]))

if __name__ == '__main__':
    app.run(debug=True)

