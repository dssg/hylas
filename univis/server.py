#!/usr/bin/env python

from flask import Flask
from flask import jsonify
from flask import request
import numpy as np

from sklearn.metrics import f1_score, precision_recall_curve

models = []

def register_model(fitted_clf, time, M_train, M_test, labels_train, 
                   labels_test):
    models.append({
        'clf': fitted_clf, 
        'time': time, 
        'M_train': M_train,
        'M_test': M_test, 
        'labels_train': labels_train,
        'labels_test': labels_test, 
        'clf_name': type(fitted_clf).__name__,
        'predicted' : fitted_clf.predict(M_test),
        'pred_proba': fitted_clf.predict_proba(M_test)[:,-1]})



app = Flask(__name__)

@app.route('/list_models', methods=['GET'])
def list_models():
    ret = [{'model_id': idx, 'time': model['time'], 
            'name': model['clf_name']} for idx, model in 
           enumerate(models)]
    return jsonify(data=ret)

@app.route('/model_info', methods=['GET']):
    model_id = int(request.args.get('model_id'))
    model = models[model_id]
    perf_metrics = {'f1_score' : f1_score(model['labels_test'], 
                    model['predicted'])}
    fpr, tpr, thresholds = roc_curve(model['labels_test'], model['pred_proba']) 
    graphs = {'roc': {'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds}}
    # TODO other perf metrics
    ret = {'model_id': model_id, 'name': model['clf_name'], 
           'time': model['time'], 'perf_metrics': perf_metrics, 
           'graphs': graphs}
    return jsonify(data=ret)

#TODO next is top n units, top n features

@app.route('/top_features', methods=['GET'])
def top_features():
    n = int(request.args.get('n', '10'))
    return jsonify(data=top_feature_cols[:n])    

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

