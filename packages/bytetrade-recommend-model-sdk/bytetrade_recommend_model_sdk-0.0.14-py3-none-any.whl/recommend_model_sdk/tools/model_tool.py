import base64
from datetime import datetime
import os
from google.protobuf.json_format import Parse, ParseDict,MessageToDict
import nltk
import zlib

from recommend_model_sdk.tools.aws_s3_tool import AWSS3Tool
from recommend_model_sdk.tools.common_tool import CommonTool
from recommend_model_sdk.embeddings.word2vec_embedding import Word2VecEmbedding
import recommend_model_sdk.proto_class.embedding_pb2 as rec_proto_embebding

class ModelTool:
    def __init__(self,model_root_dir) -> None:
        if isinstance(model_root_dir,str) is False:
            raise ValueError("model_root_dir is not str")
        if os.path.exists(model_root_dir) is False:
            raise ValueError("model_root_dir is not exist")
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
        self.__model_management_file = os.path.join(os.path.join(self.__common_tool.get_project_directory(),"resources"),"model_management.json")
        self.__logger.debug(self.__model_management_file)

        self.__model_related_files_suffix_set = set(["gz","direct"])
        self.__model_dict = self.__validate_model_management_file(self.__model_management_file)
        self.__awss3tool = AWSS3Tool()
        self.__model_name_to_infer_method = dict()
        self.__model_name_to_infer_method["word2vec_google"] = self.word2vec_calculate_embedding
        self.__model_root_dir = model_root_dir
        self.__latest_support_package_number = set([1000,5000,10000])

    
    def get_valid_model_and_version(self):
        model_name_to_valid_version_list = dict()
        for current_model_name, current_model_version_dict in self.__model_dict.items():
            for current_version_name,current_model_detail in current_model_version_dict.items():
                if current_model_detail["active"]:
                    if current_model_name not in model_name_to_valid_version_list:
                        model_name_to_valid_version_list[current_model_name] = list()
                    model_name_to_valid_version_list[current_model_name].append(current_version_name)
        return model_name_to_valid_version_list
                
        
    def __validate_model_key_field(self,current_model_detail):
        '''
        v1":{
            "mongodb_embedding_field":"word2vec_google_v1",
            "pg_embedding_mark_field":"word2vec_google_embedding",
            "s3_bucket":"gpu-model-data",
            "model_related_files":["GoogleNews-vectors-negative300.bin","tfidf.model","dictionary"]
        }
        '''
        if isinstance(current_model_detail,dict) is False:
            raise ValueError('mongodb_embedding_field is not dict')
        if "mongodb_embedding_field" not in current_model_detail:
            raise ValueError("mongodb_embedding_field is not exist")
        mongodb_embedding_field = current_model_detail["mongodb_embedding_field"]
        if isinstance(mongodb_embedding_field,str) is False:
            raise ValueError("mongodb_embedding_field is not exist")
        
        if "pg_embedding_mark_field" not in current_model_detail:
            raise ValueError("pg_embedding_mark_field is not exist")
        pg_embedding_mark_field = current_model_detail["pg_embedding_mark_field"]
        if isinstance(pg_embedding_mark_field,str) is False:
            raise ValueError("pg_embedding_mark_field is not str")
        
        if "s3_bucket" not in current_model_detail:
            raise ValueError("s3_bucket not in")
        s3_bucket = current_model_detail["s3_bucket"]
        if isinstance(s3_bucket,str) is False:
            raise ValueError("s3_bucket is not str")
        
        if "model_related_files" not in  current_model_detail:
            raise ValueError("model_related_files is not exist")
        model_related_files = current_model_detail["model_related_files"]
        if isinstance(model_related_files,list) is False:
            raise ValueError("model_related_files not exist")
        for current_file in model_related_files:
            if isinstance(current_file,str) is False:
                raise ValueError("current_file is not exist")
        
        if "model_related_files_suffix" not in current_model_detail:
            raise ValueError("model_related_files_suffix not in current_model_detail")
        model_related_files_suffix = current_model_detail["model_related_files_suffix"]
        if isinstance(model_related_files_suffix,dict) is False:
            raise ValueError("model_related_files_suffix is not dict")
        for current_file_name in model_related_files:
            if current_file_name not in model_related_files_suffix:
                raise ValueError(f'current_file_name {current_file_name} have no suffix')
            
            current_file_name_suffix = model_related_files_suffix[current_file_name]
            if current_file_name_suffix not in self.__model_related_files_suffix_set:
                raise ValueError(f"current_file_name_suffix {current_file_name_suffix} is not valid")
        
        if "model_related_files_public" not in current_model_detail:
            raise ValueError("model_related_files_public is not exist")
        model_related_files_public = current_model_detail["model_related_files_public"]
        for current_file_name in model_related_files:
            if current_file_name not in model_related_files_public:
                raise ValueError(f"current_file_name {current_file_name} not in model_related_files_public")
            current_file_name_public = model_related_files_public[current_file_name]
            if isinstance(current_file_name_public,bool) is False:
                raise ValueError(F"current_file_name {current_file_name} current_file_name_public is  not bool")
        
        
    def __validate_model_management_file(self,path):
        if isinstance(path,str) is False:
            raise ValueError(f"path {path} is not str")
        if os.path.exists(path) is False:
            raise ValueError(f"model management file {path} is not exist")
        model_management_dict = self.__common_tool.read_json(path)
        model_name_set = model_management_dict.keys()
        
        
        mongodb_embedding_field_set =  set()
        pg_embedding_mark_field_set = set()
        for current_model_name in model_name_set:
            if len(model_management_dict[current_model_name]) < 1:
                raise ValueError(f'current_model {current_model_name} have not valid model')
            for version_name,current_model_detail in model_management_dict[current_model_name].items():
                self.__validate_model_key_field(current_model_detail)
                mongodb_embedding_field = current_model_detail["mongodb_embedding_field"]
                pg_embedding_mark_field = current_model_detail["pg_embedding_mark_field"]
                if mongodb_embedding_field in mongodb_embedding_field_set:
                    raise ValueError(f"mongodb_embedding_field {mongodb_embedding_field} exist more than two model version")
                else:
                    mongodb_embedding_field_set.add(mongodb_embedding_field)
                if pg_embedding_mark_field in pg_embedding_mark_field_set:
                    raise ValueError(f"pg_embedding_mark_field {pg_embedding_mark_field} exist more than  model version")
                else:
                    pg_embedding_mark_field_set.add(pg_embedding_mark_field)
        return model_management_dict
    
    
    def valid_model_name_and_version(self,model_name,model_version):
        if isinstance(model_name,str) is False:
            raise ValueError("model name need to be str")
        if isinstance(model_version,str) is False:
            raise ValueError("model_version need to be str")
        
        if model_name not in self.__model_dict:
            return False
        
        if model_version not in self.__model_dict[model_name]:
            return False
        
        return self.__model_dict[model_name][model_version]
    
    def word2vec_calculate_embedding(self,model_name,model_version,dict_document):
        self.valid_model_name_and_version(model_name,model_version)
        self.valid_infer_document(dict_document)
        if model_name != "word2vec_google":
            raise ValueError("model name is not word2vec_google")
        current_model_dir = os.path.join(os.path.join(self.__model_root_dir,model_name),model_version)
        current_common_dir = os.path.join(self.__model_root_dir,"common")
        
        tfidf_path = os.path.join(current_model_dir,"tfidf.model")
        google_word2vec_path = os.path.join(current_common_dir,"GoogleNews-vectors-negative300.bin")
        dictionary_path = os.path.join(current_model_dir,"dictionary")
        
        word2vect_tool = Word2VecEmbedding(tfidf_path,dictionary_path,google_word2vec_path)
        id_to_infer_result = dict()
        for current_id, current_text in dict_document.items():
            id_to_infer_result[current_id] = word2vect_tool.calculate_embedding(current_text)
            
        return id_to_infer_result
        
    def valid_infer_document(self,dict_documents):
        if isinstance(dict_documents,dict) is False:
            raise ValueError("dict_documents is not dict")
        for current_id,current_text in dict_documents.items():
            if isinstance(current_id,str) is False:
                raise ValueError("current_id is not str")
            if isinstance(current_text,str) is False:
                raise ValueError("current_text is not str")
            
    def infer(self,model_name,model_version,dict_documents):
        """_summary_

        Args:
            model_name (_type_): _description_
            model_version (_type_): _description_
            list_document (_type_): _description_ {
                "id":"",
                "text:""
            }

        Raises:
            ValueError: _description_
            ValueError: _description_
        Returns:
           {
               "success":true or false
               "vec": when success
               "fail_reason": when fail str
           }
        """
        self.valid_model_name_and_version(model_name,model_version) 
        self.valid_infer_document(dict_documents)
        return self.__model_name_to_infer_method[model_name](model_name,model_version,dict_documents)
                      
    
    def get_latest_article_embedding_package_support_number(self):
        """_summary_
        """
        return self.__latest_support_package_number
    
    def download_latest_all_feed(self):
        """_summary_

        Raises:
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
            {
                feedid:{
                    "id": int
                    "feed_url":string
                    "site_url":string
                    "title":string
                    "category_id":int
                    "category_title":string
                    "icon_id":int    may missing
                    "icon_type":string may missing
                    "icon_content":bytes may missing
                }
            }
        """
        feed_field_set = set(['id', 'feed_url', 'site_url', 'title', 'category_id', 'category_title', 'icon_id', 'icon_type', 'icon_content'])
        latest_package_key = 'all_feeds'
        common_dir = os.path.join(self.__model_root_dir,'common')
        if os.path.exists(common_dir) is False or os.path.isdir(common_dir) is False:
            os.makedirs(common_dir)
        current_feed_path = os.path.join(common_dir,latest_package_key)
        current_bucket_name = 'gpu-model-data'
                           
        need_redownload = False
        if os.path.exists(latest_package_key) is False:
            self.__logger.debug(f'current_all_feeds_path {current_feed_path}  not exist')
            need_redownload = True
        else:
            exist_protobuf_compress_hash = self.__common_tool.calculate_md5_for_big_file(current_feed_path)
            self.__logger.debug(f'current_feed_path {current_feed_path} does  exist ,exist file hash {exist_protobuf_compress_hash}')
            response_header = self.__awss3tool.get_object_header(current_bucket_name, latest_package_key)
            if ("ResponseMetadata" not in response_header or 
                "HTTPStatusCode" not in response_header["ResponseMetadata"] or
                response_header["ResponseMetadata"]["HTTPStatusCode"] != 200):
                raise ValueError(f'current_bucket { current_bucket_name} key {latest_package_key} not exist')
            if response_header["Metadata"]["md5_digest"] != exist_protobuf_compress_hash:
                need_redownload = True
                
        if need_redownload:
            result = self.__awss3tool.get_object_byte(current_bucket_name,latest_package_key)
            if result["success"] is False:
                raise ValueError(f"download embedding package fail result {result}")
            current_package_compress_byte = result["bytes"]
            with open(current_feed_path,'wb') as f:
                f.write(current_package_compress_byte)
            self.__logger.debug(f'need_download {current_feed_path}')
        else:
            with open(current_feed_path,'rb') as f:
                current_package_compress_byte = f.read()
        
        decompress_bytes = zlib.decompress(current_package_compress_byte)
        current_latest_package = rec_proto_embebding.FeedPackage()
        current_latest_package.ParseFromString(decompress_bytes)
        
        all_feeds_dict = MessageToDict(current_latest_package,preserving_proto_field_name=True)
        all_feeds_list = all_feeds_dict["feeds"]
        all_feed_id_to_feed = dict()
        for current_feed in all_feeds_list:
            current_feed['id'] = int(current_feed['id'])
            if 'icon_id' in current_feed:
                current_feed['icon_id'] = int(current_feed['icon_id'])
            if 'category_id' in current_feed:
                current_feed['category_id'] = int(current_feed['category_id'])
            if 'icon_content' in current_feed:
                current_feed['icon_content'] = base64.b64decode(current_feed['icon_content'])
            for current_field in feed_field_set:
                if current_field not in current_feed:
                    current_feed[current_field] = None
            all_feed_id_to_feed[current_feed['id']] = current_feed
                
        return all_feed_id_to_feed
        

    
    def download_latest_article_embedding_package(self,model_name,model_version,latest_number,publish_time=None):
        """_summary_

        Args:
            model_name (_type_): _description_
            model_version (_type_): _description_
            latest_number (_type_): _description_
            start_time (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
            url_to_article_dict 
            {
                "http...":{
                    "url":
                    "full_text":
                    "created_at":
                    "published_at":
                    "title":
                    "author":  may not exist
                    "content":  may not exist
                    "feed_id":
                }
                "http...":{
                    
                }
            }
            
            url_to_embedding
            {
                "https://":{
                    "url":
                    "model_name":
                    "model_version":
                    "embeddings":[] list float
                }
            }
        """
        article_field_set = set(['url', 'full_text', 'created_at', 'published_at', 'title', 'author', 'content', 'feed_id', 'hash'])
        
        self.valid_model_name_and_version(model_name,model_version)
        if publish_time is not None and isinstance(publish_time,datetime) is False:
            raise ValueError('start_time is not datetime type')
        if isinstance(latest_number,int) is False:
            raise ValueError("latest_number is not int")
        if latest_number not in self.__latest_support_package_number:
            raise ValueError("latest_number is not support")
        latest_package_key = f'{model_name}_{model_version}_latest_package_{latest_number}'
        model_version_embedding_dir = os.path.join(os.path.join(os.path.join(self.__model_root_dir,model_name),model_version),'embedding')
        if os.path.exists(model_version_embedding_dir) is False or os.path.isdir(model_version_embedding_dir) is False:
            os.makedirs(model_version_embedding_dir)
        current_embedding_path = os.path.join(model_version_embedding_dir,latest_package_key)
                        
        current_model_detail = self.__model_dict[model_name][model_version]
        current_bucket_name = current_model_detail['s3_bucket']
        
        need_redownload = False
        if os.path.exists(current_embedding_path) is False:
            self.__logger.debug(f'current_embedding_path {current_embedding_path}  not exist')
            need_redownload = True
        else:
            exist_protobuf_compress_hash = self.__common_tool.calculate_md5_for_big_file(current_embedding_path)
            self.__logger.debug(f'current_embedding_path {current_embedding_path} does  exist ,exist file hash {exist_protobuf_compress_hash}')
            response_header = self.__awss3tool.get_object_header(current_bucket_name, latest_package_key)
            if ("ResponseMetadata" not in response_header or 
                "HTTPStatusCode" not in response_header["ResponseMetadata"] or
                response_header["ResponseMetadata"]["HTTPStatusCode"] != 200):
                raise ValueError(f'current_bucket { current_bucket_name} key {latest_package_key} not exist')
            if response_header["Metadata"]["md5_digest"] != exist_protobuf_compress_hash:
                need_redownload = True
                
        if need_redownload:
            result = self.__awss3tool.get_object_byte(current_bucket_name,latest_package_key)
            if result["success"] is False:
                raise ValueError(f"download embedding package fail result {result}")
            current_package_compress_byte = result["bytes"]
            with open(current_embedding_path,'wb') as f:
                f.write(current_package_compress_byte)
            self.__logger.debug(f'need_download {current_embedding_path}')
        else:
            with open(current_embedding_path,'rb') as f:
                current_package_compress_byte = f.read()
        
        decompress_bytes = zlib.decompress(current_package_compress_byte)
        current_latest_package = rec_proto_embebding.LatestPackage()
        current_latest_package.ParseFromString(decompress_bytes)
        
        article_embedding_dict = MessageToDict(current_latest_package,preserving_proto_field_name=True)
        article_list = article_embedding_dict["articles"]
        embedding_list = article_embedding_dict["embeddings"]
        url_to_article_dict = dict()
        url_to_embedding_dict = dict()
        for current_article in article_list:
            current_article['published_at'] = int(current_article['published_at'])
            current_article['created_at'] = int(current_article['created_at'])
            for current_field in article_field_set:
                if current_field not in current_article:
                    current_article[current_field] = None
                
            url_to_article_dict[current_article["url"]] = current_article
            
        for current_embedding in embedding_list:
            url_to_embedding_dict[current_embedding["url"]] = current_embedding    
        
        
        if publish_time is not None: 
            start_time_timestamp = int(round(publish_time.timestamp() * 1000))       
            filter_url_to_article_dict = dict()
            filter_url_to_embedding_dict = dict()
            for current_url,current_article in url_to_article_dict.items():

                if current_article['published_at'] > start_time_timestamp:
                    filter_url_to_article_dict[current_url] = current_article
                    filter_url_to_embedding_dict[current_url] = url_to_embedding_dict[current_url]
            return filter_url_to_article_dict,filter_url_to_embedding_dict
        else:
            return url_to_article_dict,url_to_embedding_dict
        
            
            
            
                
        
        
    
    def init_model(self,model_name,model_version):
        nltk.download('stopwords')
        return self.download(model_name,model_version,self.__model_root_dir)
        
    def download(self,model_name,model_version,directory):
        if isinstance(directory,str) is False:
            raise ValueError("directory is not str")
        if os.path.exists(directory) is False:
            raise ValueError(f"directory{directory} is not exist")
        
        model_version_directory = os.path.join(os.path.join(directory,model_name),model_version)
        if os.path.exists(model_version_directory) is False:
            os.makedirs(model_version_directory)
        model_common_directory = os.path.join(directory,"common")
        if os.path.exists(model_common_directory) is False:
            os.makedirs(model_common_directory)
        
        valid = self.valid_model_name_and_version(model_name,model_version)
        if valid is False:
            raise ValueError(f"model is not valid")
        current_model_detail = self.__model_dict[model_name][model_version]
        self.__logger.debug(f'model_name {model_name} model_version {model_version}')
        self.__logger.debug(f'current_model_detail {current_model_detail}')
        
        model_related_files = current_model_detail['model_related_files']
        model_related_files_suffix = current_model_detail["model_related_files_suffix"]
        model_related_files_public = current_model_detail["model_related_files_public"]
        
        s3_bucket_name = current_model_detail['s3_bucket']
        for original_current_file_name in model_related_files:
            self.__logger.debug(f'******** original_current_file_name {original_current_file_name}')
            if model_related_files_suffix[original_current_file_name] == "gz":
                file_name_key = f'{original_current_file_name}.gz'
            elif model_related_files_suffix[original_current_file_name] == "direct":
                file_name_key = original_current_file_name
            
            self.__logger.debug(f'******* after process suffix , file_name_key {file_name_key} ')
            if model_related_files_public[original_current_file_name] is False:
                file_name_key = f'{model_name}_{model_version}_{file_name_key}'
                current_model_related_file_dir = model_version_directory                
            else:
                current_model_related_file_dir = model_common_directory
            
            
            current_object_header = self.__awss3tool.get_object_header(s3_bucket_name,file_name_key)
            self.__logger.debug(f'current_object_header {current_object_header}')
            last_formt_dst_file = os.path.join(current_model_related_file_dir,original_current_file_name)
            self.__logger.debug(f'last_formt_dst_file {last_formt_dst_file}')
            if os.path.exists(last_formt_dst_file) is True:
                current_exist_last_format_file_hash = self.__common_tool.calculate_md5_for_big_file(last_formt_dst_file)
                self.__logger.debug(f'current_exist_file_hash {current_exist_last_format_file_hash}')
                if model_related_files_suffix[original_current_file_name] == "gz":
                    s3_exist_last_format_file_hash = current_object_header['Metadata']['uncompress_hash']
                elif model_related_files_suffix[original_current_file_name] == "direct":
                    s3_exist_last_format_file_hash = current_object_header['Metadata']['md5_digest']
                if current_exist_last_format_file_hash == s3_exist_last_format_file_hash:
                    continue
                os.remove(last_formt_dst_file)
                
            
            if model_related_files_suffix[original_current_file_name] == "gz":
                original_file_name_gz = f'{original_current_file_name}.gz'
                original_file_name_gz_path = os.path.join(current_model_related_file_dir,original_file_name_gz)
                if os.path.exists(original_file_name_gz_path) is True:
                    exist_original_file_gz_hash = self.__common_tool.calculate_md5_for_big_file(original_file_name_gz_path)
                    if exist_original_file_gz_hash != current_object_header['Metadata']['md5_digest']:
                        os.remove(original_file_name_gz_path)
                        response = self.__awss3tool.download(original_file_name_gz_path,s3_bucket_name,file_name_key)
                        self.__logger.debug(f'download bucket {s3_bucket_name} file_name_key {file_name_key} response {response}')
                else:
                    response = self.__awss3tool.download(original_file_name_gz_path,s3_bucket_name,file_name_key)
                    self.__logger.debug(f'download bucket {s3_bucket_name} file_name_key {file_name_key} response {response}')
                self.__common_tool.uncompress_file_gzip(original_file_name_gz_path,last_formt_dst_file)
                
                if os.path.exists(original_file_name_gz_path) is True:
                    os.remove(original_file_name_gz_path)   
            elif model_related_files_suffix[original_current_file_name] == "direct":
                response = self.__awss3tool.download(last_formt_dst_file,s3_bucket_name,file_name_key)
                self.__logger.debug(f'download bucket {s3_bucket_name} file_name_key {file_name_key} response {response}')
            if os.path.exists(last_formt_dst_file) is False:
                return False
        return True
                
                
                