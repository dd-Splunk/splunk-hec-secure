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

cp fullchain.pem prickey.pem $APP_DIR

# Get Let's Encrypt Root CA
wget https://letsencrypt.org/certs/isrgrootx1.pem -P $APP_DIR

cat cert.pem privkey.pem chain.pem > $APP_DIR/hec.pem

chown splunk:splunk $APP_DIR/*.pem

```

in `$SPLUNK_HOME/etc/auth/mycerts`

```
fullchain.pem
hec.pem
isrgrootx1.pem
privkey.pem

```

To check for cert chain:

```bash
openssl s_client -connect localhost:8000
```

From: <https://community.splunk.com/t5/All-Apps-and-Add-ons/How-do-I-secure-the-event-collector-port-8088-with-an-ssl/m-p/243885>

This answer was the most helpful for me.
I am adding a few things I found helpful for anyone using Certbot/LetsEncrypt

- Generate the pem key using the letsencrypt certs

```bash
cd /etc/letsencrypt/live/your-server-hostname/
cat cert.pem privkey.pem chain.pem > splunk.pem
chmod 777 splunk.pem
```

- Use the following for `inputs.conf`

```ìni
[http]
disabled = 0
index = your-hec-index-name
enableSSL = 1
serverCert = /etc/letsencrypt/live/your-server-hostname/splunk.pem
sslPassword =
crossOriginSharingPolicy = *
```

- Troubleshoot the connection

This comes from this forum post <https://community.splunk.com/t5/Security/Cna-t-Connect-to-HTTP-Event-Collector-Endpoint-with-My/m-p/308377>

### Test HEC

```bash
curl -k https://splunk.dessy.one:8088/services/collector/event \
-H "Authorization: Splunk abcd-1234-efgh-5678" \
-d '{"event":"hello world"}' -v
```
