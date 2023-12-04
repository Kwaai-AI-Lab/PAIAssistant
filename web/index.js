const https = require('https');
const express = require('express');
const fs = require('fs');
const config = require('./config.json');
const app = express();
const PORT = config.server.port;
const HOST = config.server.host;


const key = fs.readFileSync(config.certificate.key);
const cert = fs.readFileSync(config.certificate.cert);

app.use(express.static('public'));
const server = https.createServer({key: key, cert: cert }, app);

app.get('/', (req, res) => {
    res.send('Hi, I am a Personal Email Assistant.');
});

server.listen(PORT,HOST, () => { console.log('listening on '+HOST+":"+ PORT) });


