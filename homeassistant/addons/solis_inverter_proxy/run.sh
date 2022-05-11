#!/usr/bin/with-contenv bashio

echo "Hello world!"

bashio::log.info "Creating configuration..."

# Config variables
INVERTER_URL=$(bashio::config 'inverter')
USERNAME=$(bashio::config 'username')
PASSWORD=$(bashio::config 'password')

bashio::log.info "Starting proxy to $INVERTER_URL with auth $USERNAME:$PASSWORD"

python3 /inverter_proxy.py

