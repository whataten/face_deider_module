# Face Deider

+ ***Face Deider is face de-idenfication service module.***
+ ***This repository made for creating docker files.***

***

### Contact

**tiktaalik135462@gmail.com**  

### History

**23/08/24** de-identificate all faces on loaded video  
**23/09/05** de-identificate all faces without selected face on loaded video  
**23/11/08** de-identificate all faces without selected face in selected frame on loaded video  
**23/11/08** transfer to this repository

***

### Docker
*In running docker container, It **should** be mounted correct directories*  
**/root/face_deider/in** : location that original videos uploaded at  
**/root/face_deider/out** : location that converted videos saved at  

run command with parameter - `video file name`, `frame`, `left top pos x`, `left top pos y`, `right bottom pos x`, `right bottom pos y`  

*settings*  
base docker image : [ubuntu:20.04](https://hub.docker.com/_/ubuntu)  
apt install software-properties-common  
add-apt-repository ppa:deadsnakes/ppa  
apt install python3.10  
apt install python3-pip  
pip3 install opencv-python==4.8.1.78  
pip3 install ultralytics==8.0.207  

### Specifics

ubuntu==20.04  
python==3.10  
opencv-python==4.8.1.78  
ultralytics==8.0.207  
yolo==8
