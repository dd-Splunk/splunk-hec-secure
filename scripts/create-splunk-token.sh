#!/bin/bash
#
# Create Splunk auth token
# This allows VSCode to run interative Splunk commands on so1
# from the Splunk notebook: debug.splnb
#
source .env

TOKEN=$(curl -s -k -u admin:$SPLUNK_PASSWORD --location 'https://localhost:8089/services/authorization/tokens?output_mode=json' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'name=admin' \
--data-urlencode 'audience=Admins' \
--data-urlencode 'expires_on=+1d' | jq '.entry[].content.token')

echo "Token: $TOKEN"

mkdir -p .vscode

cat << EOF > .vscode/settings.json
{
    "splunk.commands.token": $TOKEN
}
EOF
