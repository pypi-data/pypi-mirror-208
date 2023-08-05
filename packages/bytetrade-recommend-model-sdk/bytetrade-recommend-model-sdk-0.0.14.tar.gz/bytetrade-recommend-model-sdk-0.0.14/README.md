
  

# recommend-model-sdk

  

## install method

use conda or pyenv create environment ,then install following requirements.txt

rquirements.txt

```

pandas==2.0.0

gensim==4.3.1

protobuf==4.21.8

nltk==3.8.1

boto3

```

```

pip install -r requiremnts.txt

```

  

```

pip install -i https://test.pypi.org/simple/ bytetrade-recommend-model-sdk==0.0.5

```

  

## example

  

### init model

```

from recommend_model_sdk.tools.model_tool import ModelTool

current_model_tool = ModelTool("~")

```

the parameter is working directory, needed to be fixed

### get valid model name and version

```

from recommend_model_sdk.tools.model_tool import ModelTool

result = current_model_tool.get_valid_model_and_version()

```

result is

```

{'word2vec_google': ['v1']}

```

the key is model name, the value is valid model version list

  

### init model environment

```

current_model_tool.init_model("word2vec_google","v1")

```

  

### downlatest article and embedding package

```

download_dir = "/home/ubuntu/download_s3"

current_model_tool = ModelTool(download_dir)

model_name = "word2vec_google"

model_version = "v1"

latest_number = 1000

latest_package_key = f'{model_name}_{model_version}_latest_package_{latest_number}'

article_embedding_dict = current_model_tool.download_latest_article_embedding_package(model_name,model_version,latest_number)

article_list = article_embedding_dict["articles"]
embedding_list = article_embedding_dict["embeddings"]
```

  

### infer document

```

download_dir = "/home/ubuntu/download_s3"

current_model_tool = ModelTool(download_dir)

model_name = "word2vec_google"

model_version = "v1"

id_to_document = dict()

id_to_document["1"] = "what a beautiful book"

id_to_document["2"] = "garbage is resources"

current_model_tool.infer(model_name,model_version,id_to_document)

```
infer result 
{
   'id':{'success':True, 'vec':numpy.array}
}
