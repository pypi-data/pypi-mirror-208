import numpy as np
from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.embeddings.embedding_tool import EmbeddingTool
import nltk
from nltk.corpus import stopwords

class Word2VecEmbedding:
    def __init__(self,tfidf_model_path, tfidf_dictionary_path, word2vec_embedding_path) -> None:
        self.__embedding_tool = EmbeddingTool()
        self.__tfidf_model = self.__embedding_tool.read_tfidf_model(tfidf_model_path)
        self.__tfidf_dictionary = self.__embedding_tool.read_gensim_dictionary(tfidf_dictionary_path)
        self.__word2vec_embedding = self.__embedding_tool.read_gensim_word2vec_embedding(word2vec_embedding_path)
        self.__current_logger = CommonTool().get_logger()
        # self.__english_word_set = CommonTool().read_stop_word_set('english')
        self.__english_word_set = set(stopwords.words('english'))
        nltk.download('stopwords')
    
    
    def calculate_embedding(self,document):
        # print(self.__tfidf_dictionary[text])
        result = dict()
        split_document = document.lower().split()
        word_idx_to_score_tuple_list = self.__tfidf_model[self.__tfidf_dictionary.doc2bow(split_document)]
        single_word_to_score = dict()
        for word_idx,score in word_idx_to_score_tuple_list:
            single_word_to_score[self.__tfidf_dictionary.get(word_idx)]  = score
        
        doc_embedding = None
        valid_word = 0
        for current_word in split_document:
            if current_word in single_word_to_score and current_word in self.__word2vec_embedding.key_to_index and current_word not in self.__english_word_set:
                # self.__current_logger.debug(f'{current_word}')
                current_word_score = single_word_to_score[current_word]
                current_vec = self.__word2vec_embedding[current_word]
                current_vec = current_vec * current_word_score  
                # self.__current_logger.debug(current_vec.shape)
                if doc_embedding is None:
                    doc_embedding =    np.zeros(current_vec.shape,dtype=np.float32)           
                doc_embedding = doc_embedding + current_vec
                valid_word = valid_word + 1
        if valid_word != 0:
            doc_embedding = doc_embedding / valid_word
            result["success"] = True
            result["vec"] = doc_embedding
        else:
            result["success"] = False
            result["fail_reason"] = "there is no valid word"
        
        return result