import os
import time
import queue
import subprocess
import threading
import logging
from database import SQLiteDB
from util import *
from protocol_map import ip_proto_to_name

def void(data):
    print(data)
    
class PacketAnalyzer:
    def __init__(self, log_dir="log/", callback=void):
        self.TSHARK_PATH = 'C:\\Program Files\\Wireshark\\tshark.exe'
        self.LOG_DIR = log_dir
        self.SEEN_SRC_IPS_FILE = "seen_src_ips.txt"
        self.SEEN_DST_IPS_FILE = "seen_dst_ips.txt"

        self.data_queue = queue.Queue()
        
        # self.db = SQLiteDB(database_name="test",in_memory=False,check_same_thread=False)
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
            "App TEXT",
            "Prot TEXT",
            "Timestamp INTEGER "
        ]
        self.db.create_table(self.src_table_name,columns)
        self.db.create_table(self.dst_table_name,columns)

    def insert_database(self,table_name,columns):
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

    def get_global_ip(self):
        try:
            response = requests.get("https://api.ipify.org")
            return response.text
        except requests.RequestException:
            return ""
        


    def run_tshark(self):
        seen_src_ips = self.load_seen_ips(self.SEEN_SRC_IPS_FILE)
        seen_dst_ips = self.load_seen_ips(self.SEEN_DST_IPS_FILE)
        current_ip = self.get_global_ip()
        
        cmd = [
            self.TSHARK_PATH,
            '-i', 'BroadCast',
            '-T', 'fields',
            '-e', 'ip.proto',
            '-e', 'dns',
            '-e', 'ftp',
            '-e', 'http',
            '-e', 'telnet',
            '-e', 'ssh',
            '-e', 'quic',
            '-e', 'rdp',
            '-e', 'ip.dst',
            '-e', 'ip.src',
            '-e', 'ipv6.dst',
            '-e', 'ipv6.src',
            '-E', 'separator=|' ,
            '-b', 'duration:3600',  # 1時間ごとにローテーション
            '-b', 'files:24',       # 最大24ファイル保存
            '-w', os.path.join(self.LOG_DIR, 'capture.pcap')
        ]
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, text=True)
            while True:
                line = process.stdout.readline()
                if line.replace("|","").strip():
                    data = line.strip().split("|")

                    if data[-1]: #ipv6をさぼった
                        continue

                    num_prot = ip_proto_to_name(data[0])
                    app_prot = [value for value in data[1:-4] if value != ""]
                    if len(app_prot) != 1:
                        app_prot = num_prot
                    else:
                       app_prot = app_prot[0].replace("\"","")

                    dsts, srcs = data[-4:-2]
                    for src,dst in zip(srcs.split(","),dsts.split(",")):
                        if current_ip not in src:
                            thread1 = threading.Thread(target=self.insert_src_IP, args=(src,app_prot,num_prot))
                            thread1.daemon = True
                            thread1.start()
                            if src not in seen_src_ips:
                                print(f"New src IP detected: {src}")
                                seen_src_ips.add(src)
                                self.save_seen_ips(seen_src_ips, self.SEEN_SRC_IPS_FILE)
                                
                        elif current_ip not in dst:
                            thread2 = threading.Thread(target=self.insert_dst_IP, args=(dst,app_prot,num_prot))
                            thread2.daemon = True 
                            thread2.start()
                            if dst not in seen_dst_ips:
                                print(f"New dst IP detected: {dst}")
                                seen_dst_ips.add(dst)
                                self.save_seen_ips(seen_dst_ips, self.SEEN_DST_IPS_FILE)

        except Exception as e:
            logging.error(f"An error occurred: {e}")


    def insert_src_IP(self, src, app_prot, num_prot):
        check_result = self.bl_list.check_ip_in_downloaded_blacklist(src)
        region_result = get_country(src)

        columns = {
            "IPaddr": src,
            "TALO": check_result["TALO"] if "TALO" in check_result else 2 ,
            "FIRE": check_result["FIRE"] if "TALO" in check_result else 2 ,
            "ISO": region_result["ISO"],
            "Country": region_result["Country"],
            "City": region_result["City"],
            "App":app_prot,
            "Prot":num_prot,
            "timestamp": int(time.time())  # 挿入時間
        }

        self.insert_database(self.src_table_name,columns)
        columns["kinds"] = "src"
        columns["lon"] = region_result["lon"]
        columns["lat"] = region_result["lat"]
        
        self.data_queue.put(columns)


    def insert_dst_IP(self, dst, app_prot, num_prot):
        check_result = self.bl_list.check_ip_in_downloaded_blacklist(dst)
        region_result = get_country(dst)

        columns = {
            "IPaddr": dst,
            "TALO": check_result["TALO"] if "TALO" in check_result else 2 ,
            "FIRE": check_result["FIRE"] if "TALO" in check_result else 2 ,
            "ISO": region_result["ISO"],
            "Country": region_result["Country"],
            "City": region_result["City"],
            "App":app_prot,
            "Prot":num_prot,
            "timestamp": int(time.time())  # 挿入時間
        }

        self.insert_database(self.dst_table_name,columns)
        columns["kinds"] = "dst"
        columns["lon"] = region_result["lon"]
        columns["lat"] = region_result["lat"]
        
        self.data_queue.put(columns)

if __name__ == "__main__":
    analyzer = PacketAnalyzer()
    try:
        analyzer.run_tshark()
    except KeyboardInterrupt:
        print("GoodBye")


# columns = {
#             "IPaddr": "0.0.0.0",
#             "TALO": 2 ,
#             "FIRE": 2 ,
#             "ISO": "None",
#             "Country": "None",
#             "City": "None",
#             "timestamp": 100  # 挿入時間
#         }