# author: dchep001@fiu.edu
# id: 6152714
# 3/28/2020
# CNT4713 U01 1201  
# 
# "server" side script for
# streaming webcam video feed to heroku
# "server" in the sense that it provides a video stream
# in response to a client's request
# heroku web app acting as "client" 
# only in this specific case

# ----------

from time import time
import cv2
import io
import socket
import struct
import pickle
import zlib

import requests
# ----------

HOST = socket.gethostbyname(socket.gethostname()) # get host name     
PORT = 5055
socket.setdefaulttimeout(70)

DEST_URL = "https://videostreamers5.herokuapp.com/http_stream"

wcam = cv2.VideoCapture(0)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]


def generate_video():
	if wcam.isOpened():
		rec, frame = wcam.read()
	else: rec = False
	
	while True:
		rec, fr = wcam.read()
		result, frame = cv2.imencode('.jpg', fr, encode_param)
		# data = pickle.dumps(frame, 0)
		# img_str = cv2.imencode('.jpg', frame)[1].tostring()
		#----data_encode = np.array(frame)
		# data = {'frame' : frame.tobytes()}
		data = frame.tobytes()
		resp = requests.post(DEST_URL, data=data)
		key = cv2.waitKey(40)


# ---------------------------
# old version - streams only within LAN
def vid_server():
	socket.setdefaulttimeout(60)
	serv_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	serv_socket.bind((HOST, PORT))
	serv_socket.listen(10) 
	print("serving @: " + str(serv_socket))	
	wcam = cv2.VideoCapture(0)
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
	if wcam.isOpened():
		rec, frame = wcam.read()
	else: rec = False
	
	# accept a connection
	conn, addr = serv_socket.accept()
	data = conn.recv(4096)
	print("connection accepted")
	while True:
		rec, frame = wcam.read()
		result, frame = cv2.imencode('.jpg', frame, encode_param)
		data = pickle.dumps(frame, 0)
		size = len(data)
		# send over socket ---------------------------------
		conn.sendall(struct.pack(">L", size)+data) # sends the packet with encoded frame --> to socket
		key = cv2.waitKey(40)
        


if __name__ == "__main__":  
    generate_video()
	#pass

"""
while True:
		try:
			vid_server()
		except:
			print("server disconnected;\n\'r\' to reconnect\nany other to quit")
			response = input("-> ")
			if response == 'r': continue
			else: break
"""
# end of program