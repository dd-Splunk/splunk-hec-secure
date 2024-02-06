import splunklib.client as client

# https://docs.splunk.com/DocumentationStatic/PythonSDK/1.7.4/client.html

s = client.Service(username="boris", password="natasha")
s.login()
# Or equivalently
s = client.connect(username="boris", password="natasha")
# Or if you already have a session token
s = client.Service(token="atg232342aa34324a")
# Or if you already have a valid cookie
s = client.Service(cookie="splunkd_8089=...")
service = client.connect(...)
storage_passwords = service.storage_passwords

# Create a secret
storage_password = storage_passwords.create("password1", "user1", "realm1")
print("Created storage password with name: {}".format(storage_password.name))

service = client.connect(...)
storage_passwords = service.storage_passwords

# List secrets
for storage_password in storage_passwords.list():
    print(storage_password.name)
