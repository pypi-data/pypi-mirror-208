import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from cosineSimilarity import findMisclassification2

###Load data

corpus =pd.read_excel("/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-ml/examples/Emails_parsed_new.xlsx")

corpus['forwarded']= corpus['subject'].str.startswith('FW:')
corpus.forwarded = corpus.forwarded.fillna(False)
corpus['selected']=0
corpus.loc[corpus.forwarded, 'selected']=1

corpus=corpus[corpus.fragment_id==corpus.selected]
cc = corpus#.sample(n=20000)

cc['content']=cc['subject'].astype(str) + ". "+cc['f_body'].astype(str)
cc=cc.reset_index()
misclassified = findMisclassification2(cc, 'content', 'target', 'id')

misclassified.to_excel('misclassified.xlsx')

