FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y \
        net-tools \
        python3.10 \
        python3-pip \
        npm \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --config python3

WORKDIR /app/web
COPY web/package*.json ./
RUN npm install

COPY web/ .

WORKDIR /app/api
COPY api/ .

RUN pip install -r requirements.txt

EXPOSE 4000
EXPOSE 7860

ENV OPENAI_API_KEY <SAMPLE_OPENAI_API_KEY>

CMD ["sh", "-c", "python api.py & npm start"]
