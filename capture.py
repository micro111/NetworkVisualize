import os
import subprocess
from database import SQLiteDB
class PacketAnalyzer:
    def __init__(self, log_dir="log/"):
        self.TSHARK_PATH = 'C:\\Program Files\\Wireshark\\tshark.exe'
        self.LOG_DIR = log_dir
        self.SEEN_SRC_IPS_FILE = "seen_src_ips.txt"
        self.SEEN_DST_IPS_FILE = "seen_dst_ips.txt"
        self.db = SQLiteDB()

        # db.insert_data("users", {"name": "Taro", "age": 30})
        # print(db.fetch_all("users"))
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)

    def load_seen_ips(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return set(f.read().splitlines())
        return set()

    def save_seen_ips(self, ip_set, filename):
        with open(filename, 'w') as f:
            for ip in ip_set:
                f.write(f"{ip}\n")

    def run_tshark(self):
        seen_src_ips = self.load_seen_ips(self.SEEN_SRC_IPS_FILE)
        seen_dst_ips = self.load_seen_ips(self.SEEN_DST_IPS_FILE)
        
        cmd = [
            self.TSHARK_PATH,
            '-i', 'BroadCast',
            '-T', 'fields',
            '-e', 'ip.dst',
            '-e', 'ip.src',
            '-b', 'duration:3600',  # 1時間ごとにローテーション
            '-b', 'files:24',       # 最大24ファイル保存
            '-w', os.path.join(self.LOG_DIR, 'capture.pcap')
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            line = process.stdout.readline()
            if line.strip():
                src, dst = line.strip().split()
                if src not in seen_src_ips:
                    print(f"New src IP detected: {src}")
                    seen_src_ips.add(src)
                    self.save_seen_ips(seen_src_ips, self.SEEN_SRC_IPS_FILE)
                if dst not in seen_dst_ips:
                    print(f"New dst IP detected: {dst}")
                    seen_dst_ips.add(dst)
                    self.save_seen_ips(seen_dst_ips, self.SEEN_DST_IPS_FILE)

if __name__ == "__main__":
    analyzer = PacketAnalyzer()
    analyzer.run_tshark()