from datetime import datetime
import gzip
import hashlib
import json
import os
import pandas as pd
import shutil


class CommonTool:
    def __init__(self) -> None:
        self.__language_set = set(['english'])

    def read_excel(self,path):
        if isinstance(path,str) is False:
            raise ValueError('path is not str')
        df = pd.read_excel(path)
        return json.loads(df.to_json(orient='records'))
    
    def write_json(self,content,path):
        if isinstance(content,dict) is False:
            raise ValueError("content is not dict")
        if isinstance(path, str) is False:
            raise ValueError("path is not str")
        with open(path, "w") as outfile:
            json.dump(content, outfile)
    
    def read_json(self,path):
        if isinstance(path,str) is False:
            raise ValueError("path is not str")
        if os.path.exists(path) is False:
            raise ValueError('current_path {current_path} is not exist'.format(current_path = path))
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        return data
    
    def get_project_directory(self):
        project_root = os.path.dirname(os.path.dirname(__file__))
        return project_root
    
    def get_offset_from_utc_hours(self,time_zone):
        import datetime
        current_time = datetime.datetime.now(time_zone)
        offset_hours = current_time.utcoffset().total_seconds()/60/60
        return offset_hours
    
    def get_logger(self):
        import logging
        logger = logging.getLogger(__name__)
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
        logging.basicConfig(format=FORMAT)
        logger.setLevel(logging.DEBUG)
        return logger
    
    def calculate_md5(self,path):
        if isinstance(path,str) is False:
            raise ValueError("path is not str")
        if os.path.exists(path) is False:
            raise ValueError(f'path {path} is not exist')
        with open(path, 'rb') as f:
            digest = hashlib.md5(f.read()).hexdigest()
        return digest
    
    def calculate_md5_for_big_file(self,path,blocksize=2**27):
        if isinstance(path,str) is False:
            raise ValueError("path is not str")
        if os.path.exists(path) is False:
            raise ValueError(f'path {path} is not exist')
        m = hashlib.md5()
        with open( path , "rb" ) as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                m.update( buf )
        return m.hexdigest()
    
    def uncompress_file_gzip(self,input_path,output_path):
        if isinstance(input_path,str) is False:
            raise ValueError(f'input_path is not str')
        if os.path.exists(input_path) is False:
            raise ValueError(f'input_path {input_path} is not exist')
        if input_path[len(input_path)-3:] != ".gz":
            raise ValueError(f'not valid gz')
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out,length=2**20)
    
    
    def compute_diff_time(self,start_time,end_time):
        if isinstance(start_time,datetime) is False:
            raise ValueError('start_time is not datetime')
        if isinstance(end_time,datetime) is False:
            raise ValueError('end_time is not datetime')
        if end_time < start_time:
            raise ValueError('end_time is small than start_time')
        diff = end_time-start_time 
        diff_in_seconds = diff.total_seconds() 
        return diff_in_seconds
    
