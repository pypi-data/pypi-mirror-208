import numpy as np
import pandas as pd
import gc
import networkx as nx

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
#from sklearn.metrics.pairwise import cosine_similarity
from kolibri.data.text.quality.pairwise_cos_sim import cosine_similarity
from kdmt.sequences import chunk_generator
import datetime


def find_similar(tfidf_matrix, index, top_n=5):
    cosine_similarities = linear_kernel(tfidf_matrix[index:index + 1], tfidf_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != index]
    # related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] ]
    return [(index, cosine_similarities[index]) for index in related_docs_indices][0:top_n]


def findMisclassification(df, content_field, classField, id_col):
    start_time = datetime.datetime.now()
    # newCol ='Desp_NoSign_ShortDescription'
    newCol = content_field
    tfidf = TfidfVectorizer().fit_transform(df[newCol].values.astype('U'))
    similarList = []
    n = len(df[newCol])
    threshold = 0.95 #config.qualityControl['simiScore']
    count = 0
    for searchIndex in range(n):
        simiIndex = set()
        for index, score in find_similar(tfidf, searchIndex):
            if (score > threshold):
                if df.iloc[searchIndex][classField] != df.iloc[index][classField]:
                    simiIndex.add(df.iloc[index][id_col])
        if simiIndex:
            simiIndex.add(df.iloc[searchIndex][id_col])
            if simiIndex not in similarList:
                if similarList:
                    newSet = True
                    for itemSimi in simiIndex:
                        # for itemList in similarList:
                        for i in range(len(similarList)):
                            if itemSimi in similarList[i]:
                                similarList[i] = set(list(similarList[i]) + list(simiIndex))
                                newSet = False
                                break
                    # that mean simiIndex is new set
                    if newSet:
                        if not set(simiIndex) < set(similarListSet):
                            similarList.append((set(simiIndex)))
                else:
                    similarListSet = (tuple(x) for x in similarList)
                    if not set(simiIndex) < set(similarListSet):  # check subset of list
                        similarList.append(set(simiIndex))
        if (searchIndex % 1000 == 0 and searchIndex != 0):
            #logger.info('Compared %s data', (str)(searchIndex))
            print("Compared %s data", str(searchIndex))

        count = count + 1
    end_time = datetime.datetime.now()

    #logger.info('----Time to find miss classification {}----'.format(end_time - start_time))
    print('Time to find miss classiication {}----'.format(end_time - start_time))
    return similarList



def findMisclassification2(df, content_field, classField, id_field, threshold = 0.95,chunk_size=1000):
    start_time = datetime.datetime.now()
    tfidf = TfidfVectorizer().fit_transform(df[content_field].values.astype('U'))
    similarList = []
    n = len(df[content_field])
     #config.qualityControl['simiScore']
    count = 0
    G = nx.Graph()
    for chunk in chunk_generator(list(range(0, n)), chunk_size):

        if count==6:
            print(count)
        cosines=linear_kernel(tfidf[chunk], tfidf)
        similar_sub_list_=np.where(cosines>threshold)
#        similar_sub_list=[(df.iloc[s[0]+(count*chunk_size)]['source'], df.iloc[s[0]+(count*chunk_size)][id_field], df.iloc[s[0]+(count*chunk_size)][classField],df.iloc[s[0]+(count*chunk_size)][content_field], df.iloc[s[1]]['source'], df.iloc[s[1]][id_field], df.iloc[s[1]][classField], df.iloc[s[1]][content_field], df.iloc[s[1]]['lib1']) for s in zip(*similar_sub_list_) if s[0] != s[1] and df.iloc[s[0]+(count*chunk_size)][classField] !=df.iloc[s[1]][classField]]
        similar_sub_list=[(df.index[s[0]+(count*chunk_size)], df.index[s[1]]) for s in zip(*similar_sub_list_) if s[0] != s[1] and df.iloc[s[0]+(count*chunk_size)][classField] !=df.iloc[s[1]][classField]]
        count+=1
        similarList.extend(similar_sub_list)
        gc.collect()
#    similarList=np.where(cosines>threshold)
#    similarList=[(s[0], df.iloc[s[0]][classField], s[1], df.iloc[s[1]][classField]) for s in zip(*similarList) if s[0] != s[1] and df.iloc[s[0]][classField] !=df.iloc[s[1]][classField]]

    end_time = datetime.datetime.now()

    #logger.info('----Time to find miss classification {}----'.format(end_time - start_time))
    print('Time to find miss classiication {}----'.format(end_time - start_time))
    G.add_edges_from(similarList)
    return [g for g in nx.connected_components(G)]