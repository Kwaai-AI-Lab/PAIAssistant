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
// Handle byte range requests for MP4 files
app.get('/video/:name', (req, res) => {
    const videoName = req.params.name;
    const videoPath = path.join(__dirname, 'public', videoName); // Assuming videos are stored in the 'public' folder
    const stat = fs.statSync(videoPath);
    const fileSize = stat.size;
    const range = req.headers.range;

    if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
        const chunkSize = (end - start) + 1;
        const file = fs.createReadStream(videoPath, {start, end});
        const head = {
            'Content-Range': `bytes ${start}-${end}/${fileSize}`,
            'Accept-Ranges': 'bytes',
            'Content-Length': chunkSize,
            'Content-Type': 'video/mp4',
        };
        res.writeHead(206, head);
        file.pipe(res);
    } else {
        const head = {
            'Content-Length': fileSize,
            'Content-Type': 'video/mp4',
        };
        res.writeHead(200, head);
        fs.createReadStream(videoPath).pipe(res);
    }
});

const server = https.createServer({key: key, cert: cert }, app);

app.get('/', (req, res) => {
    res.send('Hi, I am a Personal Email Assistant.');
});

server.listen(PORT,HOST, () => { console.log('listening on '+HOST+":"+ PORT) });


