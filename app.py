import eventlet
eventlet.monkey_patch()
from flask import Flask, request, render_template, jsonify, session,url_for
import uuid
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json

from python_code.agents import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

users_agent = {}
def get_user_agent(user_id):
    print('get_agent')
    if user_id not in users_agent:
        users_agent[user_id] = aiagent('test')
        users_agent[user_id].sid = user_id
        users_agent[user_id].socketio = socketio
    return users_agent[user_id]


@app.route('/')
def index():
    print('333')
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    print(users_agent)
    return render_template('chat.html')



@socketio.on('message')
def send_message(user_message):
    def emit_message(response_message):
        with app.app_context():
            message = {"type": "response", "content": response_message}
        return message
    
    def process_message(user_message,user_id):
        print('!',user_id)
        current_agent = get_user_agent(user_id)
        response_message = current_agent.chat(user_message)
        if response_message !=None:
            message =  emit_message(response_message)
            socketio.emit('new_message', message)
        return response_message,user_id
    
    def handle_response(future):
        response_message,user_id = future.wait()

    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id

    pool = eventlet.GreenPool()
    future = pool.spawn(process_message, user_message, user_id)
    future.link(handle_response)

    @socketio.on('heartbeat')
    def handle_heartbeat(data):
        # print('Heartbeat received')
        pass

if __name__ == '__main__':
    print('111')

    socketio.run(app, host='127.0.0.1', port=5005, debug=False)

    print('222')
    # app.run(debug=True,port =5000)



