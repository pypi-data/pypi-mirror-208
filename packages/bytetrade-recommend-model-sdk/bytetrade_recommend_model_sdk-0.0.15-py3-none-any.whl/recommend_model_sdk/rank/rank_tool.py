import faiss
import numpy as np
from datetime import datetime
from recommend_model_sdk.rank.time_weight_decay_tool import TimeWeightDecayTool
from recommend_model_sdk.tools.common_tool import CommonTool


class RankTool:
    def __init__(self,base_document_id_to_embedding) -> None:
        """_summary_

        Args:
            base_document_id_to_embedding (_type_): _description_
            {
                "document_id":{
                    "embedding":[],numpy
                    "created_at": datetime
                }
            }

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        if isinstance(base_document_id_to_embedding,dict) is False:
            raise ValueError("base_document_id_to_embedding is not dict")
        if len(base_document_id_to_embedding) < 1:
            raise ValueError('base_document_id_to_embedding length small than 1')
        set_shape = set()
        list_current_embedding = list()
        self.__base_length = len(base_document_id_to_embedding)
        self.__base_index_to_document_id = dict()
        self.__base_document_id_to_index = dict()
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        current_index = 0
        self.__base_document_id_to_created_at_tuple_list = list()
        for current_document_id, current_embedding_info in base_document_id_to_embedding.items():
            if isinstance(current_document_id,str) is False:
                raise ValueError(f"current_document_id {current_document_id} is not str")
            if isinstance(current_embedding_info,dict) is False:
                raise ValueError("current_embedding_info is not dict")
            if "embedding" not in current_embedding_info:
                raise ValueError("embedding not in current_embedding_info")
            current_embedding = current_embedding_info["embedding"]
            # if isinstance(current_embedding,np.array)
            if isinstance(current_embedding,np.ndarray) is False:
                raise ValueError('there is embedding is not np.ndarray')
            if current_embedding.dtype != np.float32:
                raise ValueError("embedding_value is not float32")
            if "created_at" not in current_embedding_info:
                raise ValueError("created_at not in current_embedding_info")
            created_at = current_embedding_info["created_at"]
            if isinstance(created_at,datetime) is False:
                raise ValueError("created_at is not datetime")
            self.__base_document_id_to_created_at_tuple_list.append((current_document_id,created_at))
            
            set_shape.add(current_embedding.shape)
            list_current_embedding.append(current_embedding)
            self.__base_index_to_document_id[current_index] = current_document_id
            self.__base_document_id_to_index[current_document_id] = current_index
            
            current_index = current_index + 1
        self.__base_document_id_to_created_at_tuple_list.sort(key=lambda tup: tup[1],reverse=True)
        self.__logger.debug(self.__base_document_id_to_created_at_tuple_list)
        if len(set_shape) > 1:
            raise ValueError(f'have different shape embeddings')
        self.__embedding_shape = set_shape.pop()
        self.__original_base_embedding = np.stack(list_current_embedding)
        self.__normalized_base_embedding = np.copy(self.__original_base_embedding)
        faiss.normalize_L2(self.__normalized_base_embedding)
        # self.__original_base_embedding_index =  faiss.IndexFlatL2(self.__original_base_embedding)
        self.__cosin_index = faiss.index_factory(self.__embedding_shape[0], "Flat", faiss.METRIC_INNER_PRODUCT)
        self.__cosin_index.add(self.__normalized_base_embedding)
        self.__time_weight_decay_tool = TimeWeightDecayTool()
    
    def get_latest_article(self,rank_limit=100):
        
        pass
    
    def rank(self,document_id_to_document_info,rank_limit = 100):
        # https://github.com/facebookresearch/faiss/issues/396
        # 
        """_summary_
        {
            "document_id":{
                "embedding":[] numpy
                "last_reviewed":datetime
            }
        }
        [0-50]
        Args:
            document_id_to_document_info (_type_): _description_
        """
        query_document_length = len(document_id_to_document_info)
        self.__logger.debug(f'query_document_length {query_document_length}')
        if rank_limit > self.__base_length:
            raise ValueError("rank_limit is bigger than base length")
        full_weight = 50

        if len(document_id_to_document_info) == 0:
            current_tuple_list = self.__base_document_id_to_created_at_tuple_list[:rank_limit]
            document_id_to_weight_tuple_list = list()
            for current_document_id, current_created_at in current_tuple_list:
                document_id_to_weight_tuple_list.append((current_document_id,self.__time_weight_decay_tool.compute(full_weight,current_created_at,datetime.now())))
            return document_id_to_weight_tuple_list
            
        search_k = 3
        while(query_document_length*search_k < 2 * rank_limit):
            search_k = search_k + 1
        self.__logger.debug(f"search_k {search_k}")
        # previous review weight
        
        # currently weight
        query_index_to_query_document_id = dict()
        query_document_id_to_query_index = dict()
        query_index = 0
        list_query_embedding = list()
        query_document_id_to_weight = dict()
        query_index_to_weight = dict()
        current_time = datetime.now()
        for current_document_id, current_embedding_info in document_id_to_document_info.items():
            if isinstance(current_document_id,str) is False:
                raise ValueError("current_document_id is not str")
            if isinstance(current_embedding_info,dict) is False:
                raise ValueError('current_embedding_info is not dict')
            if "embedding" not in current_embedding_info:
                raise ValueError("embedding not in current_embedding_info")
            current_embedding = current_embedding_info["embedding"]
            if isinstance(current_embedding,np.ndarray) is False:
                raise ValueError('there is embedding is not np.ndarray')
            if current_embedding.dtype != np.float32:
                raise ValueError("embedding_value is not float32")
            if current_embedding.shape != self.__embedding_shape:
                raise ValueError("embedding shape is not equal to shape in base embedding")
            current_last_reviewed_time = current_embedding_info['last_reviewed']
            current_time_weight = self.__time_weight_decay_tool.compute(full_weight,current_last_reviewed_time,current_time)
            query_document_id_to_weight[current_document_id] = current_time_weight
            query_index_to_weight[query_index] = current_time_weight
            list_query_embedding.append(current_embedding)
            query_document_id_to_query_index[current_document_id] = query_index 
            query_index_to_query_document_id[query_index] = current_document_id
            query_index = query_index + 1
            
        
        stack_query_embedding = np.stack(list_query_embedding)
        faiss.normalize_L2(stack_query_embedding)
        
        
        while(True):
            distances, nearest_indexes = self.__cosin_index.search(stack_query_embedding, search_k) #[[]] [[]]
            article_index_weight_tuple_list = list() # tuple first_element weight, second_element_index
            for current_query_index in range(query_index):
                # repeat article
                current_distance_list = distances[current_query_index]
                current_nearest_index_list = nearest_indexes[current_query_index]
                for current_distance,current_neares_index in zip(current_distance_list,current_nearest_index_list):
                    article_index_weight_tuple_list.append((full_weight * current_distance + query_index_to_weight[current_query_index],current_neares_index))
            
            article_index_weight_tuple_list.sort(key=lambda tup: tup[0],reverse=True)
            
            exist_article_index_set = set()
            new_article_index_weight_list = list()
            
            for current_index_weight_tuple in article_index_weight_tuple_list:
                if current_index_weight_tuple[1] in exist_article_index_set:
                    continue
                new_article_index_weight_list.append(current_index_weight_tuple)
                exist_article_index_set.add(current_index_weight_tuple[1])
            if len(new_article_index_weight_list) >= rank_limit:
                break
            search_k = 2*search_k
            self.__logger.debug(f"search_k {search_k}")
        
        
        document_id_to_weight_tuple_list = list()
        for current_weight,current_base_article_index in article_index_weight_tuple_list:
            document_id_to_weight_tuple_list.append((self.__base_index_to_document_id[current_base_article_index],current_weight))

        
        return document_id_to_weight_tuple_list
            