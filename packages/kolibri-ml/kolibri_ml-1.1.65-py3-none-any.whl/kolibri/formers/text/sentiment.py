from kolibri.formers.text.classifier import TextClassiFormer



class SentimentFormer(TextClassiFormer):

    def __init__(self, output_folder, data, content, target):
        super().__init__(output_folder, data, content, target)