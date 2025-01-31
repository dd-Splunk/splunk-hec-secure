# Splunk HEC Secure

PoC to secure HEC using Let's Encrypt certificates.

## Generate Certs for Web

### Steps

- Create the certificates

<https://github.com/dd-Splunk/splunk-hec-secure/blob/0c991a9c0b164b1f9b9bd9f6cc3e9af8327af499/scripts/create-certs.sh#L3-L31>

At the end of the script the following should be
in `$SPLUNK_HOME/etc/auth/mycerts`

```bash
-rw-r--r--. 1 splunk splunk 5242 Feb 12 16:06 fullchain.pem
-rw-r--r--. 1 splunk splunk 5483 Feb 12 16:06 hec.pem
-rw-r--r--. 1 splunk splunk 1939 Feb 12 16:06 isrgrootx1.pem
-rw-------. 1 splunk splunk  241 Feb 12 16:06 privkey.pem

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

### Test HEC

Send a test event:

```bash
DOMAIN=dessy.one
SPLUNK_HOST=splunk
FQDN=${SPLUNK_HOST}.${DOMAIN}
curl -k https://$FQDN:8088/services/collector/event \
-H "Authorization: Splunk abcd-1234-efgh-5678" \
-d '{"event":"hello world"}' -v
```

### Troubleshooting

Check for cert chain integrity:

```bash
DOMAIN=dessy.one
SPLUNK_HOST=splunk
FQDN=${SPLUNK_HOST}.${DOMAIN}
openssl s_client -connect $FQDN:8000
openssl s_client -connect $FQDN:8088
```

### Renew certificate

Run the following ideally once per day:

```bash
sudo certbot renew
```
