const https = require('https');
const express = require('express');
const fs = require('fs');
const config = require('./config.json');
const app = express();
const PORT = config.server.port;
const HOST = config.server.host;
const allowSelfSignedSSL = config.server.allowSelfSignedSSL;


const key = fs.readFileSync(config.certificate.key);
const cert = fs.readFileSync(config.certificate.cert);

app.use(express.static('public'));
// For parsing application/json
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

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


// Forward route for /run/predict with JSON payload
app.post('/run/predict', (req, res) => {
        // Check if the expected fields exist in the request body
        //
        // console.log('Received body: ' , req.body)
    
        // Attempt to parse the first item in the 'data' array as JSON
        let postData;
        postData= JSON.stringify(req.body);
    
        const options = {
            hostname: 'localhost',
            port: 7860,
            path: '/run/predict',
            method: 'POST', // Assuming POST method, modify if needed
            headers: {
                ...req.headers,
                'Content-Type': 'application/json', // Ensure the content-type is set for JSON
                'Content-Length': Buffer.byteLength(postData), // Set the content length
            },
            rejectUnauthorized: !allowSelfSignedSSL // This bypasses the certificate validation
        };
    
        // Remove the 'host' header to avoid issues with the target server
        delete options.headers.host;
    
        const apiRequest = https.request(options, (apiResponse) => {
            let data = ''; // Initialize data variable to collect the response
            apiResponse.on('data', (chunk) => {
                data += chunk;
            });
            apiResponse.on('end', () => {
                res.setHeader('Content-Type', 'application/json');
                res.send(data); // Send back the data received from the internal API
            });
        });
    
        apiRequest.on('error', (error) => {
            console.error(error);
            res.status(500).send('Internal Server Error');
        });
    
        apiRequest.write(postData); // Write the JSON payload to the API request
        apiRequest.end(); // End the API request
    });
    
    

const server = https.createServer({key: key, cert: cert }, app);

app.get('/', (req, res) => {
    res.send('Hi, I am an AI Assistant.');
});

server.listen(PORT,HOST, () => { console.log('listening on '+HOST+":"+ PORT) });


