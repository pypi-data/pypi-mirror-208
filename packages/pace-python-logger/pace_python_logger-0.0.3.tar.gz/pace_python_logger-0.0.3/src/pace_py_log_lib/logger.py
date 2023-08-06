from datetime import datetime
import requests
import json
from websocket import create_connection
from urllib.parse import urlparse

__server__hostname = None
__log_web_socket = None
__session = None
__request = None
__experience = None
__start_time = None

def set_socket_url(starter_url):
    global __log_web_socket
    global __server__hostname

    socket_url_rel = requests.get(starter_url).text

    parsed_uri = urlparse(starter_url)

    __server__hostname = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
    socket_uri = f"wss://{parsed_uri.netloc}{socket_url_rel}"

    print(f"[INFO] Got a websocker url {socket_uri}")

    __log_web_socket = create_connection(socket_uri)

def close_open_connection():
    if __log_web_socket:
        __log_web_socket.close()

def peek_last_test_url():
    global __server__hostname
    return requests.get(f"{__server__hostname}/test").json()

def log_raw_message(message):
    __log_web_socket.send(message)


def start_event_marker(session,request,experience):
    global __session, __request, __experience, __start_time
    __session = session
    __request = request
    __experience = experience
    __start_time = datetime.now()

def log_final_snippet(snippet):

    if(not __start_time):
        raise ValueError("Start the logging before finalizing")

    end_time = datetime.now()
    delta = end_time - __start_time
    duration = delta.total_seconds()
    msg_obj = {"request_id":__request,
               "session_id":__session,
               "experience_id":__experience,
               "snippet":snippet,
               "duration":duration,
               "final":True}
    
    log_raw_message(json.dumps(msg_obj))