import json
from flask import Flask, render_template, send_from_directory
from flask_sockets import Sockets
from database import SQLiteDB

app = Flask(__name__, template_folder="./app/dist")
sockets = Sockets(app)

connected_clients = []

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/<path:filename>', methods=['GET'])
def resource(filename):
    return send_from_directory("./app/dist", filename)

@app.route('/assets/<path:filename>', methods=['GET'])
def assets_resource(filename):
    return send_from_directory("./app/dist/assets", filename)

@app.route('/send')
def send_message():
    data = {
        "message": "Hello from server",
        "info": "This is a broadcast message"
    }
    json_data = json.dumps(data)
    
    # すべての接続されているクライアントにメッセージを送信
    for ws in connected_clients:
        if not ws.closed:
            ws.send(json_data)
    
    return jsonify({"status": "Message sent"})


@sockets.route('/get_ip')
def get_ip_json(ws):
    # 新しく接続されたクライアントをリストに追加
    connected_clients.append(ws)
    
    while not ws.closed:
        message = ws.receive()
        ws.send(message)

    # クライアントが切断されたらリストから削除
    connected_clients.remove(ws)


def is_admin():
    """現在のプロセスが管理者権限で実行されているか確認する関数"""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


if __name__ == "__main__":
    try:
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            app.run(host="0.0.0.0", port=80, debug=True)
    except KeyboardInterrupt:
        db.close()