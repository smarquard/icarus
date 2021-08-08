#! /usr/bin/python3

import threading
import time
import datetime
import os
import sys
import re
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import base64

import solar_config

import http.server
from http.server import HTTPServer

# sys.stderr = open('/data/log/powerserver_err.log', 'w')

# Values we expect to read
inverter_w = -1
grid_w = -1

def fetch_inverter_power():
    # First check if there's been a reading recently
    with open('/usr/share/nginx/www/staticdata/inverter.txt', 'r') as file:
        last_power = file.read().replace('\n', '')

    if (last_power == '0'):
        return 0;

    request = urllib.request.Request(solar_config.solis_url)
    authdetails = solar_config.solis_username + ':' + solar_config.solis_password
    base64string = base64.b64encode(authdetails.encode())
    request.add_header("Authorization", "Basic %s" % base64string)
    response = urllib.request.urlopen(request, timeout = 10)
    status_page = response.read().decode('UTF-8')

    solis_power_re = re.compile('webdata_now_p\s=\s"([0-9]+)";');
    m = solis_power_re.search(status_page)
    if m:
        power = m.group(1)
        return int(power);

    return 0;

def fetch_grid_power():
    response = urllib.request.urlopen(solar_config.efergy_url, timeout = 15)
    efergy_data = json.loads(response.read().decode('UTF-8'))
    for key, value in list(efergy_data[0]["data"][0].items()):
       grid_w = value
    return grid_w

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):

    log_file = open('/data/log/powerserver_access.log', 'w')

    def do_GET(self):
            # Refresh if needed (for now, fetch anyway)

            inverter_w = fetch_inverter_power()
            grid_w = fetch_grid_power()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers()
            self.wfile.write(json.dumps({"inverter" : inverter_w, "grid" : grid_w}).encode('UTF-8'))

    def log_message(self, format, *args):
        self.log_file.write("%s - - [%s] %s\n" %
                            (self.client_address[0],
                             self.log_date_time_string(),
                             format%args))
        self.log_file.flush()

server = HTTPServer(('', 8081), MyRequestHandler)

thread = threading.Thread(target = server.serve_forever)
thread.daemon = True

try:
    thread.start()
except KeyboardInterrupt:
    server.shutdown()
    sys.exit(0)

print('Server started on port 8081')

while True:
    time.sleep(60)

