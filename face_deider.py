import os
import sys
import cv2
from ultralytics import YOLO
import math
import torch
import boto3

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

PATH      = '/root/face_deider/work_bench/'

ratioX = (float(leftTopX) + float(rightBottomX)) / 2
ratioY = (float(leftTopY) + float(rightBottomY)) / 2

init         = True

path         = PATH + fileName

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
    
    if init:
        init = False
        pos_x = len(frame[0]) * ratioX
        pos_y = len(frame) * ratioY
    
    if success:
        frameNum += 1
        origFrames.append(frame)
        results = preprocessingModel.track(frame, persist=True)
        
        if frameNum == selectedFrameNum:
            boxes = results[0].boxes.xywh.cpu()
            trackIDs = results[0].boxes.id.int().cpu().tolist()
            
            for box, trackID in zip(boxes, trackIDs):
                x, y, _, _ = box
                distance = math.sqrt((pos_x - x)**2 + (pos_y - y)**2)

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

out = cv2.VideoWriter(PATH + fileName, fourcc, fps, (width, height))

for scene in cvtdFrames:
    out.write(scene)

out.release()

# S3 업로드
BUCKET = 'deider-bucket'
auth_file = open('/root/face_deider/auth.txt', 'r')
auth = auth_file.readlines()

access_key_id = auth[0]
secret_access_key = auth[1]

s3 = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
response = s3.upload_file(PATH+fileName, BUCKET, 'videos/' + fileName)

if response:
    try:
        os.remove(PATH+fileName)
    except OSError as e:
        pass
    presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': 'videos/' + fileName}, ExpiresIn=300)
    print(presigned_url)