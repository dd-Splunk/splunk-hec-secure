# Splunk HEC Secure

PoC to secure HEC using Let's Encryot CERT

## Generate Certs for Web

### Steps

```bash
# Must be run as root

APP_DIR=$PWD/configs/mycerts
DOMAIN=dessy.one
SPLUNK_HOST=splunk
FQDN=s${SPLUNK_HOST}.${DOMAIN}
certbot certonly --standalone -d $FQDN
cd /etc/letsencrypt/live/$FQDN

# Will prompt for password
openssl pkcs8 -topk8 -inform PEM -outform PEM -in privkey.pem -out privkey.enc.pem

cp fullchain.pem prickey.pem $APP_DIR
wget https://letsencrypt.org/certs/isrgrootx1.pem -P $APP_DIR
chown splunk:splunk $APP_DIR/*.pem

```

in `$SPLUNK_HOME/etc/auth/mycerts`

```
fullchain.pem
isrgrootx1.pem
privkey.pem

```

To check for cer chain:

```bash
openssl s_client -connect localhost:8000
```
