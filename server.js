// express
const express = require('express');
const app = express();
const path = require('path');
const publicPath = path.join(__dirname, 'public');
app.use(express.static(publicPath));

// upload
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
		    done(null, path.join(__dirname, "uploads"));
	    },
    }),
    // limits: { fileSize: 1024 * 1024},
});

// api
const uploadMiddleware = upload.single('myFile');
var spawn = require('child_process').spawn;

app.post('/upload', uploadMiddleware, (req, res) => {
    const frameNum = req.body.frame;
    const leftTopX = req.body.x1;
    const leftTopY = req.body.y1;
    const rightBottomX = req.body.x2;
    const rightBottomY = req.body.y2;

    const result = spawn('python3', ['/root/face_deider/face_deider.py', fileName, leftTopX,leftTopY,rightBottomX,rightBottomY, frameNum]);
    
    result.stdout.on('data', function(data) {
        const filePath = path.join(__dirname, "downloads/") + fileName;
        
        res.sendFile(filePath, (err) => {
            if (err) {
                console.error('Error sending file:', err.message);
                return res.status(err.status || 500).end();
            } else {
                console.log('File sent successfully:', fileName)
            }
        });
    })
    
    result.stderr.on('data', function(data) {
        console.log("failure", data.toString());
    });
});

app.listen(PORT, () => {
    console.log("Server is running on http://localhost:8080")
});