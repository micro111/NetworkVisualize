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

def color_selector(prot):
    if prot =="TCP":
        return "green"
    elif prot == "RDP":
        return "orange"
    elif prot == "L2TP":
        return "purple"
    elif prot == "UDP":
        return "blue"
    elif prot == "http":
        return "lightskyblue"
    elif "Domain Name System" in prot:
        return "yellow"
    elif prot == "ESP":
        return "deeppink"
    return "white"

class PacketAnalyzer:
    def __init__(self, log_dir="log/", callback=void):
        self.TSHARK_PATH = 'C:\\Program Files\\Wireshark\\tshark.exe'
        self.LOG_DIR = log_dir
        self.sender_ips_FILE = "sender_ips.txt"
        self.reciver_ips_FILE = "reciver_ips.txt"
        self.data_queue = queue.Queue()

        self.db_used = False
         
        # self.db = SQLiteDB(database_name="test",in_memory=False,check_same_thread=False)
        self.db = SQLiteDB(check_same_thread=False) if self.db_used else None
        self.src_table_name = "ip_list_src"
        self.dst_table_name = "ip_list_dst"
        self.create_database()

        self.bl_list = BlacklistChecker()
        self.callback = callback

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
        if self.db_used:
            self.db.create_table(self.src_table_name,columns)
            self.db.create_table(self.dst_table_name,columns)

    def insert_database(self,table_name,columns):
        if self.db_used:
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
        sender_ips = self.load_seen_ips(self.sender_ips_FILE)
        reciver_ips = self.load_seen_ips(self.reciver_ips_FILE)
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
                        if current_ip in src: #送信
                            thread = threading.Thread(target=self.insert_sender_IP, args=(dst,app_prot,num_prot))
                            thread.daemon = True 
                            thread.start()
                            if dst not in reciver_ips:
                                print(f"New reciver IP detected: {dst}")
                                reciver_ips.add(dst)
                                self.save_seen_ips(reciver_ips, self.reciver_ips_FILE)    
                                
                        elif current_ip in dst: #受信
                            thread = threading.Thread(target=self.insert_reciver_IP, args=(src,app_prot,num_prot))
                            thread.daemon = True
                            thread.start()
                            if src not in sender_ips:
                                print(f"New Sender IP detected: {src}")
                                sender_ips.add(src)
                                self.save_seen_ips(sender_ips, self.sender_ips_FILE)
                                
                                


        except Exception as e:
            logging.error(f"An error occurred: {e}")


    def insert_reciver_IP(self, src, app_prot, num_prot):
        check_result = self.bl_list.check_ip_in_downloaded_blacklist(src)
        region_result = get_country(src)
        t = int(time.time())
        columns = {
            "IPaddr": src,
            "TALO": check_result["TALO"] if "TALO" in check_result else 2 ,
            "FIRE": check_result["FIRE"] if "TALO" in check_result else 2 ,
            "ISO": region_result["ISO"],
            "Country": region_result["Country"],
            "City": region_result["City"],
            "App":app_prot,
            "Prot":num_prot,
            "timestamp": t  # 挿入時間
        }

        self.insert_database(self.src_table_name,columns)
        columns["kinds"] = "Reciver"
        columns["lon"] = region_result["lon"]
        columns["lat"] = region_result["lat"]
        columns["color"] = color_selector(columns["App"])
        self.data_queue.put(columns)


    def insert_sender_IP(self, dst, app_prot, num_prot):
        check_result = self.bl_list.check_ip_in_downloaded_blacklist(dst)
        region_result = get_country(dst)
        t = int(time.time())
        columns = {
            "IPaddr": dst,
            "TALO": check_result["TALO"] if "TALO" in check_result else 2 ,
            "FIRE": check_result["FIRE"] if "TALO" in check_result else 2 ,
            "ISO": region_result["ISO"],
            "Country": region_result["Country"],
            "City": region_result["City"],
            "App":app_prot,
            "Prot":num_prot,
            "timestamp": t  # 挿入時間
        }

        self.insert_database(self.dst_table_name,columns)
        columns["kinds"] = "Sender"
        columns["lon"] = region_result["lon"]
        columns["lat"] = region_result["lat"]
        columns["color"] = color_selector(columns["App"])
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