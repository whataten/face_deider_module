# Face Deider

+ **Face Deider is face de-idenfication service module.**
+ **This repository can be used to create docker files.**

### Contact

**tiktaalik135462@gmail.com**  

### History

**23/08/24** de-identificate all faces on loaded video  
**23/09/05** de-identificate all faces without selected face on loaded video  
**23/11/08** de-identificate all faces without selected face in selected frame on loaded video  
**23/11/08** transfer to this repository  
**23/11/13** add html based web service

***

### Web Server

+ [face-deid-service](http://13.209.16.244:8080)  

*settings*  
``` shell
apt install nodejs
apt install npm
npm install -g npm@latest
npm init
npm install -g express --save
npm install -g multer --save
npm install -g child_process --save
pip install boto3
curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install uuid
```

### Docker

+ [Image](https://hub.docker.com/repository/docker/whataten/face_deider/general)  

*In running docker container, It **should** be mounted correct directories*  
**/root/face_deider/in** : location that original videos uploaded at  
**/root/face_deider/out** : location that converted videos saved at  

```shell
python face_deider video_file_name frame left_top_pos_x left_top_pos_y right_ bottom_pos_x right_ bottom_ pos_y  
```

*settings*  
base docker image : [ubuntu:20.04](https://hub.docker.com/_/ubuntu)  

``` shell
apt install software-properties-common  
add-apt-repository ppa:deadsnakes/ppa  
apt install python3.10  
apt install python3-pip  
pip3 install opencv-python==4.8.1.78  
pip3 install ultralytics==8.0.207  
```

### Specifics

ubuntu==20.04  
python==3.10  
opencv-python==4.8.1.78  
ultralytics==8.0.207  
yolo==8  
