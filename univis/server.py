#!/usr/bin/env python

import os
import json

from flask import Flask
from flask import jsonify
from flask import request
from flask import send_from_directory
import numpy as np

from sklearn.metrics import f1_score, roc_auc_score, roc_curve, precision_recall_curve
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.preprocessing import normalize

from diogenes.display import get_top_features

models = []

def register_model(fitted_clf, time, M_train, M_test, labels_train, 
                   labels_test, feature_names, uid_feature):
    col_idx = {col_name: idx for idx, col_name in 
                    enumerate(feature_names)}
    # TODO better distance metric
    norm_M_test = normalize(M_test)
    distances = pairwise_distances(norm_M_test)
    models.append({
        'clf': fitted_clf, 
        'time': time, 
        'M_train': M_train,
        'M_test': M_test, 
        'norm_M_test': norm_M_test,
        'distances': distances,
        'labels_train': labels_train,
        'labels_test': labels_test, 
        'feature_names': feature_names,
        'uid_feature': uid_feature,
        'clf_name': type(fitted_clf).__name__,
        'predicted' : fitted_clf.predict(M_test),
        'pred_proba': fitted_clf.predict_proba(M_test)[:,-1],
        'col_idx': col_idx,
        'uid_idx': {uid: idx for idx, uid in 
            enumerate(M_test[:,col_idx[uid_feature]])}})

app = Flask(__name__)

@app.route('/list_models', methods=['GET'])
def list_models():
    ret = [{'model_id': idx, 'time': model['time'], 
            'name': model['clf_name']} for idx, model in 
           enumerate(models)]
    return jsonify(data=ret)

@app.route('/model_info', methods=['GET'])
def model_info():
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    perf_metrics = {'f1_score' : f1_score(model['labels_test'], 
                    model['predicted']),
                    'roc_auc_score': roc_auc_score(model['labels_test'], 
                    model['predicted'])}
    fpr, tpr, roc_thresholds = roc_curve(model['labels_test'], model['pred_proba']) 
    precision, recall, pr_thresholds = precision_recall_curve(
        model['labels_test'], model['pred_proba'])
    graphs = {'roc': {'fpr': list(fpr), 'tpr': list(tpr), 
                      'thresholds': list(roc_thresholds)},
              'pr': {'precision': list(precision), 'recall': list(recall),
                     'thresholds': list(pr_thresholds)}}
    # TODO other perf metrics
    ret = {'model_id': model_id, 'name': model['clf_name'], 
           'time': model['time'], 'perf_metrics': perf_metrics, 
           'graphs': graphs}
    return jsonify(data=ret)

#TODO next is top n units, top n features

@app.route('/top_features', methods=['GET'])
def top_features():
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    n = int(request.args.get('n', '10'))
    top_features = get_top_features(
            model['clf'], 
            col_names=model['feature_names'],
            n=n)
    ret = [{'feature': feat, 'score': score} for feat, score in 
           top_features]
    return jsonify(data=ret)

@app.route('/top_units', methods=['GET'])
def top_units():
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    n = int(request.args.get('n', '10'))
    pred_proba = model['pred_proba']
    sorted_idxs = np.argsort(pred_proba)[::-1]
    top_idxs = sorted_idxs[:n]
    top_uid = model['M_test'][top_idxs,model['col_idx'][model['uid_feature']]]
    top_scores = pred_proba[top_idxs]
    ret = [{'unit_id': uid, 'score': score} for uid, score in 
           zip(top_uid, top_scores)]
    return jsonify(data=ret)

@app.route('/unit', methods=['GET'])
def unit():
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    unit_id = int(request.args.get('unit_id'))
    features = request.args.get('features', '')
    if not features:
        features = model['feature_names']
    else:
        features = features.split(',')
    row_id = model['uid_idx'][unit_id]
    M_test = model['M_test']
    col_idx = model['col_idx']
    ret = {feat: M_test[row_id, col_idx[feat]] for feat in features}
    return jsonify(data=ret)

@app.route('/units', methods=['GET'])
def units():
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    unit_ids = request.args.get('unit_ids')
    unit_ids = [int(id) for id in unit_ids.split(',')]
    features = request.args.get('features', '')
    if not features:
        features = model['feature_names']
    else:
        features = features.split(',')
    uid_idx = model['uid_idx']
    M_test = model['M_test']
    col_idx = model['col_idx']
    ret = [{feat: M_test[uid_idx[uid], col_idx[feat]] for feat in features}
           for uid in unit_ids]
    return jsonify(data=ret)

@app.route('/distribution', methods=['GET'])
def distribution():
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    feature = request.args.get('feature')
    labels_test = model['labels_test']
    col = model['M_train'][:, model['col_idx'][feature]]
    positive = col[labels_test]
    negative = col[np.logical_not(labels_test)]
    ret = {'positive': list(positive), 'negative': list(negative)}
    return jsonify(data=ret)

@app.route('/similar', methods=['GET'])
def similar():
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    unit_id = int(request.args.get('unit_id'))
    features = request.args.get('features', '').split(',')
    n = int(request.args.get('n', '10'))
    M_test = model['M_test']
    uid_idx = model['uid_idx']
    col_idx = model['col_idx']
    distances = model['distances']
    
    uid_col = M_test[:, model['col_idx'][model['uid_feature']]]
    distances_from_uid = distances[:,uid_idx[unit_id]]
    scores = 1 - distances_from_uid / max(distances_from_uid)
    top_idxs = np.argsort(scores)[::-1][:n]
    top_uids = uid_col[top_idxs]
    top_scores = scores[top_idxs]
    ret = [{'unit_id': uid, 'score': score} for uid, score in
            zip(top_uids, top_scores)]
    return jsonify(data=ret)
    
@app.route('/debug', methods=['GET'])
def debug():
    return send_from_directory('views', 'requester.html')    

@app.route('/', methods=['GET'])
def index():
    return send_from_directory('views', 'index.html')    

# http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
@app.route('/js/<path:path>', methods=['GET'])
def js_path(path):
    return send_from_directory(os.path.join('public', 'javascripts'), path)    

@app.route('/css/<path:path>', methods=['GET'])
def css_path(path):
    return send_from_directory(os.path.join('public', 'css'), path)    

@app.route('/images/<path:path>', methods=['GET'])
def image_path(path):
    return send_from_directory(os.path.join('public', 'images'), path)    

if __name__ == '__main__':

    # for now, build a sample model
    M, labels = make_classification(n_samples=1000)
    M[:,0] = np.arange(1000)
    M_train = M[:800]
    labels_train = labels[:800]
    M_test = M[800:]
    labels_test = labels[800:]
    feature_names = ['f{}'.format(i) for i in xrange(M.shape[1])]
    rf_clf = RandomForestClassifier(n_estimators=10)
    rf_clf.fit(M_train, labels_train)
    register_model(rf_clf, 'November 10, 2015', M_train, M_test, labels_train, labels_test,
                   feature_names, 'f0')
    rf_clf_2 = RandomForestClassifier(n_estimators=100)
    rf_clf_2.fit(M_train, labels_train)
    register_model(rf_clf_2, 'November 12, 2015', M_train, M_test, labels_train, labels_test,
                   feature_names, 'f0')

    app.run(debug=True)

