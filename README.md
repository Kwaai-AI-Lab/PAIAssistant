<h1 align="center">Welcome to PAIAssistant 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000" />
  <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">
    <img alt="License: CC-BY-4.0" src="https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg" />
  <a href="https://kwaaiailab.slack.com" target="_blank">
    <img alt="Slack: Kwaai.org" src="https://img.shields.io/badge/slack-join-green?logo=slack" />
  </a>
  <a href=" https://releases.ubuntu.com/focal/" target="_blank">
    <img alt="Ubuntu" src="https://img.shields.io/ubuntu/v/ubuntu-wallpapers/focal" />
  </a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.10-blue" />
  <img alt="Browser" src="https://img.shields.io/badge/Browser-chrome-red" />
</p>


PAIAssistant is a AI tool designed for users interact with emails via natural language queries. This demo showcases its ability to organize emails using a vector database. It features various Retrieval-Augmented Generation (RAG) methods including Basic Retrieval, Sentence Window Retrieval, and Auto-Merging Retrieval. These methods enhance the processing of user queries, which are then handled by a Large Language Model (LLM) like OpenAI's. The AI generates responses that can be either displayed on-screen or read aloud, offering a comprehensive and user-friendly email management experience.

The best way to support Kwaai is to give us a ⭐ on [GitHub](https://github.com/KWAAI-ai-lab/paiassistant) and join our [slack community](https://kwaaiailab.slack.com)!

### Demo clip
![](doc/DemoPA.gif) 

### Docker setup (Required: Nvidia RTX series GPU)
1. Install docker desktop from <a href="https://www.docker.com/products/docker-desktop/" target="_blank">Docker Desktop</a>
2. Clone the git repository
3. Change to PAIAssistant folder and run "docker-compose build"
4. Once Step 3 completes you should have paiassistant-pai:latest image in docker ( mine was about 20GB or so )
5. Run image using "docker run -it --rm -p 4000:4000 --gpus all paiassistant-pai:latest"
6. At this point you should be able to visit https://127.0.0.1:4000. It wont function fully until you populate it with your data.
7. Find your container name using  "docker ps --format "{{.Names}}"
8. Copy pdf files to container in a folder for eg. "docker cp Mypdfdir (containername from step 7):/pai/api/data/Mypdfdir
9. Update api/config.ini file to use the newly created folder in step 8 for indexing and querying.
10. Download and Copy your model file to api/models folder using same step like you used the pdf copy in step 8. <a href="https://huggingface.co/TheBloke/openchat_3.5-GGUF/blob/main/openchat_3.5.Q4_K_M.gguf" target="_blank">Openchat 3.5</a>
11. Update the api/config.ini to reflect the model file name.
12. Run api/createindex.py to create the index.
13. Start the api process using "python api.py" from api folder.
14. Now you can chat with the files using https://127.0.0.1:4000
15. [Optionally update the prompt in the api.py and restart to suit the files knowledge base]


### VM Installation and Setup
The steps below can be used to setup the enviroment for this demo to run on Ubuntu 20.04.6 LTS.
Alternatively you can setup the python3.10 environment on a windows machine with Nvidia gpu card with necessary drivers.
The install will run with or without GPU. Running locally would be very slow on CPU inference. 
Running with OpenAI support could be alternative if GPU is not available. 

Optional: Check flag/api key settings in documentation to use OpenAI if you dont have a computer with GPU

#### Optional: If you already have access to ubuntu instance, you can skip this section.

NOTE: This example VM setup will work for OpenAI inference. Local inference will be very slow due to lack of GPU. For local inference use a machine with GPU, windows or linux.

1. Download <a href="https://releases.ubuntu.com/focal/" target="_blank">Ubuntu 20.04.6 LTS server ISO image.</a>
2. Download <a href="https://www.virtualbox.org/wiki/Downloads" target="_blank">Oracle VirtualBox.</a> 
3. Create a new virtual machine with the ubuntu image downloaded above. Sample configuration is 4gb ram, 2 vcpu, bridged network settting, 25 gb disk.
4. Optional : Signup for platform.openai.com and <a href="https://platform.openai.com/api-keys">generate OpenAI api key</a>


### Clone repository and update config
1. Change directory to web. If necessary update host/port parameter in config.json
2. Change directory to web/public. Update the completion.apiendpoint to the ip address of your instance.
3. Change directory to api. Update config.ini to update host/port parameters if needed.

#### Setup environment and required packages
```bash
    cd PAIAssistant
    ./setupenv.sh
```
### Data set and index
1. Create a new folder under api/data and copy over the data in pdf/csv/doc etc
2. Update api/config.ini to update the folder name data/<folder> and run createindex.py to create the vector index (basic/sentence/automerge) for query.
```bash     
    cd api    
    # By default index is created using local embedding file in config.ini
    # if you dont have gpu, use export below and set useopenai flag to true to use openai api. 
    # adjust modelname accordingly for openai.
    # export OPENAI_API_KEY=<YOUR OPENAI API KEY>    
    python createindex.py
```

#### Choose index to query
Choose which version of index to query by updating the config.ini in api folder [api] section.

#### Bring up the website and api service
```bash
    cd web    
    npm start

    cd api   
    # export below is optional. Use when you dont have gpu or if you want to use openai models. 
    #export OPENAI_API_KEY=<YOUR OPENAI API KEY>
    python api.py
```

#### Running locally vs using openai 
To use openai set the following attribute in api/config.ini.
By default it is set to false.

useopenai=true

#### Visit in chrome browser
1. https://[ipaddress]:4000 in chrome browser to use the demo.
2. https://[ipaddress]:7860 gradio text input/response interface.

### TODO
- [ ] Create a jupyter notebook
- [ ] Create google colab notebook
- [ ] Create git workflow to post to hosting platform to visualize it.

## 📝 License

This project is [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) licensed.

