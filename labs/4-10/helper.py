## -*- coding: utf-8 -*-

from gensim import models
import numpy as np


def show_topics(model):
    """Shows topic number and corresponding feature names to be used with a gensim model."""
    assert type(model) is models.LdaModel, "Not Gensim LDA instance."
    for i in model.show_topics():
        print('Topic ' + str(i[0]))
        print(i[1])
        print()

def topic_words(model, feature_names, n_top_words):
    """
    Display n_top_words number of words for a model
    and its corresponding feature_names.
    """
    for num_topic, topic in enumerate(model.components_):
        words = np.argsort(topic)[::-1][:n_top_words]
        print('Topic ' + str(num_topic) + ':')
        print(' '.join([feature_names[i] for i in words]))
