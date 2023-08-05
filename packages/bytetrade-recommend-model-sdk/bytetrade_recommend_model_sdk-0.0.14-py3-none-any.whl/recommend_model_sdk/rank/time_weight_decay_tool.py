from recommend_model_sdk.tools.common_tool import CommonTool
from datetime import datetime

class TimeWeightDecayTool:
    def __init__(self,DECLINE_RATE=0.9,DECLINE_CYCLE=86400 ,LINEAR_SCALE=25,TIME_COMPRESS_RATE=5) -> None:
        # https://blog.csdn.net/Vincent_Field/article/details/104115170
        # https://datascience.stackexchange.com/questions/81169/why-is-the-cosine-distance-used-to-measure-the-similatiry-between-word-embedding
        if isinstance(DECLINE_RATE,float) is False:
            raise ValueError("DECLINE_RATE is not float")
        if DECLINE_RATE < 0 or DECLINE_RATE > 1:
            raise ValueError("DECLINE_RATE is not valid")
        if isinstance(DECLINE_CYCLE,int) is False and  isinstance(DECLINE_CYCLE,float) is False:
            raise ValueError("DECLINE_CYCLE is not float")
        if isinstance(LINEAR_SCALE,int) is False:
            raise ValueError("LINEAR_SCALE is not int")
        if LINEAR_SCALE < 1:
            raise ValueError("LINEAR_SCALE is small than 1")
        if isinstance(TIME_COMPRESS_RATE,int) is False:
            raise ValueError("TIME_COMPRESS_RATE is not int")
        if TIME_COMPRESS_RATE < 1:
            raise ValueError("TIME_COMPRESS_RATE is small than 1")
        self.__common_tool = CommonTool()
        self.__DECLINE_RATE = DECLINE_RATE
        self.__DECLINE_CYCLE = DECLINE_CYCLE
        self.__LINEAR_SCALE = LINEAR_SCALE
        self.__TIME_COMPRESS_RATE = TIME_COMPRESS_RATE
        
    
    def compute(self,weight,start_time,end_time):
        if isinstance(weight,float) is False and isinstance(weight,int) is False:
            raise ValueError("weight is not number")
        if isinstance(start_time,datetime) is False:
            raise ValueError("start_time is not datetime")
        if isinstance(end_time,datetime) is False:
            raise ValueError("end_time is not datetime")
        diff_time_seconds = self.__common_tool.compute_diff_time(start_time,end_time)
        decay_weight = weight-weight * pow(self.__DECLINE_RATE,self.__LINEAR_SCALE/pow(diff_time_seconds/self.__DECLINE_CYCLE,1.0/self.__TIME_COMPRESS_RATE))
        return decay_weight