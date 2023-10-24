import os
import requests
from geolite2 import geolite2


TALO_URL = "https://www.talosintelligence.com/documents/ip-blacklist"
FIRE_URL = "https://iplists.firehol.org/files/firehol_level2.netset"
URL_SET = {"TALO":TALO_URL,"FIRE":FIRE_URL}
BLACKLIST_DIR = "./blacklist/"

def get_country(ip_address):
    reader = geolite2.reader()
    location = reader.get(ip_address)
    if location:
        return {        
            "ISO": location["country"]["iso_code"] if "country" in location and "iso_code" in location["country"] else "None",
            "Country": location["country"]["names"]["en"] if "country" in location and "names" in location["country"] and "en" in location["country"]["names"] else "None",
            "City": location["city"]["names"]["en"]  if "city" in location and "names" in location["city"] and "en" in location["city"]["names"] else "None",
            "lon" : location["location"]["longitude"] if "location" in location and "longitude" in location["location"] else "-1",
            "lat" : location["location"]["latitude"] if "location" in location and "latitude" in location["location"] else "-1"
            }
    else:
        return {
            "ISO":"None",
            "Country":"None",
            "City":"None",
            "lon":"-1",
            "lat":"-1"
        }
    # loc["continent"]["names"]["en"]


### This method is VeryVeryVery Slowly... :( Never don't Use it :(
# import socket
# def get_domain_name(ip_address):
#     try:
#         domain_name = socket.gethostbyaddr(ip_address)
#         return domain_name[0]
#     except socket.herror:
#         return None



class BlacklistChecker:
    def __init__(self):
        self.list_set = {}
        # self.download_blacklist_file()
        self.ip_read()

    def download_blacklist_file(self, filename="ip_blacklist"):
        result = []

        if not os.path.exists(BLACKLIST_DIR):
            os.makedirs(BLACKLIST_DIR)

        for name, url in URL_SET.items():
            response = requests.get(url)
            if response.status_code == 200:
                with open(BLACKLIST_DIR + filename + "_" + name + ".txt", 'wb') as f:
                    f.write(response.content)
                result.append(True)
            else:
                print("Failed to download the file :" + name)
                result.append(False)
        return result

    def ip_read(self, filename="ip_blacklist"):
        for name, _ in URL_SET.items():
            try:
                with open(BLACKLIST_DIR + filename + "_" + name + ".txt", 'r') as f:
                    self.list_set[name] = set(f.read().splitlines())
            except FileNotFoundError:
                print("File not found :" + name)
                continue

    def check_ip_in_downloaded_blacklist(self, target_ip):
        result = {}

        for name, ip_set in self.list_set.items():
            if target_ip in ip_set:
                result[name] = 1
            else:
                result[name] = 0
        return result
    

if __name__ == "__main__":
    checker = BlacklistChecker()
    checker.download_blacklist_file()
    checker.ip_read()
    result = checker.check_ip_in_downloaded_blacklist("192.168.1.1")