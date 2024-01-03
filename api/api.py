
from llama_index import StorageContext, load_index_from_storage, ServiceContext
import gradio as gr
import sys
import os
import logging
from utils import get_automerging_query_engine
from utils import get_sentence_window_query_engine
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


os.environ["GRADIO_ANALYTICS_ENABLED"]='False'

indextype=config['api']['indextype'] 

embed_modelname = config['api']['embedmodel']
basic_idx_dir = config['index']['basic_idx_dir']
sent_win_idx_dir = config['index']['sent_win_idx_dir']
auto_mrg_idx_dir = config['index']['auto_mrg_idx_dir']
serverip = config['api']['host']
serverport = config['api']['port']
sslcert = config['api']['sslcert']
sslkey = config['api']['sslkey']
useopenai = config.getboolean('api', 'useopenai')
# Get the logging level
log_level_str = config.get('api', 'loglevel', fallback='WARNING').upper()
# Convert the log level string to a logging level
log_level = getattr(logging, log_level_str, logging.WARNING)

def chatbot(input_text):
    
    if indextype == 'basic':
        query_engine = index.as_query_engine()
    elif indextype == 'sentence' :
        query_engine =get_sentence_window_query_engine(index)
    elif indextype == 'automerge':
        query_engine = get_automerging_query_engine(automerging_index=index, service_context=service_context)
        
    response =query_engine.query(input_text)    
    return response.response
    
logging.basicConfig(stream=sys.stdout, level=log_level)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, label="Enter your text"),
                     outputs="text",
                     title="Email data query")

 
from langchain.llms import LlamaCpp

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
    temperature=0.1,
    f16_kv=True
    )

 
service_context = ServiceContext.from_defaults(
    llm=llm, embed_model=embed_modelname
)

index_directory=''
if indextype == 'basic':
    index_directory = basic_idx_dir
elif indextype == 'sentence' :
    index_directory = sent_win_idx_dir
elif indextype == 'automerge':
    index_directory = auto_mrg_idx_dir

print(config['api']['indextype'] )
print(index_directory)
# load index
storage_context = StorageContext.from_defaults(persist_dir=index_directory)
index = load_index_from_storage(storage_context=storage_context, service_context=service_context)   
iface.launch( share=False, server_name=serverip, server_port=int(serverport), ssl_verify=False, ssl_keyfile=sslkey, ssl_certfile=sslcert)