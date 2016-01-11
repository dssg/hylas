#!/usr/bin/env python

import os
import json
import uuid
import cPickle
from datetime import datetime as dt

from flask import Flask
from flask import redirect
from flask import jsonify
from flask import request
from flask import send_from_directory
from flask import send_file

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask.ext.login import current_user
from flask.ext.security.utils import encrypt_password

import numpy as np

from sklearn.metrics import f1_score, roc_auc_score, roc_curve, precision_recall_curve
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.preprocessing import normalize

from diogenes.utils import open_csv_as_sa
from diogenes.utils import remove_cols
from diogenes.display import get_top_features
from diogenes.display import Report
from diogenes.grid_search import Experiment
from diogenes.grid_search.standard_clfs import DBG_std_clfs

from config import SECRET_KEY, DATABASE_URI, SALT, REPORT_FORMAT

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Setting up Flask-security
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = SALT
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/login'

db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.before_first_request
def create_user():
    db.create_all()
    db.session.commit()

# Model maintanance
all_models = {}
last_experiments = {}

def get_models(user):
    try:
        return all_models[user]
    except KeyError:
        ret = []
        all_models[user] = ret
        return ret

def clear_models(user):
    get_models(user)[:] = []

def register_model(
        user,
        fitted_clf, 
        time, 
        M_train, 
        M_test, 
        labels_train, 
        labels_test, 
        feature_names, 
        uid_feature):
    models = get_models(user)
    # M_train, etc. are numpy array
    # feature names is names of colums
    # uid_feature is the name of the column that has the unique id
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

# Endpoints
# TODO use tokens rather than login. Less of a security risk
@app.route('/list_models', methods=['GET'])
@login_required
def list_models():
    models = get_models(current_user.id)
    ret = [{'model_id': idx, 'time': model['time'], 
            'name': model['clf_name']} for idx, model in 
           enumerate(models)]
    return jsonify(data=ret)

@app.route('/model_info', methods=['GET'])
@login_required
def model_info():
    models = get_models(current_user.id)
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
@login_required
def top_features():
    models = get_models(current_user.id)
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
@login_required
def top_units():
    models = get_models(current_user.id)
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
@login_required
def unit():
    models = get_models(current_user.id)
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
@login_required
def units():
    models = get_models(current_user.id)
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
@login_required
def distribution():
    models = get_models(current_user.id)
    model_id = int(request.args.get('model_id', '0'))
    model = models[model_id]
    feature = request.args.get('feature')
    labels_test = model['labels_test'].astype(bool)
    col = model['M_train'][:, model['col_idx'][feature]]
    positive = col[labels_test]
    negative = col[np.logical_not(labels_test)]
    ret = {'positive': list(positive), 'negative': list(negative)}
    return jsonify(data=ret)

@app.route('/similar', methods=['GET'])
@login_required
def similar():
    models = get_models(current_user.id)
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

def register_exp(exp, uid_feature):
    exp.run()
    last_experiments[current_user.id] = exp
    clear_models(current_user.id)
    for trial in exp.trials:
        for subset in trial.runs:
            for run in subset:
                register_model(
                        current_user.id,
                        run.clf, 
                        dt.now(),
                        run.M[run.train_indices], 
                        run.M[run.test_indices], 
                        run.labels[run.train_indices], 
                        run.labels[run.test_indices], 
                        run.col_names, 
                        uid_feature)

def run_csv(fin, uid_feature, label_feature):
    sa = open_csv_as_sa(fin)
    labels = sa[label_feature]
    M = remove_cols(sa, label_feature)
    exp = Experiment(M, labels, clfs=DBG_std_clfs)
    register_exp(exp, uid_feature)

@app.route('/upload_csv', methods=['POST'])
@login_required
def upload_csv():
    fin = request.files['file'].stream
    uid_feature = request.values['otherInfo[unit_id_feature]']
    label_feature = request.values['otherInfo[label_feature]']
    run_csv(fin, uid_feature, label_feature)
    # TODO return 201 with link to new resource
    return "OK"

@app.route('/upload_pkl', methods=['POST'])
@login_required
def upload_pkl():
    fin = request.files['file'].stream
    uid_feature = request.values['otherInfo[unit_id_feature]']
    exp = cPickle.load(fin)
    register_exp(exp, uid_feature)
    # TODO return 201 with link to new resource
    return "OK"

@app.route('/download_pdf', methods=['GET'])
@login_required
def download_pdf():
    try:
        exp = last_experiments[current_user.id]
    except KeyError:
        return 'No CSV Uploaded', 409
    base_path = os.path.join('pdf', '{}'.format(current_user.id))
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    report_path = os.path.join(base_path, '{}.pdf'.format(uuid.uuid4()))
    report = Report(exp=exp, report_path=report_path)
    REPORT_FORMAT(report, exp)
    report.to_pdf(verbose=False)
    return send_file(report_path, as_attachment=True)

@app.route('/download_csv', methods=['GET'])
@login_required
def download_csv():
    try:
        exp = last_experiments[current_user.id]
    except KeyError:
        return 'No CSV Uploaded', 409
    base_path = os.path.join('csv', '{}'.format(current_user.id))
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    report_path = os.path.join(base_path, '{}.csv'.format(uuid.uuid4()))
    exp.make_csv(file_name=report_path)
    return send_file(report_path, as_attachment=True)

@app.route('/download_pkl', methods=['GET'])
@login_required
def download_pkl():
    try:
        exp = last_experiments[current_user.id]
    except KeyError:
        return 'No CSV Uploaded', 409
    base_path = os.path.join('pkl', '{}'.format(current_user.id))
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    report_path = os.path.join(base_path, '{}.pkl'.format(uuid.uuid4()))
    with open(report_path, 'wb') as pkl_file:
        cPickle.dump(exp, pkl_file)
    return send_file(report_path, as_attachment=True)
    
@app.route('/', methods=['GET'])
@login_required
def index():
    return send_from_directory('views', 'index.html')    

# http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
@app.route('/js/<path:path>', methods=['GET'])
@login_required
def js_path(path):
    return send_from_directory(os.path.join('public', 'javascripts'), path)    

@app.route('/css/<path:path>', methods=['GET'])
@login_required
def css_path(path):
    return send_from_directory(os.path.join('public', 'css'), path)    

@app.route('/images/<path:path>', methods=['GET'])
@login_required
def image_path(path):
    return send_from_directory(os.path.join('public', 'images'), path)    

@app.route('/views/<path:path>', methods=['GET'])
@login_required
def views_path(path):
    return send_from_directory('views', path)    

@app.route('/bower/<path:path>', methods=['GET'])
@login_required
def bower_path(path):
    return send_from_directory('bower_components', path)    

@app.route('/reset', methods=['POST'])
@login_required
def reset():
    with open('sample.csv') as fin:
        run_csv(fin, 'id', 'label')
    return "OK"

if __name__ == '__main__':

    app.run(debug=True)

