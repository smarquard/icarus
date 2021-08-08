#! /usr/bin/python3

import threading
import time
import serial
import datetime
import os
import sys
import re
import json

import http.server
from http.server import HTTPServer

sys.stderr = open('/data/log/voltageserver_err.log', 'w')

# Values we expect to read

voltage = -1		# voltage
mains_power = -1	# mains power
inverter = -1		# inverter status

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):

    log_file = open('/data/log/voltageserver_access.log', 'w')

    def do_GET(self):
	    self.send_response(200)
	    self.send_header("Content-type", "application/json")
	    self.send_header("Access-Control-Allow-Origin","*")
	    self.end_headers()
	    #self.wfile.write(json.dumps({"voltage" : voltage}))
	    self.wfile.write(json.dumps({"voltage" : voltage}).encode('UTF-8'))

    def log_message(self, format, *args):
        self.log_file.write("%s - - [%s] %s\n" %
                            (self.client_address[0],
                             self.log_date_time_string(),
                             format%args))
        self.log_file.flush()

server = HTTPServer(('', 8080), MyRequestHandler)

thread = threading.Thread(target = server.serve_forever)
thread.daemon = True

try:
    thread.start()
except KeyboardInterrupt:
    server.shutdown()
    sys.exit(0)

print('Server started on port 8080')

port = '/dev/ttyACM0'
ser = serial.Serial(port, 9600, timeout=12) # Create a serial object

# ser.readline();

mv_re = re.compile('voltage=([0-9.]+)');
mains_re = re.compile('mains_power=([01]+)');
inverter_re = re.compile('inverter=([01]+)');

while True:
	status = ser.readline().decode('ascii')

	# print("status: " + status + "\n")

	m = mv_re.search(status)
	if m:
		voltage = m.group(1)

	m = mains_re.search(status)
	if m:
		mains_power = m.group(1);

	m = inverter_re.search(status)
	if m:
		inverter = m.group(1);

	# print(json.dumps({"voltage" : voltage, "mains_power" : mains_power, "inverter" : inverter}))

