from kolibri.features.text.embedders.glove_embedder import GloVeEmbedder
from kolibri.features.text.embedders.fasttext_embedder import FasttextEmbedder

def get_embedder(embedder, configs):
    if embedder=="glove":
        return GloVeEmbedder(configs)
    elif embedder=="fasttext":
        return FasttextEmbedder(configs)

    return None