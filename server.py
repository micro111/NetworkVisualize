import sys
import ctypes
import time
import threading
from flask import Flask, render_template, send_from_directory,jsonify,request
from flask_socketio import SocketIO
from flask_cors import CORS
from capture import PacketAnalyzer



app = Flask(__name__, template_folder="./app/dist")
CORS(app)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

connected_clients = set()  

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/<path:filename>', methods=['GET'])
def resource(filename):
    return send_from_directory("./app/dist", filename)

@app.route('/assets/<path:filename>', methods=['GET'])
def assets_resource(filename):
    return send_from_directory("./app/dist/assets", filename)

@socketio.on('connect')
def handle_connect():
    client_id = request.sid  # クライアントのセッションIDを取得
    print(f"Client connected: {client_id}")
    connected_clients.add(client_id)

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid  # クライアントのセッションIDを取得
    print(f"Client disconnected: {client_id}")
    connected_clients.remove(client_id)

@socketio.on('message')
def handle_message(msg):
    print(f"Received message: {msg}")
    socketio.emit('message', msg)  # すべてのクライアントにメッセージをブロードキャスト


def is_admin():
    """現在のプロセスが管理者権限で実行されているか確認する関数"""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

def process_data():
    analyzer = PacketAnalyzer()
    tshark_thread = threading.Thread(target=analyzer.run_tshark)
    tshark_thread.daemon = True
    tshark_thread.start()

    ipaddr_sender = ""
    ipaddr_reciver = ""
    wait_time = 0
    while True:
        if not analyzer.data_queue.empty():
            wait_time += 100
            data = analyzer.data_queue.get()
            data["delay"] = wait_time
            if data["kinds"] == "Sender":
                if data["IPaddr"] == "91.109.182.3":
                    print("Sender")
                if not ipaddr_sender == data["IPaddr"]: 
                    ipaddr_sender = data["IPaddr"]
                    socketio.emit('message', data)
            else:
                if not ipaddr_reciver == data["IPaddr"]: 
                    ipaddr_reciver = data["IPaddr"]
                    socketio.emit('message', data) 
        else:
            time.sleep(0.1)
            wait_time = 0


if __name__ == "__main__":
    try:
        if is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            data_thread = threading.Thread(target=process_data)
            data_thread.daemon=True
            data_thread.start()
            try:
                socketio.run(app, host='0.0.0.0', port=8080)
                

            except Exception as e:
                print(f"An error occurred: {e}")


    except KeyboardInterrupt:
        print("GoodBye")