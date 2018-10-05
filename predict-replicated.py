import pandas as pd
import numpy as np
import re
from multiprocessing import Pool
from gensim.models import KeyedVectors
from sklearn import svm, linear_model
from sklearn.metrics import make_scorer, roc_curve, precision_recall_curve
from sklearn.model_selection import cross_validate, RepeatedStratifiedKFold

vectors = '/mnt/sda1/wv/w2v.wiki50d.txt'

def V(w):
    try:
        return x[w]
    except KeyError:
        return None

x = KeyedVectors.load_word2vec_format(vectors)
# x = {'the': [1]}

data = pd.read_json('flat.json', orient='records')
# data['dois'] = docs['dois']

def read_paper(title):
    try:
        with open('txt-papers/' + title + '.pdf.txt', 'r') as f:
            return f.read()
    except IOError:
        return None

p = Pool()
data['text'] = p.map(read_paper, data['title'])
data['failed'] = data['result'].str.contains('2')
succeeded = data['result'].str.contains('1') # | data['result'].str.contains('4')
print(len(data))
data = data.loc[data['failed'] != succeeded].dropna(subset=['text', 'failed'])
data['words'] = data['text'].apply(lambda c: re.findall(r"\w+", c.lower(), re.UNICODE))
data['mean_vector'] = data['words'].apply(lambda ws: np.mean([V(word) for word in ws if not V(word) is None], axis=0))
data = data[data['mean_vector'].str.len() > 0]

curves = []
curves_i = -1

def roc_curve_as_score(y, y_pred, **kwargs):
    global curves, curves_i
    curves_i += 1
    curves.append(roc_curve(y, y_pred))
    # print(curves[curves_i][2])
    return curves_i

def pr_curve(y, y_pred, **kwargs):
    global curves, curves_i
    curves_i += 1
    curves.append(precision_recall_curve(y, y_pred))
    return curves_i

scoring = {s:s for s in ['f1', 'accuracy', 'precision', 'recall', 'roc_auc', 'average_precision']}
scoring['roc_curve'] = make_scorer(roc_curve_as_score, needs_threshold=True)
scoring['pr_curve'] = make_scorer(pr_curve, needs_threshold=True)

X = np.stack(data['mean_vector'].values)
y = data['failed'].values

model = svm.LinearSVC(class_weight='balanced')
model = linear_model.LogisticRegression(class_weight='balanced', C=1.)

scores = cross_validate(model, X, y, cv=RepeatedStratifiedKFold(n_splits=20), scoring=scoring)
print({k:np.mean(scores[k]) for k in scores if k.startswith('test_')})


# http://www.aclweb.org/anthology/Q15-1016


# print(data.groupby('title').filter(lambda x: len(x) > 1)[['title', 'result', 'questioned']].sort_values('title'))

print(len(data))

# print(data.iloc[0])
