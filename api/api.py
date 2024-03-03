from llama_index import StorageContext, load_index_from_storage, ServiceContext
import gradio as gr
import sys
import os
import logging
from utils import get_automerging_query_engine
from utils import get_sentence_window_query_engine
import configparser
from TTS.api import TTS
from gtts import gTTS
import simpleaudio as sa
import threading
from datetime import datetime
import json
import subprocess
from llama_index.prompts.base import PromptTemplate
from inference import main as generateVideo
import pyttsx3

def run_inference(checkpoint_path, face_video, audio_file, resize_factor, outfile):
    
    # Construct the command with dynamic parameters
    command = [        
        "--checkpoint_path", checkpoint_path,
        "--face", face_video,
        "--audio", audio_file,
        "--resize_factor", str(resize_factor),
        "--outfile", outfile
    ]
    print(command)    
    generateVideo(command)
    


def play_sound_then_delete(path_to_wav):
    def play_and_delete():
        try:
            wave_obj = sa.WaveObject.from_wave_file(path_to_wav)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until the sound has finished playing
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            try:
                #os.remove(path_to_wav)
                print(f"File {path_to_wav} successfully deleted.")
            except Exception as e:
                print(f"Error deleting file: {e}")
     # Start playback in a new thread
    threading.Thread(target=play_and_delete, daemon=True).start()


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
ttsengine = config['api']['ttsengine']
# Get the logging level
log_level_str = config.get('api', 'loglevel', fallback='WARNING').upper()
# Convert the log level string to a logging level
log_level = getattr(logging, log_level_str, logging.WARNING)

def chatbot(input_text):
    global tts
    print("User Text:" + input_text)    
    
    response =query_engine.query(input_text)        
 
    # Save the output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_audfile=f"output_{timestamp}.wav"
    output_vidfile=f"output_{timestamp}.mp4"
    output_path = "../web/public/audio/output/"+output_audfile
    
    
    if ttsengine == 'coqui':
        tts.tts_to_file(text=response.response, file_path=output_path ) # , speaker_wav=["bruce.wav"], language="en",split_sentences=True)
    elif ttsengine == 'gtts':
        tts = gTTS(text=response.response, lang='en')
        tts.save(output_path)
    else:
        tts.save_to_file(response.response , output_path)
        tts.runAndWait()

    checkpoint_path = "./checkpoints/wav2lip_gan.pth"
    face_video = "media/Avatar.mp4"
    audio_file = "../web/public/audio/output/"+output_audfile
    outfile="../web/public/video/output/"+output_vidfile
    resize_factor = 2
    run_inference(checkpoint_path, face_video, audio_file, resize_factor, outfile)
    #play_sound_then_delete(output_path)

    #construct response object
    # Building the citation list from source_nodes
    citation = [
        {
            "filename": node.metadata["file_name"],
            "text": node.get_text()
        } for node in response.source_nodes
    ]
    
    # Creating the JSON object structure
    jsonResponse = {
        "response": response.response,
        "video": output_vidfile,
        "audio": output_audfile,
        "citation": citation
    }
    
    # Convert to JSON string
    jsonResponseStr = json.dumps(jsonResponse, indent=4)
        
    return jsonResponseStr
    
logging.basicConfig(stream=sys.stdout, level=log_level)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, label="Enter your text"),
                     outputs="text",
                     title="Email data query")

 
from langchain.llms import LlamaCpp
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

#from langchain.globals import set_debug
#set_debug(True)


if useopenai:
    from langchain.chat_models import ChatOpenAI
    modelname = config['api']['openai_modelname']
    llm =ChatOpenAI(temperature=0.1, model_name=modelname)
else:
    modelname = config['api']['local_modelname']
    n_gpu_layers = -1  # Change this value based on your model and your GPU VRAM pool.
    n_batch = 2048  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
    
    #cache prompt/response pairs for faster retrieval next time.
    set_llm_cache(InMemoryCache())
    
    llm = LlamaCpp(
    model_path="./models/"+ modelname,
    cache=True,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    n_ctx=2048,
    n_threads=8,
    temperature=0.01,
    max_tokens=512,
    f16_kv=True,
    repeat_penalty=1.1,
    min_p=0.05,
    top_p=0.95,
    top_k=40,
    stop=["<|end_of_turn|>"]  
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
if ttsengine == 'coqui':
    tts = TTS(model_name="tts_models/en/ljspeech/vits--neon", progress_bar=False).to("cuda")
    #tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to("cuda")
elif ttsengine == 'gtts':
    tts = gTTS(text='', lang='en')        
else: 
    tts = pyttsx3.init()
    voices = tts.getProperty('voices')
    tts.setProperty('voice', voices[1].id)  # this is female voice
    rate = tts.getProperty('rate')
    tts.setProperty('rate', rate-50)


# load index
storage_context = StorageContext.from_defaults(persist_dir=index_directory)
index = load_index_from_storage(storage_context=storage_context, service_context=service_context)   
if indextype == 'basic':
    query_engine = index.as_query_engine()
elif indextype == 'sentence' :
    query_engine =get_sentence_window_query_engine(index)
elif indextype == 'automerge':
    query_engine = get_automerging_query_engine(automerging_index=index, service_context=service_context)

#prompts_dict = query_engine.get_prompts()
#print(list(prompts_dict.keys()))
    
# Optional: Adjust prompts to suit the llms.

qa_prompt_tmpl_str = (
    "GPT4 User: You are an assistant named Maggie. You assist with any questions regarding the organization kwaai.\n"
    "Context information is below\n"
    "----------------------\n"
    "{context_str}\n"
    "----------------------\n"
    "Given the context information and not prior knowledge respond to user: {query_str}\n"
    "<|end_of_turn|>GPT4 Assistant:"
)
qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)
query_engine.update_prompts(
    {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
)


iface.launch( share=False, server_name=serverip, server_port=int(serverport), ssl_verify=False, ssl_keyfile=sslkey, ssl_certfile=sslcert)