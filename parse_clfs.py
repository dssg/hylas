import json

from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.dummy import DummyClassifier

clf_classes = {'AdaBoostClassifier': AdaBoostClassifier,
               'RandomForestClassifier': RandomForestClassifier,
               'LogisticRegression': LogisticRegression,
               'DecisionTreeClassifier': DecisionTreeClassifier,
               'SVC': SVC,
               'DummyClassifier': DummyClassifier}


def parse_clfs(clf_json):
    try:
        with open('public/javascripts/parse_params/params.json') as json_spec_f:
            json_spec = json.load(json_spec_f)
        clf_json = json.loads(clf_json)
        args = []
        for clf_directive in clf_json:
            this_arg = {}
            clf_name = clf_directive[0]
            try:
                clf = clf_classes[clf_name]
            except KeyError:
                continue
            try:
                clf_spec = json_spec[clf_name]
            except KeyError:
                continue
            this_arg['clf'] = clf
            for param_directive in clf_directive[1]:
                param = param_directive[0]
                try:
                    param_spec = clf_spec[param]
                except KeyError:
                    continue
                settings = []
                for setting_directive in param_directive[1]:
                    if not isinstance(setting_directive, basestring): 
                        pass
                    elif setting_directive.upper() == 'NONE':
                        settings.append(None)
                    elif isinstance(param_spec, list):
                        if setting_directive in param_spec:
                            settings.append(setting_directive)
                    elif param_spec == 'Integer':
                        try:
                            settings.append(int(setting_directive))
                        except ValueError:
                            pass
                    elif param_spec == 'Float':
                        try:
                            settings.append(float(setting_directive))
                        except ValueError:
                            pass
                this_arg[param] = settings
            args.append(this_arg)
        print clf_json
        print args
        return args
    except Exception:
        return [{'clf': RandomForestClassifier}]
