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

# Create cert
# certbot certonly --standalone -d $FQDN
cd /etc/letsencrypt/live/$FQDN

# Get Let's Encrypt Root CA
wget -q https://letsencrypt.org/certs/$ROOT_CA -O $APP_DIR/$ROOT_CA

# Add Certs to the Splunk cert store
cp fullchain.pem privkey.pem $APP_DIR

# Create chain of certs for HEC
cat cert.pem privkey.pem chain.pem > $APP_DIR/hec.pem

# Ensure proper ownership
chown splunk:splunk $APP_DIR/*.pem
