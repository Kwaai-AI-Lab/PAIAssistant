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

The best way to support TruLens is to give us a ⭐ on [GitHub](https://github.com/KWAAI-ai-lab/paiassistant) and join our [slack community](https://kwaaiailab.slack.com)!

### Demo clip
<video src="doc/DemoPA.mp4" controls title="Title"></video>
 
### Installation and Setup
The steps below can be used to setup the enviroment for this demo to run on Ubuntu 20.04.6 LTS.

If you already have access to ubuntu instance, you can skip this section.

1. Download <a href="https://releases.ubuntu.com/focal/" target="_blank">
    Ubuntu 20.04.6 LTS server ISO image.
  </a>
2. Download <a href="https://www.virtualbox.org/wiki/Downloads" target="_blank">
    Oracle VirtualBox.
  </a> 
3. Create a new virtual machine with the ubuntu image downloaded above. Sample configuration is 4gb ram, 2 vcpu, bridged network settting, 25 gb disk.
4. Signup for platform.openai.com and <a href="https://platform.openai.com/api-keys">generate OpenAI api key</a>


#### Install net-tools and update fresh linux vm.
```bash
    sudo apt install net-tools
    sudo apt update && sudo apt upgrade
```
#### Install Python 3.10
```bash
    sudo apt install software-properties-common -y
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install python3.10
    sudo apt install python-is-python3
```
#### Setup Python 3.10 as default
```bash
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    sudo update-alternatives --config python3
```
#### Setup Pip
```bash
    curl https://bootstrap.pypa.io/get-pip.py | python
    sudo apt install python3.10-distutils
```
#### Install npm & reboot 
```bash
    sudo apt install npm
    sudo reboot now
```
### Clone repository and update config
1. Change directory to web. If necessary update host/port parameter in config.json
2. Change directory to web/public. Update the completion.apiendpoint to the ip address of your instance.
3. Change directory to api. Update config.ini to update host/port parameters if needed.

#### Bring up the website and api service
```bash
    cd web
    npm install
    npm start

    cd api
    pip install -r requirements.txt
    export OPENAI_API_KEY=<YOUR OPENAI API KEY>
    python api.py
```

#### Visit in chrome browser
1. https://[ipaddress]:4000 in chrome browser to use the demo.
2. https://[ipaddress]:7860 gradio text input/response interface.


## 📝 License

This project is [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) licensed.

