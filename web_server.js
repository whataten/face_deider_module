const express = require('express');
const app = express();
const path = require('path');
const PATH = path.join(__dirname, 'views');
app.use(express.static(PATH));

var fileName = "";
const multer = require('multer');
const uuid4 = require('uuid4');
const upload = multer({
    storage: multer.diskStorage({
      	filename(req, file, done) {
            const randomID = uuid4();
            const ext = path.extname(file.originalname);
            fileName = randomID + ext;
          	console.log(file);
			done(null, fileName);
        },
		destination(req, file, done) {
      		console.log(file);
		    done(null, path.join(__dirname, "work_bench"));
	    },
    }),
    limits: { fileSize: 10 * 1024 * 1024}  // 10MB
});

const uploadMiddleware = upload.single('video_file');
var spawn = require('child_process').spawn;

app.post('/upload', uploadMiddleware, (req, res) => {
    const frameNum = req.body.frameNum;
    const leftTopX = req.body.leftTopX;
    const leftTopY = req.body.leftTopY;
    const rightBottomX = req.body.rightBottomX;
    const rightBottomY = req.body.rightBottomY;

    const result = spawn('python3', ['/root/face_deider/face_deider.py', fileName, frameNum, leftTopX, leftTopY, rightBottomX, rightBottomY]);
    
    result.stdout.on('presigned_url', (presigned_url) => {
        console.log("finished!!")
    });
    
    result.stderr.on('data', function(data) {
        console.log("failure", data.toString());
    });
});

app.get('/', (req, res) => {
    const filePath = path.join(__dirname, 'views', 'home.html');
    res.sendFile(filePath);
});

app.get('/deid', (req, res) => {
    const filePath = path.join(__dirname, 'views', 'deid.html');
    res.sendFile(filePath);
});

var PORT = 8080;

app.listen(PORT, () => {
    console.log("Server is running on http://localhost:8080")
});