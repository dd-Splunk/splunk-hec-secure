# Splunk HEC Secure

PoC to secure HEC using Let's Encryot CERT

## Generate Certs for HEC

### Steps

```bash
# Must be run as root
DOMAIN=splunk.dessy.one
certbot certonly --standalone -d $DOMAIN
cd /etc/letsencrypt/live/$DOMAIN

# Will prompt for password
openssl pkcs8 -topk8 -inform PEM -outform PEM -in privkey.pem -out privkey.enc.pem

cat cert.pem >> hec.pem

cat privkey.enc.pem >> hec.pem

cat chain.pem >> hec.pem

```

`inputs.conf` for hec:

```ini
[http]
enableSSL=1
disabled=0
serverCert = $path/hec.pem
sslPassword= passwordwhichisusedwhilecreatingprivatekey
```
