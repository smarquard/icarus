#!/usr/bin/with-contenv bashio

# Config variables
INVERTER_URL=$(bashio::config 'inverter')
USERNAME=$(bashio::config 'username')

bashio::log.info "Starting proxy to $INVERTER_URL with username $USERNAME"

python3 /inverter_proxy.py

