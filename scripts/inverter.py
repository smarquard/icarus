#! /usr/bin/python3
import threading
import time
import datetime
import os
import sys
import re
import json
import urllib3
import base64

import solar_config

import http.server
from http.server import HTTPServer

httpPool = urllib3.PoolManager()

sys.stderr = open('/data/log/powerserver_err.log', 'w')

# Values we expect to read
inverter_w = -1

def fetch_inverter_power():
    try:
        response = httpPool.request('GET', solar_config.solis_url, headers = auth_headers, timeout = 10)
        status_page = response.data.decode('UTF-8')
        solis_power_re = re.compile('webdata_now_p\s=\s"([0-9]+)";');
        m = solis_power_re.search(status_page)
        if m:
            power = m.group(1)
            return int(power);
        else:
            sys.stderr.write("Error matching regex in response page:\n" + status_page);
            return -1;

    except Exception as e:
        return -2;

    # Shouldn't reach here
    return -3;

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):

    log_file = open('/data/log/powerserver_access.log', 'w')

    def do_GET(self):

            #print("path: " + self.path)

            if (self.path.endswith("below_horizon")) or (self.path.endswith("favicon.ico")):
                inverter_w = 0
            else:
                # Fetch from inverter
                inverter_w = fetch_inverter_power()

            now = time.time()

            if (inverter_w >= 0):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write(json.dumps({"now" : now, "inverter" : inverter_w}).encode('UTF-8'))
            else:
                self.send_response(503)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("Error fetching response from inverter".encode())

    def log_message(self, format, *args):
        self.log_file.write("%s - - [%s] %s\n" %
                            (self.client_address[0],
                             self.log_date_time_string(),
                             format%args))
        self.log_file.flush()

server = HTTPServer(('', 8081), MyRequestHandler)

authstr = solar_config.solis_username + ":" + solar_config.solis_password
auth_headers = {"Authorization": f"Basic {base64.b64encode(authstr.encode()).decode()}"}

thread = threading.Thread(target = server.serve_forever)
thread.daemon = True

try:
    thread.start()
except KeyboardInterrupt:
    server.shutdown()
    sys.exit(0)

# print('Server started on port 8081')

while True:
    time.sleep(1)

