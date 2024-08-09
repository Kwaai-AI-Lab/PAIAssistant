from llama_index.core import SimpleDirectoryReader
from llama_index.core import ServiceContext
from llama_index.core import VectorStoreIndex
from utils import build_sentence_window_index
from utils import build_automerging_index
from langchain_community.llms import LlamaCpp

import sys
import os
import logging
import configparser

RUNNING_FLAG_FILE = "/pai/api/index/index.running"
COMPLETE_FLAG_FILE = "/pai/api/index/index.complete"

# Write running flag file
try:
    os.remove(COMPLETE_FLAG_FILE)
except FileNotFoundError:
    pass
open(RUNNING_FLAG_FILE, 'a').close()

config = configparser.ConfigParser()
config.read('config.ini')

# get config values
src_data_dir = config['index']['src_data_dir']
basic_idx_dir = config['index']['basic_idx_dir']
sent_win_idx_dir = config['index']['sent_win_idx_dir']
auto_mrg_idx_dir = config['index']['auto_mrg_idx_dir']
modelname = config['index']['modelname']
embed_modelname = config['index']['embedmodel']
useopenai = config.getboolean('index', 'useopenai')


def check_and_create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")
    else:
        print(f"Directory '{directory_path}' already exists.")

def construct_basic_index(src_directory_path,index_directory):
    check_and_create_directory(index_directory)
    if useopenai:
        from langchain.chat_models import ChatOpenAI
        modelname = config['api']['openai_modelname']
        llm =ChatOpenAI(temperature=0.1, model_name=modelname)
    else:
        modelname = config['api']['local_modelname']
        n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
        n_batch = 4096  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
        llm = LlamaCpp(
        model_path="./models/"+ modelname,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        n_ctx=4096,
        n_threads=8,
        temperature=0.1,
        f16_kv=True
        )

    service_context = ServiceContext.from_defaults(
        llm=llm, embed_model=embed_modelname
    )

    documents = SimpleDirectoryReader(src_directory_path, recursive=True).load_data()
    index = VectorStoreIndex.from_documents(documents,
                                            service_context=service_context)
    # pickup any changes in documents and update index
    index.refresh_ref_docs(documents)
    index.storage_context.persist(persist_dir=index_directory)
    return index

def construct_sentencewindow_index(src_directory_path,index_directory):

    if useopenai:
        from langchain.chat_models import ChatOpenAI
        modelname = config['api']['openai_modelname']
        llm =ChatOpenAI(temperature=0.1, model_name=modelname)
    else:
        modelname = config['api']['local_modelname']
        n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
        n_batch = 4096  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
        llm = LlamaCpp(
        model_path="./models/"+ modelname,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        n_ctx=4096,
        n_threads=8,
        temperature=0.1,
        f16_kv=True
        )
    documents = SimpleDirectoryReader(src_directory_path, recursive=True).load_data()
    index = build_sentence_window_index(
    documents,
    llm,
    embed_model=embed_modelname,
    save_dir=index_directory
    )
    return index

def construct_automerge_index(src_directory_path,index_directory):
    if useopenai:
        from langchain.chat_models import ChatOpenAI
        modelname = config['api']['openai_modelname']
        llm =ChatOpenAI(temperature=0.1, model_name=modelname)
    else:
        modelname = config['api']['local_modelname']
        n_gpu_layers = -1  # Change this value based on your model and your GPU VRAM pool.
        n_batch = 4096  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
        llm = LlamaCpp(
        model_path="./models/"+ modelname,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        n_ctx=4096,
        n_threads=8,
        temperature=0.1,
        f16_kv=True
        )
    documents = SimpleDirectoryReader(src_directory_path, recursive=True).load_data()

    index = build_automerging_index(
    documents,
    llm,
    embed_model=embed_modelname,
    save_dir=index_directory
    )
    return index


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


#Create basic index
if basic_idx_dir is not None and basic_idx_dir != "":
    index = construct_basic_index(src_data_dir,basic_idx_dir)
#create sentencewindow index
if sent_win_idx_dir is not None and sent_win_idx_dir != "":
    sentindex = construct_sentencewindow_index(src_data_dir,sent_win_idx_dir)
#create automerge index
if auto_mrg_idx_dir is not None and auto_mrg_idx_dir != "":
    autoindex = construct_automerge_index(src_data_dir,auto_mrg_idx_dir)

# Write completed flag file
try:
    os.remove(RUNNING_FLAG_FILE)
except FileNotFoundError:
    pass
open(COMPLETE_FLAG_FILE, 'a').close()
