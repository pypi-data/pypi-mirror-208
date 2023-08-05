import boto3
import sys 

from recommend_model_sdk.tools.common_tool import CommonTool

class AWSS3Tool:
    def __init__(self) -> None:
        self.__client = boto3.client('s3')
        self.__common_tool = CommonTool()
        self.__logger = self.__common_tool.get_logger()
    
    def upload_file(self,local_path,bucket_name,key):
        response = self.__client.upload_file(local_path,bucket_name,key)
        return response
    
    def get_file_size(self,s3_bucket, s3_object_key):
        meta_data = self.__client.head_object(Bucket=s3_bucket, Key=s3_object_key)
        total_length = int(meta_data.get('ContentLength', 0))
        return total_length
    
    

    def download(self,local_file_name, s3_bucket, s3_object_key):

        meta_data = self.__client.head_object(Bucket=s3_bucket, Key=s3_object_key)
        total_length = int(meta_data.get('ContentLength', 0))
        downloaded = 0

        def progress(chunk):
            nonlocal downloaded
            downloaded += chunk
            done = int(50 * downloaded / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )

        with open(local_file_name, 'wb') as f:
            response = self.__client.download_fileobj(s3_bucket, s3_object_key, f, Callback=progress)
        return response
    
    def put_object(self,byte_body,bucket_name,key,content_type):
        if isinstance(bucket_name,str) is False:
            raise ValueError("bucket name is not str")
        if isinstance(key,str) is False:
            raise ValueError("key is not str")
        if isinstance(content_type,str) is False:
            raise ValueError("content_type is not str")
        response = self.__client.put_object(
            Body=byte_body,
            Bucket=bucket_name,
            Key=key,
            ContentType=content_type
        )
        return response
    

    def get_object(self,bucket_name,key):
        if isinstance(bucket_name,str) is False:
            raise ValueError("bucket name is not str")
        if isinstance(key,str) is False:
            raise ValueError("key is not str")
        response = self.__client.get_object(
            Bucket=bucket_name,
            Key=key,
        )
            
            
        return response
    
    def get_object_byte(self,bucket_name,key):
        if isinstance(bucket_name,str) is False:
            raise ValueError("bucket name is not str")
        if isinstance(key,str) is False:
            raise ValueError("key is not str")
        response = self.__client.get_object(
            Bucket=bucket_name,
            Key=key,
        )
        result=dict()
        if ("ResponseMetadata" not in response or 
            "HTTPStatusCode" not in response["ResponseMetadata"] or
            response["ResponseMetadata"]["HTTPStatusCode"] != 200):
            self.__logger.error(f"get bucket {bucket_name} key {key} fail, response {response}")
            result["success"] = False
            result["response"] = response
            
        else:
            current_byte = response["Body"].read()
            result["success"] = True
            result["response"] = response
            result["bytes"] = current_byte
        return result
            
            
            
        

    
    def get_object_header(self,s3_bucket, s3_object_key):
        meta_data = self.__client.head_object(Bucket=s3_bucket, Key=s3_object_key)
        return meta_data
    