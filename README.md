# Splunk HEC Secure

PoC to secure HEC using Let's Encrypt certificates.

## Generate Certs for Web

### Steps

<https://github.com/dd-Splunk/splunk-hec-secure/blob/ca6735c47e2f07c92ffff8f09c45bdbba38559ed/scripts/create-certs.sh>

```bash
# Must be run as root

APP_DIR=$PWD/configs/mycerts
DOMAIN=dessy.one
SPLUNK_HOST=splunk
FQDN=s${SPLUNK_HOST}.${DOMAIN}

# Standalone as no server exists yet.
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
-rw-r--r--. 1 splunk splunk 5242 Feb 12 16:06 fullchain.pem
-rw-r--r--. 1 splunk splunk 5483 Feb 12 16:06 hec.pem
-rw-r--r--. 1 splunk splunk 1939 Feb 12 16:06 isrgrootx1.pem
-rw-------. 1 splunk splunk  241 Feb 12 16:06 privkey.pem

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
cat cert.pem privkey.pem chain.pem > hec.pem
chmod 644 hec.pem
```

- Use the following for `inputs.conf`

```ìni
[http]
disabled = 0
index = your-hec-index-name
enableSSL = 1
serverCert = /etc/letsencrypt/live/your-server-hostname/hec.pem
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
