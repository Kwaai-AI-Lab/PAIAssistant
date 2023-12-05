
from llama_index import StorageContext, load_index_from_storage, ServiceContext
from langchain.chat_models import ChatOpenAI
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
modelname = config['api']['modelname']
embed_modelname = config['api']['embedmodel']
basic_idx_dir = config['index']['basic_idx_dir']
sent_win_idx_dir = config['index']['sent_win_idx_dir']
auto_mrg_idx_dir = config['index']['auto_mrg_idx_dir']
serverip = config['api']['host']
serverport = config['api']['port']
sslcert = config['api']['sslcert']
sslkey = config['api']['sslkey']

def chatbot(input_text):
    
    if indextype == 'basic':
        query_engine = index.as_query_engine()
    elif indextype == 'sentence' :
        query_engine =get_sentence_window_query_engine(index)
    elif indextype == 'automerge':
        query_engine = get_automerging_query_engine(index)
        
    response =query_engine.query(input_text)    
    return response.response
    
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, label="Enter your text"),
                     outputs="text",
                     title="Email data query")

 

llm =ChatOpenAI(temperature=0.1, model_name=modelname)
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