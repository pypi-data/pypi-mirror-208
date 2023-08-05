# encoding: utf-8



from typing import Dict, Any, Optional

from tensorflow import keras

from kolibri.backend.tensorflow.embeddings.base_embedding import BaseEmbedding

L = keras.layers


class DefaultEmbedding(BaseEmbedding):
    """
    DefaultEmbedding is a random init `tf.keras.layers.Embedding` layer for text sequence embedding,
    which is the defualt embedding class for kolibri models.
    """

    def __init__(self,
                 embedding_size: int = 100,
                 **kwargs: Any):
        """

        Args:
            embedding_size: Dimension of the dense embedding.
            kwargs: additional params
        """
        self.embedding_size: int = embedding_size
        super(DefaultEmbedding, self).__init__(embedding_size=embedding_size,
                                               **kwargs)

    def load_embed_vocab(self) -> Optional[Dict[str, int]]:
        return None

    def build_embedding_model(self,
                              *,
                              vocab_size: int = None,
                              force: bool = False,
                              **kwargs: Dict) -> None:
        if self.embed_model is None or force:
            input_tensor = L.Input(shape=(None,),
                                   name=f'input')
            layer_embedding = L.Embedding(vocab_size,
                                          self.embedding_size,
                                          mask_zero=True,
                                          name=f'layer_embedding')

            embedded_tensor = layer_embedding(input_tensor)
            self.embed_model = keras.Model(input_tensor, embedded_tensor)


if __name__ == "__main__":
    pass
