
import sklearn.preprocessing as pp


def cosine_similarity(mat):
    col_normed_mat = pp.normalize(mat.tocsc(), axis=1)
    return col_normed_mat * col_normed_mat.T
