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

import http.server
from http.server import HTTPServer

# Read config
f = open('options.json')
config = json.load(f)
f.close()

httpPool = urllib3.PoolManager()

# Values we expect to read
inverter_w = -1

# Reset at midnight
inverter_today = 0.0

# Never reset
inverter_total = 0.0

def fetch_inverter_power():

    global inverter_w
    global inverter_today
    global inverter_total

    try:
        response = httpPool.request('GET', config['inverter'], headers = auth_headers, timeout = 10)
        status_page = response.data.decode('UTF-8')

        # Source is like this:
        #   var webdata_now_p = "1780";
        #   var webdata_today_e = "3.40";
        #   var webdata_total_e = "3063.0";

        solis_power_re = re.compile('webdata_now_p\s=\s"([0-9]+)";');
        solis_today_re = re.compile('webdata_today_e\s=\s"([0-9.]+)";');
        solis_total_re = re.compile('webdata_total_e\s=\s"([0-9.]+)";');

        m_power = solis_power_re.search(status_page)
        m_today = solis_today_re.search(status_page)
        m_total = solis_total_re.search(status_page)

        if m_power and m_today and m_total:
            inverter_w = int(m_power.group(1))
            inverter_today = float(m_today.group(1))
            inverter_total = float(m_total.group(1))
            return "active"
        else:
            # Most likely returned a status page with empty values
            return "no data"

    except Exception as e:
        return "exception: {}".format(str(e))

    # Shouldn't reach here
    return "unknown"

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):

    log_file = open('/data/powerserver_access.log', 'w')

    def do_GET(self):

            global inverter_w
            global inverter_today
            global inverter_total

            # Reset daily total after midnight
            if ((inverter_today > 0) and (datetime.datetime.today().hour >= 0) and (datetime.datetime.today().hour < 9)and self.path.endswith("below_horizon")):
                inverter_today = 0

            if (self.path.endswith("below_horizon")) or (self.path.endswith("favicon.ico")):
                # Inverter is probably offline
                resp_status = "inactive"
            else:
                # Fetch from inverter
                resp_status = fetch_inverter_power()

            if (resp_status == "active"):
                # Online, real values
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write( json.dumps(
                        { "inverter" : inverter_w,
                        "today" : inverter_today,
                        "total" : inverter_total,
                        "status" : resp_status }
                    ).encode('UTF-8'))

            if (resp_status == "no data"):
                # Return the last set of values we got
                self.send_response(503)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write( json.dumps(
                        { "inverter" : inverter_w,
                        "today" : inverter_today,
                        "total" : inverter_total,
                        "status" : resp_status }
                    ).encode('UTF-8'))

            if (resp_status == "inactive"):
                # Probably offline
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write( json.dumps(
                        { "inverter" : 0,
                        "today" : inverter_today,
                        "total" : inverter_total,
                        "status" : resp_status }
                    ).encode('UTF-8'))

            if (resp_status.startswith("exception") or (resp_status == "unknown")):
                # Unknown error
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write( json.dumps(
                        { "status": "unknown-error",
                           "error": resp_status }
                    ).encode('UTF-8'))

server = HTTPServer(('', 8081), MyRequestHandler)

authstr = config['username'] + ":" + config['password']
auth_headers = {"Authorization": f"Basic {base64.b64encode(authstr.encode()).decode()}"}

thread = threading.Thread(target = server.serve_forever)
thread.daemon = True

try:
    thread.start()
except KeyboardInterrupt:
    server.shutdown()
    sys.exit(0)

while True:
    time.sleep(1)
