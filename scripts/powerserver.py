#! /usr/bin/python

import threading
import time
import datetime
import os
import sys
import re
import json
import urllib
import urllib2
import base64

import solar_config

import SimpleHTTPServer
from BaseHTTPServer import HTTPServer

sys.stderr = open('/data/log/powerserver_err.log', 'w')

# Values we expect to read
inverter_w = -1
grid_w = -1

def fetch_inverter_power():
    # First check if there's been a reading recently
    with open('/usr/share/nginx/www/staticdata/inverter.txt', 'r') as file:
        last_power = file.read().replace('\n', '')

    if (last_power == '0'):
	return 0;

    request = urllib2.Request(solar_config.solis_url)
    base64string = base64.b64encode('%s:%s' % (solar_config.solis_username, solar_config.solis_password))
    request.add_header("Authorization", "Basic %s" % base64string)
    response = urllib2.urlopen(request, timeout = 10)
    status_page = response.read()

    solis_power_re = re.compile('webdata_now_p\s=\s"([0-9]+)";');
    m = solis_power_re.search(status_page)
    if m:
        power = m.group(1)
        return int(power);

    return 0;

def fetch_grid_power():
    response = urllib2.urlopen(solar_config.efergy_url, timeout = 15)
    efergy_data = json.loads(response.read())
    for key, value in efergy_data[0]["data"][0].items():
	grid_w = value
    return grid_w

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    log_file = open('/data/log/powerserver_access.log', 'w')

    def do_GET(self):
            # Refresh if needed (for now, fetch anyway)

            inverter_w = fetch_inverter_power()
            grid_w = fetch_grid_power()

	    self.send_response(200)
	    self.send_header("Content-type", "application/json")
	    self.send_header("Access-Control-Allow-Origin","*")
	    self.end_headers()
	    self.wfile.write(json.dumps({"inverter" : inverter_w, "grid" : grid_w}))

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

print 'Server started on port 8081'

while True:
    time.sleep(60)

