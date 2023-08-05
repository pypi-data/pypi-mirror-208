from gensim import corpora

import gensim
import os
class EmbeddingTool:
    def __init__(self) -> None:
        pass
    
    def read_tfidf_model(self, tfidf_file):
        if os.path.exists(tfidf_file) is False:
            raise ValueError(f"{tfidf_file} is not exist")
        tfidf = gensim.models.TfidfModel.load(tfidf_file)
        return tfidf
    
    def read_gensim_dictionary(self,path):
        if os.path.exists(path) is False:
            raise ValueError(f"path {path} is not exist")
        current_dict = corpora.Dictionary().load(path)
        return current_dict
    
    def read_gensim_word2vec_embedding(self,path):
        if os.path.exists(path) is False:
            raise ValueError(f'path {path} is not exist')
        current_model = gensim.models.keyedvectors.load_word2vec_format(path, binary=True)
        return current_model
    
    


