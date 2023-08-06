import numpy as np
from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.embeddings.embedding_tool import EmbeddingTool
import nltk
from nltk.corpus import stopwords
from rake_nltk import Rake


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

    def calculate_embedding_for_short_phrase_rake_nltk_keyword(self,weight,phrase):
        if isinstance(phrase,str) is False:
            raise ValueError("document is not str")
        if isinstance(weight,int) is False and isinstance(weight,float) is False:
            raise ValueError("weight is not int")
        if weight < 0:
            raise ValueError("weight should not be negative")
        # print(self.__tfidf_dictionary[text])
        split_document = phrase.lower().split()
        word_idx_to_score_tuple_list = self.__tfidf_model[self.__tfidf_dictionary.doc2bow(split_document)]
        single_word_to_score = dict()
        for word_idx,score in word_idx_to_score_tuple_list:
            single_word_to_score[self.__tfidf_dictionary.get(word_idx)]  = score
        phrase_embedding = None
        for current_word in split_document:
            if current_word in single_word_to_score and current_word in self.__word2vec_embedding.key_to_index and current_word not in self.__english_word_set:
                # self.__current_logger.debug(f'{current_word}')
                current_vec = self.__word2vec_embedding[current_word]
                # self.__current_logger.debug(current_vec.shape)
                if phrase_embedding is None:
                    phrase_embedding =    np.zeros(current_vec.shape,dtype=np.float32)           
                phrase_embedding =phrase_embedding + current_vec * weight
        return phrase_embedding
        
    
    def calculate_embedding_rake_nltk_keyword(self,document):
        # https://towardsdatascience.com/keyword-extraction-process-in-python-with-natural-language-processing-nlp-d769a9069d5c
        if isinstance(document,str) is False:
            raise ValueError("document is not str")
        result = dict()
        rake_tool = Rake()
        rake_tool.extract_keywords_from_text(document)
        list_phrases = rake_tool.get_ranked_phrases_with_scores() #[(16.0, 'advanced natural language processing'), (9.0, 'software company explosion')]
        if len(list_phrases) > 5:
            list_phrases = list_phrases[:5]
        doc_embedding = None
        for current_tuple in list_phrases:
            current_phrase_embedding = self.calculate_embedding_for_short_phrase_rake_nltk_keyword(current_tuple[0],current_tuple[1])
            if current_phrase_embedding is None:
                continue
            if doc_embedding is None:
                doc_embedding =    np.zeros(current_phrase_embedding.shape,dtype=np.float32)     
            doc_embedding = doc_embedding + current_phrase_embedding
        
        if doc_embedding is not  None:
            result["success"] = True
            result["vec"] = doc_embedding
        else:
            result["success"] = False
            result["fail_reason"] = "there is no valid doc phrase doc_embedding"
        
        return result
    