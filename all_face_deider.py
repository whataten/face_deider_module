import cv2
from ultralytics import YOLO
import torch

# 변수 선언
model       = YOLO('/root/face_deider/model_weight.pt')
PATH        = '/root/face_deider/work_bench/'
fileName    = 'add_new.mp4'
path        = PATH + fileName
cap         = cv2.VideoCapture(path)
fps         = cap.get(cv2.CAP_PROP_FPS)
frameNum    = 0
cvtdFrames  = []

while cap.isOpened():
    success, frame = cap.read()
    
    if success:
        results = model.track(frame, persist=True)
        annotatedFrame = results[0].orig_img
        isDetected = torch.all(results[0].boxes.cls == 0).item()

        if isDetected:
            boxes = results[0].boxes.xywh.cpu()
            for box in boxes:
                x, y, w, h = box
                
                left = x - (w/2)
                top = y - (h/2)
                right = x + (w/2)
                bottom = y + (h/2)
                
                eachFace = annotatedFrame[int(top):int(bottom), int(left):int(right), :]
                
                blurredEachFace = cv2.GaussianBlur(eachFace, (99, 99), 30)
                
                annotatedFrame[int(top):int(bottom), int(left):int(right), :] = blurredEachFace

        cvtdFrames.append(annotatedFrame)
    else:
        break
    
# 결과 비디오 생성
height, width, _ = cvtdFrames[0].shape

fourcc = cv2.VideoWriter_fourcc(*'XVID')

out = cv2.VideoWriter(PATH + fileName, fourcc, fps, (width, height))

for scene in cvtdFrames:
    out.write(scene)

out.release()