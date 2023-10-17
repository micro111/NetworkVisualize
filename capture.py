import os
import time
import subprocess
import threading
from database import SQLiteDB
from util import *

def void(data):
    print(data)
    
class PacketAnalyzer:
    def __init__(self, log_dir="log/", callback=void):
        self.db_lock = threading.Lock()
        self.TSHARK_PATH = 'C:\\Program Files\\Wireshark\\tshark.exe'
        self.LOG_DIR = log_dir
        self.SEEN_SRC_IPS_FILE = "seen_src_ips.txt"
        self.SEEN_DST_IPS_FILE = "seen_dst_ips.txt"

        self.db = SQLiteDB(check_same_thread=False)
        self.src_table_name = "ip_list_src"
        self.dst_table_name = "ip_list_dst"
        self.create_database()

        self.bl_list = BlacklistChecker()
        self.callback = callback

        # db.insert_data("users", {"name": "Taro", "age": 30})
        # print(db.fetch_all("users"))
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)

    def create_database(self):
        columns = [
            "IPaddr TEXT",
            "TALO INTEGER",
            "FIRE INTEGER",
            "ISO TEXT",
            "Country TEXT",
            "City TEXT",
            "Timestamp INTEGER "
        ]
        self.db.create_table(self.src_table_name,columns)
        self.db.create_table(self.dst_table_name,columns)

    def insert_database(self,table_name,columns):
        with self.db_lock: 
            self.db.insert_data(table_name,columns)

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

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, text=True)
        while True:
            line = process.stdout.readline()
            if line.strip():
                srcs, dsts = line.strip().split()
                for src,dst in zip(srcs.split(","),dsts.split(",")):
                    if src not in seen_src_ips:
                        print(f"New src IP detected: {src}")
                        seen_src_ips.add(src)
                        self.save_seen_ips(seen_src_ips, self.SEEN_SRC_IPS_FILE)
                    if dst not in seen_dst_ips:
                        print(f"New dst IP detected: {dst}")
                        seen_dst_ips.add(dst)
                        self.save_seen_ips(seen_dst_ips, self.SEEN_DST_IPS_FILE)
                    thread1 = threading.Thread(target=self.insert_src_IP, args=(src,))
                    thread2 = threading.Thread(target=self.insert_dst_IP, args=(dst,))
                    thread1.start()
                    thread2.start()

    def insert_src_IP(self, src):
        check_result = self.bl_list.check_ip_in_downloaded_blacklist(src)
        region_result = get_country(src)

        columns = {
            "IPaddr": src,
            "TALO": check_result["TALO"] if "TALO" in check_result else 2 ,
            "FIRE": check_result["FIRE"] if "TALO" in check_result else 2 ,
            "ISO": region_result["ISO"],
            "Country": region_result["Country"],
            "City": region_result["City"],
            "timestamp": int(time.time())  # 挿入時間
        }
        self.insert_database(self.src_table_name,columns)
        pass


    def insert_dst_IP(self, dst):
        check_result = self.bl_list.check_ip_in_downloaded_blacklist(dst)
        region_result = get_country(dst)

        columns = {
            "IPaddr": dst,
            "TALO": check_result["TALO"] if "TALO" in check_result else 2 ,
            "FIRE": check_result["FIRE"] if "TALO" in check_result else 2 ,
            "ISO": region_result["ISO"],
            "Country": region_result["Country"],
            "City": region_result["City"],
            "timestamp": int(time.time())  # 挿入時間
        }
        self.insert_database(self.dst_table_name,columns)
        pass

if __name__ == "__main__":
    analyzer = PacketAnalyzer()
    analyzer.run_tshark()