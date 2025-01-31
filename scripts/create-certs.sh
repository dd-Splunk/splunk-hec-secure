#!/bin/bash

# Must run as root
if [ $EUID -ne 0 ]
then
    echo "Please run this script with root privileges"
    exit 1
fi

# Setup context
APP_DIR=$PWD/configs/mycerts
DOMAIN=dessy.one
SPLUNK_HOST=splunk
FQDN=${SPLUNK_HOST}.${DOMAIN}
ROOT_CA=isrgrootx1.pem

# Get Let's Encrypt Root CA
wget -q https://letsencrypt.org/certs/$ROOT_CA -O $APP_DIR/$ROOT_CA

# Create cert
# Use standalone mode as no Web server exists yet.
certbot certonly --standalone -d $FQDN
cd /etc/letsencrypt/live/$FQDN

# Add Certs to the Splunk cert store
cp fullchain.pem privkey.pem $APP_DIR

# Create chain of certs for HEC:
# https://community.splunk.com/t5/All-Apps-and-Add-ons/How-do-I-secure-the-event-collector-port-8088-with-an-ssl/m-p/571431/highlight/true#M75360
cat cert.pem privkey.pem chain.pem > $APP_DIR/hec.pem

# Ensure proper ownership
chown splunk:splunk $APP_DIR/*.pem
