ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 py3-pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Python 3 HTTP Server serves the current working dir
# So let's set it to our add-on persistent data directory.
WORKDIR /data

# Copy data for add-on
COPY run.sh /
COPY inverter_proxy.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

