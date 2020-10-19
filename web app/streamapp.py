# author: dchep001@fiu.edu
# id: 6152714
# 3/28/2020
# CNT4713 U01 1201  
#
# Static and live webcam streaming
# on heroku:  https://videostreamers5.herokuapp.com/ 


from flask import Flask, render_template, Response, request, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from camera import Camera

# socket/server imports
#import os
#import sys
import cv2
import numpy as np
import time
from queue import Queue

CUSTOM_PORT = 5055

app = Flask(__name__)
auth = HTTPBasicAuth()

users = { "user1" : generate_password_hash("627pw") }

frame_queue = Queue(maxsize = 120) #max of 120 frames

# authentication
@auth.verify_password
def verify_password(uname, pword):
    if uname in users:
        return check_password_hash(users.get(uname), pword)
    return False

# home page
@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')

# generic frame generator
def generate(cam):
    while True:
        frame = cam.get_frame()
        yield(b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ------------------------------------------
# generate frames for static video streaming
# with a preset video file "train.mp4"
@app.route('/video_feed')
def video_feed():
    # video name could be parametrized but who cares
    return Response(generate(Camera("train.mp4")), mimetype='multipart/x-mixed-replace; boundary=frame')



# ------------------------------------------
# generate frames from custom server
# talks to a remote server running on some other
# machine - this version only work on LAN
'''
def generate_custom(remote_ip):
    # establish a client connection and receive frames
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((socket.gethostbyname(socket.gethostname()), CUSTOM_PORT))
    data = b""
    pay_size = struct.calcsize(">L")
    msg = "hello" # message doesn't matter, just needs a connection
    client_socket.send(msg.encode())
    while True:
        while len(data) < pay_size:
            data += client_socket.recv(4096)
        packed_size = data[:pay_size]
        data = data[pay_size:]
        msg_size = struct.unpack(">L", packed_size)[0]
        while len(data) < msg_size:
            data += client_socket.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imencode('.jpg', cv2.imdecode(frame, cv2.IMREAD_COLOR))[1].tobytes() 
        yield(b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/webc_custom')
def webc_custom():
    return Response(generate_custom(None), mimetype='multipart/x-mixed-replace; boundary=frame')

'''

# ------------------------------------------
# stream with python's requests library
@app.route('/http_stream', methods=['POST'])
def http_stream():
    if frame_queue.full():
        trash_frame = request.data
        # discard new incoming frames
    frame_queue.put(request.data)    



@app.route('/generate_http')
def generate_http():
    while True:
        #frame_array = np.fromstring(str_frame, np.uint8)
        time.sleep(0.04)
        frame = frame_queue.get()
        yield(b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/webcam_feed')
def webcam_feed():
    return Response(generate_http(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ------------------------------------------
# here the streaming page renders
# either static video file
# or live webcam feed from the client side script
# depends on the link (incoming request.args)
@app.route('/get_stream', methods=['GET'])
def get_stream():
    requested_type = request.args.get('type')
    if requested_type == "static":
        stream_type = "video_feed"
        title = "Static video file"
    else:
        stream_type = "webcam_feed"
        title = "Live webcam feed"
    return render_template("streaming.html", type=(title, stream_type))


# ------------------------------------------
# previous version of live webcam streamer
# can't work with heroku since it does not allow 
# picking ports, assigns them dynamically instead --
#
# doesn't need a camera parameter - 
#  frames come from the socket
#  received in chunks of 4096
def webcam_stream_demoted():
    '''s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(),PORT))
    s.listen(10)'''
    conn, addr = s.accept()
    data = b""
    pay_size = struct.calcsize(">L")
    while True:
        while len(data) < pay_size:
            data += conn.recv(4096)
        packed_size = data[:pay_size]
        data = data[pay_size:]
        msg_size = struct.unpack(">L", packed_size)[0]
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imencode('.jpg', cv2.imdecode(frame, cv2.IMREAD_COLOR))[1].tobytes() 
        #cv2.waitKey(40)

        # frame = cam.get_frame()
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# heroku doesn't start running here
# gunicorn launches the app
if __name__ == '__main__':
    app.run()