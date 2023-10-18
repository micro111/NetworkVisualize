import sys
import json
import ctypes
import eventlet
import threading
from flask import Flask, render_template, send_from_directory,jsonify,request
from flask_socketio import SocketIO

from capture import PacketAnalyzer



app = Flask(__name__, template_folder="./app/dist")
socketio = SocketIO(app, async_mode='threading')

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

    while True:
        if not analyzer.data_queue.empty():
            received_data = analyzer.data_queue.get()
            socketio.emit('message', received_data)

if __name__ == "__main__":
    try:
        if not is_admin():
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