import sys
import cv2
from ultralytics import YOLO
import math
import torch

# 인수 전달
fileName            = sys.argv[1]
selectedFrameNum    = sys.argv[2]
leftTopX            = sys.argv[3]
leftTopY            = sys.argv[4]
rightBottomX        = sys.argv[5]
rightBottomY        = sys.argv[6]

# 변수 선언
preprocessingModel  = YOLO('/root/face_deider/model_weight.pt')
postprocessingModel = YOLO('/root/face_deider/model_weight.pt')

IN_PATH      = '/root/face_deider/in/'
OUT_PATH     = '/root/face_deider/out/'

selectedPosX = int((leftTopX + rightBottomX) / 2)
selectedPosY = int((leftTopY + rightBottomY) / 2)

path         = IN_PATH + fileName

cap          = cv2.VideoCapture(path)
fps          = cap.get(cv2.CAP_PROP_FPS)

targetID     = None
frameNum     = 0

bowl         = [-1, math.inf]

cvtdFrames   = []
origFrames   = []

# Target ID 획득
while cap.isOpened():
    success, frame = cap.read()
    
    if success:
        frameNum += 1
        origFrames.append(frame)
        results = preprocessingModel.track(frame, persist=True)
        
        if frameNum == selectedFrameNum:
            boxes = results[0].boxes.xywh.cpu()
            trackIDs = results[0].boxes.id.int().cpu().tolist()
            
            for box, trackID in zip(boxes, trackIDs):
                x, y, _, _ = box
                    
                distance = math.sqrt((selectedPosX - x)**2 + (selectedPosY - y)**2)

                if distance < bowl[1]:
                    bowl[0] = trackID
                    bowl[1] = distance
                
            targetID = bowl[0]
            bowl = [-1, math.inf]
    else:
        break

cap.release()

# 비식별화
for frame in origFrames:
    results = postprocessingModel.track(frame, persist=True)
    annotatedFrame = results[0].orig_img
    isDetected = torch.all(results[0].boxes.cls == 0).item()
    
    # 비식별화할 대상이 식별된 경우
    if isDetected:
        boxes = results[0].boxes.xywh.cpu()
        
        # 물체가 식별된 첫 프레임 : 바운딩 박스는 존재하나 아이디가 존재하지 않는 경우
        if results[0].boxes.id is None:
            for box in boxes:
                x, y, w, h = box
                
                left = x - (w/2)
                top = y - (h/2)
                right = x + (w/2)
                bottom = y + (h/2)
                
                eachFace = annotatedFrame[int(top):int(bottom), int(left):int(right), :]
                
                blurredEachFace = cv2.GaussianBlur(eachFace, (99, 99), 30)
                
                annotatedFrame[int(top):int(bottom), int(left):int(right), :] = blurredEachFace
        
        # 그 외 : 바운딩 박스와 아이디가 모두 존재하는 경우
        else:
            trackIDs = results[0].boxes.id.int().cpu().tolist()
                
            for box, trackID in zip(boxes, trackIDs):
                if trackID != targetID:
                    x, y, w, h = box
                    
                    left = x - (w/2)
                    top = y - (h/2)
                    right = x + (w/2)
                    bottom = y + (h/2)
                    
                    eachFace = annotatedFrame[int(top):int(bottom), int(left):int(right), :]
                    
                    blurredEachFace = cv2.GaussianBlur(eachFace, (99, 99), 30)
                    
                    annotatedFrame[int(top):int(bottom), int(left):int(right), :] = blurredEachFace

    # 비식별화가 필요없는 프레임과 비식별화가 끝난 프레임을 영상 순서대로 추가
    cvtdFrames.append(annotatedFrame)
    
# 결과 비디오 생성
height, width, _ = cvtdFrames[0].shape

fourcc = cv2.VideoWriter_fourcc(*'XVID')

out = cv2.VideoWriter(OUT_PATH + fileName, fourcc, fps, (width, height))

for scene in cvtdFrames:
    out.write(scene)

out.release()