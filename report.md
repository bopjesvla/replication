---
title: |
    Automatically Finding and Categorizing Replication Studies \
    \vfill
    \large{Text and Multimedia Mining}\
    Radboud University Nijmegen\
    November, 2018
author:
    - Authored by Bob de Ruiter
abstract: |
    This work introduces the Mafiascum dataset,
    a collection of over 700 forum games
    where players were randomly assigned deceptive and non-deceptive roles.
    Parsable alignment distributions are available for the majority of the games,
    making the dataset suitable for training deception classifiers.

    Over 10,000 documents were compiled from the dataset, which each contained all messages
    written by a single player in a single game. This corpus was processed into multiple
    feature sets, including a set of hand-picked features based on deception theory
    and a set of average word embeddings enriched
    with subword information.

    An SVM trained on the combination of these two feature sets achieved an
    area under the precision-recall curve of 0.35 (compared to 0.26 by chance)
    and an ROC AUC of 0.64 (compared to 0.5 by chance) on large documents.
    \newpage
    \thispagestyle{empty}
    \mbox{}
    \newpage
header-includes:
    - \usepackage{float}
    - \usepackage{changepage}
    - \floatplacement{figure}{H}
---

## Introduction

Ever since 2010, when the replication crisis first entered public awareness, researchers have attempted to replicate, reproduce and reinvestigate results from various research fields, often with sobering results.
Perhaps best known is the Reproducibility Project, which failed to replicate 62 out of 97 psychology papers [@open2015estimating],
even though all original papers were widely-cited and published in esteemed journals. 
A large chunk of replication efforts, however, are not part of a centralized collaboration. Because of this, finding all replication studies for a given paper can prove to be difficult, be it automatically or manually.

If all replications of a given study could be automatically identified, citation databases and academic search engines such as Google Scholar could enrich the top-ranking papers with links to their replications, decreasing the chance that results that have already been called into question are taken at face value. If a system is developed that can automatically distinguish between failed, successful and partially successful replications, warnings for papers with failed replications could also be added.

Since replication studies typically cite the papers they aim to replicate, we can limit our search to papers that cite the given paper. For most papers, however, replication studies only make up a fraction of the citations: additional filtering is needed. One approach is to only query for documents that contain variants of the words "replication", "reproduction", "reanalysis" and "reinvestigation", but this may not even return half of the replication studies, as is shown in the section "Statistical Analysis".

Instead of a rule-based approach, we could train a supervised text classification model to identify replications. This, however, requires a labeled dataset. Fortunately, a website named the ReplicationWiki has a collection of structured data concerning XXX replication attempts spread over as many pages, which could be downloaded using a web scraper.

The ReplicationWiki also includes reproductions and reinvestigations in their "Replications" category, presumably because they are equally interesting to those evaluating the trustworthiness of a study. For the sake of brevity, the same broad definition of "replication" is used throughout this paper.

Replication pages specify whether the attempt was successful, although this field is missing for XX% of the studies. This information will be used to train a classification model to distinguish between failed and successful replication attempts. Taking this idea even further, I will attempt to create a model that predicts from a paper's text content whether it is likely to replicate.

## Methods

Replication metadata was scraped from the ReplicationWiki, including the title of the original paper, the title of the replication paper, whether the replication attempt was successful, whether different data was used for the replication, and whether new methods were used. The Crossref API was called to retrieve the DOI's of both the original papers and the replication studies. Using the DOI's, many of the papers could be downloaded directly. The other papers were downloaded manually. All papers were converted to text using the command-line tool `pdftotext`. Documents with less than 100 English words were discarded, leaving 334 replications and 344 original papers^[There are slightly more original papers than replications because some replication studies investigate multiple papers].

Fifty-dimensional word vectors trained on Wikipedia 2014 and Gigaword 5 were obtained from the [GloVe project page]. The low dimensionality was chosen because of the relatively small number of papers in the dataset. All words in all documents were mapped to their corresponding word vectors. Then, for each document, the average of all word vectors in that document was used as the document representation. Document-level hand-picked features were added on a per-task basis.

The model used in all tasks is a regularized logistic regression model (C = 1.0, balanced class weights).

### Task 1: Identifying Replications

Replication studies and replicated papers were annotated with positive and negative labels, respectively. For this task, the normalized frequencies of words starting with "replicat", "reproduc", "note", "comment", "reply", "re-" and "reinvestigat" were independently added as features. Additionally, both the average word vectors and the hand-picked features were recomputed for the paper titles rather than the full text, and this second feature matrix was concatenated to the first one. A logistic regression model was trained and tested on a stratified 40-fold split of the data.

### Task 2: Categorizing Replications

Replication studies were annotated with a label denoting whether the study failed. Partially successful and ambiguous replications were discarded, as were replications where data about the outcome was missing, leaving 150 replications, of which 49 were successful. A logistic regression model was trained and tested on a stratified 20-fold split of the data.

### Task 3: Predicting Replicability

All original papers were annotated with a label denoting whether its replications failed. Papers with mixed or partially successful replications were discarded, as were original papers where all replication results were missing, leaving 178 original papers, of which 68 were successfully replicated. A logistic regression model was trained and tested on a stratified 20-fold split of the data.

## Results

![ROC curves for all tasks](rocs.png){#pr}
![Precision-recall curves for all tasks](pr.png){#pr}

### Task 1: Identifying Replications

## Discussion



Although replicated papers may not be entirely similar to the set of papers that cite replicated papers, this task at the very least showed that replication studies are distinguishable from other papers.


[GloVe project page]: https://nlp.stanford.edu/projects/glove/

## Bibliography
