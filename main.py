## Init

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import re
from multiprocessing import Pool
from gensim.models import KeyedVectors
from sklearn import svm, linear_model, feature_extraction, feature_selection
from sklearn.metrics import make_scorer, roc_curve, precision_recall_curve, average_precision_score, accuracy_score
from sklearn.model_selection import cross_validate, RepeatedStratifiedKFold, StratifiedKFold

vectors = '/mnt/sda1/wv/w2v.wiki50d.txt'
x = KeyedVectors.load_word2vec_format(vectors)

## Config

TASK = 'identify'
TASK = 'predict'
TASK = 'categorize'

## Preprocessing

def read_paper(title):
    try:
        with open('txt-papers/' + title + '.pdf.txt', 'r') as f:
            return f.read()
    except IOError:
        return None

p = Pool()
papers = pd.read_json('flat.json', orient='records')
replications = pd.DataFrame(list(papers['replication']))

if TASK == 'identify':
    # papers['dois'] = docs['dois']

    replications['replication'] = True
    papers['replication'] = False
    data = pd.concat((replications[['title', 'replication']], papers[['title', 'replication']]))
    data = data.drop_duplicates(subset='title', keep='first')
else:
    data = replications if TASK == 'categorize' else papers
    data['failed'] = papers['result'].str.contains('2')
    succeeded = papers['result'].str.contains('1') # | data['result'].str.contains('4')
    data = data.loc[data['failed'] != succeeded].dropna(subset=['failed'])
    # drop mixed results
    data.groupby('title').filter(lambda x: x['failed'].all() or not x['failed'].any())
    data.drop_duplicates(subset='title', keep='first')

data['text'] = p.map(read_paper, data['title'].str.replace('/', '_'))
data = data.dropna(subset=['text'])
data['words'] = data['text'].apply(lambda c: re.findall(r"\w+", c.lower(), re.UNICODE))
data['wc'] = data['words'].str.len()

data['repl'] = data['text'].str.count(r'\breplicat', re.I) / data['wc']
data['repr'] = data['text'].str.count(r'\breproduc', re.I) / data['wc']
data['re'] = data['text'].str.count(r'\bre\b', re.I) / data['wc'] - data['repl']
data['comment'] = data['text'].str.count(r'\bcomment', re.I) / data['wc']
data['note'] = data['text'].str.count(r'\bnote', re.I) / data['wc']
data['article'] = data['text'].str.count(r'\barticle', re.I) / data['wc']
data['correspondence'] = data['text'].str.count(r'\bcorrespondence', re.I) / data['wc']
data['doi'] = data['text'].str.count(r'\bdoi', re.I) / data['wc']
data['original'] = data['text'].str.count(r'\boriginal', re.I) / data['wc']
data['results'] = data['text'].str.count(r'\bresults\b', re.I) / data['wc']
data['references'] = data['text'].str.count(r'\b\)', re.I) / data['wc']
data['title_repl'] = data['title'].str.count(r'\breplicat', re.I) / data['wc']
data['title_repr'] = data['title'].str.count(r'\breproduc', re.I) / data['wc']
data['title_re'] = data['title'].str.count(r'\bre\b', re.I) / data['wc'] - data['repl']
data['title_comment'] = data['title'].str.count(r'\bcomment', re.I) / data['wc']
data['title_note'] = data['title'].str.count(r'\bnote', re.I) / data['wc']

data['failcount'] = data['text'].str.count(r'\bfail', re.I) / data['wc']

def V(w):
    try:
        return x[w]
    except KeyError:
        return None

def mean_vector(ws, min_len=100):
    vectors = [V(word) for word in ws if not V(word) is None]
    if len(vectors) > min_len:
        return np.mean(vectors, axis=0)

# tfidf_model = feature_extraction.text.TfidfVectorizer(min_df=10)
# tfidf = tfidf_model.fit_transform(data['text'].values)
# select = feature_selection.SelectKBest(k=20)
# best = select.fit(tfidf, data['replication'].values).get_support()
# best_features = np.array(tfidf_model.get_feature_names())[best]
# best_scores = select.scores_[best]
# print([f for _, f in sorted(zip(best_scores, best_features))])

data['mean_vector'] = data['words'].apply(mean_vector)
data['title_mean_vector'] = data['title'].apply(mean_vector, args=(10,))
data = data.dropna(subset=['mean_vector', 'title_mean_vector'])

data = data[(data['mean_vector'].str.len() > 0) & (data['title_mean_vector'].str.len() > 0)]

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

if TASK == 'identify':
    hp_columns = 're comment note title_repl title_repr title_re title_comment title_note repr repl'.split()
else:
    hp_columns = ''.split()

hand_picked = data[hp_columns]
hand_picked -= hand_picked.mean()
hand_picked /= hand_picked.std()

if TASK == 'identify':
    X = np.concatenate((np.stack(data['mean_vector'].values), np.stack(data['title_mean_vector'].values), hand_picked), axis=1)
    y = data['replication'].values
else:
    X = np.concatenate((np.stack(data['mean_vector'].values), hand_picked), axis=1)
    y = data['failed'].values

## Evaluation

model = svm.LinearSVC(class_weight='balanced')

from autosklearn.classification import AutoSklearnClassifier
import autosklearn
from tpot import TPOTClassifier

y_true=[]
y_pred=[]
for train, test in RepeatedStratifiedKFold(n_splits=20).split(X, y):
    model = linear_model.LogisticRegression(class_weight='balanced', C=1.)
    # model = AutoSklearnClassifier(
    #     time_left_for_this_task=360, per_run_time_limit=5,
    #     resampling_strategy=StratifiedKFold,
    #     resampling_strategy_arguments={'n_splits': 5},
    #     ensemble_size=1)
    # model = TPOTClassifier(generations=10, population_size=10, scoring='average_precision', verbosity=2)
    # model = linear_model.LogisticRegression(class_weight='balanced', C=1.)
    # model.fit(X[train], y[train], metric=autosklearn.metrics.average_precision)
    # model.refit(X[train], y[train])
    model.fit(X[train], y[train])
    y_true += list(y[test])
    y_pred += list(model.predict_proba(X[test])[:,1])
score = average_precision_score(y_true, y_pred)
print(score)

fpr, tpr, _ = roc_curve(y_true, y_pred)
plt.figure()
plt.plot(fpr, tpr, label='ROC curve')
plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=.8)
plt.legend()
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.xlim([0,1])
plt.ylim([0,1])
plt.savefig('roc_'+TASK)

# http://www.aclweb.org/anthology/Q15-1016

plt.figure()
prec, rec, _ = precision_recall_curve(y_true, y_pred)
plt.plot(rec, prec, alpha=.8, label='PR curve')
plt.plot([0, 1], [sum(y)/len(y), sum(y)/len(y)], linestyle='--', lw=2, color='r', label='Chance', alpha=.8)
plt.legend()
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.xlim([0,1])
plt.ylim([0,1])
plt.savefig('pr_'+TASK)
# print(data.groupby('title').filter(lambda x: len(x) > 1)[['title', 'result', 'questioned']].sort_values('title'))

print(len(papers))

# print(papers.iloc[0])
