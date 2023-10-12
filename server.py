from flask import Flask, render_template, send_from_directory
from database import SQLiteDB

app = Flask(__name__, template_folder="./app/dist")

def is_admin():
    """現在のプロセスが管理者権限で実行されているか確認する関数"""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/<path:filename>', methods=['GET'])
def resource(filename):
    return send_from_directory("./app/dist", filename)

@app.route('/assets/<path:filename>', methods=['GET'])
def assets_resource(filename):
    return send_from_directory("./app/dist/assets", filename)


if __name__ == "__main__":
    try:
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            app.run(host="0.0.0.0", port=80, debug=True)
    except KeyboardInterrupt:
        db.close()