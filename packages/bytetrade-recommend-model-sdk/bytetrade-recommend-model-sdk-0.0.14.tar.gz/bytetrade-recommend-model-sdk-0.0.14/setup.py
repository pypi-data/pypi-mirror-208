from setuptools import setup,find_packages
import os,sys
try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements


def parse_requiremnt():
    file_dir = os.path.abspath(os.path.dirname(__file__))
    requirement_filename  = os.path.join(file_dir,"requirements.txt")
    install_reqs = parse_requirements(requirement_filename,session='hack')
    
    try:
        requirements = [str(ir.req) for ir in install_reqs]
    except:
        requirements = [str(ir.requirement) for ir in install_reqs]
    print(requirements)
    return requirements

sys.path.append(os.path.dirname(__file__) + "/recommend-model")




setup(
    name="bytetrade-recommend-model-sdk",
    version="0.0.14",
    # packages=find_packages(exclude="unit_test"),
    install_requires=[
        "pandas==2.0.0",
        "gensim==4.3.1",
        "protobuf==4.21.8",
        "nltk==3.8.1",
        "boto3"
    ],
    include_package_data=True
)