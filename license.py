from cryptography.hazmat import backends
from cryptography.hazmat.primitives import serialization

from truepy import LicenseData, License

with open('secrets/pem-passwd.txt', 'rb') as f:
  keyPassword = f.read()
with open('secrets/license-passwd.txt', 'rb') as f:
  licensePassword = f.read()

# Load the certificate
with open('secrets/spoken-screen-cert.pem', 'rb') as f:
  certificate = f.read()

# Load the private key
with open('secrets/spoken-screen-key.pem', 'rb') as f:
  key = serialization.load_pem_private_key(
    f.read(),
    password=keyPassword,
    backend=backends.default_backend())

# Issue the license
license = License.issue(
  certificate,
  key,
  license_data=LicenseData(
    '2000-10-01T00:00:00',
    '2000-11-01T00:00:00'))

# Store the license
with open('secrets/license.key', 'wb') as f:
  license.store(f, licensePassword)


##############

with open('secrets/license.key', 'rb') as f:
  reloadedLicense = License.load(f, licensePassword)

try:
  reloadedLicense.verify(certificate)
  print(reloadedLicense.data.not_before)
except:
  print('OOPS')

# client inputs:
# - certificate
# - license password


# purchase license
# license ID emailed to user
# install client
# client has prompt for license ID
# client sends request for license to server
# server generates license and returns to client
#   for convenience, we can use the license ID as the password
