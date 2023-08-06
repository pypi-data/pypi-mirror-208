# LicenseSpring Python Library

The LicenseSpring Python Library provides convenient access to the LicenseSpring API from
applications written in the Python language.

## Installation

Install `licensespring` library:

```
pip install licensespring
```

Requires: Python >=3.7

## Hardware (Device) IDs

This library provides preconfigured hardware identity providers:
- `HardwareIdProvider` (default)
- `PlatformIdProvider`

You can set the desired hardware identity provider when initializing the APIClient:
```python
api_client = APIClient(api_key="_your_api_key_", shared_key="_your_shared_key_", hardware_id_provider=PlatformIdProvider)
```

It also supports their customization and creation of your own hardware id provider.

### HardwareIdProvider

 Uses [uuid.getnode()](https://docs.python.org/3/library/uuid.html#uuid.getnode) to generate unique ID per device as described:

> Get the hardware address as a 48-bit positive integer. The first time this runs, it may launch a separate program, which could be quite slow. If all attempts to obtain the hardware address fail, we choose a random 48-bit number with the multicast bit (least significant bit of the first octet) set to 1 as recommended in RFC 4122. “Hardware address” means the MAC address of a network interface. On a machine with multiple network interfaces, universally administered MAC addresses (i.e. where the second least significant bit of the first octet is unset) will be preferred over locally administered MAC addresses, but with no other ordering guarantees.

All of the methods exposed by `HardwareIdProvider`:
```python
class HardwareIdProvider:
    def get_id(self):
        return str(uuid.getnode())

    def get_os_ver(self):
        return platform.platform()

    def get_hostname(self):
        return platform.node()

    def get_ip(self):
        return socket.gethostbyname(self.get_hostname())

    def get_is_vm(self):
        return False

    def get_vm_info(self):
        return None

    def get_mac_address(self):
        return ":".join(("%012X" % uuid.getnode())[i : i + 2] for i in range(0, 12, 2))

    def get_request_id(self):
        return str(uuid.uuid4())
```

### PlatformIdProvider

Uses [sys.platform](https://docs.python.org/3/library/sys.html#sys.platform) and OS queries to find the raw GUID of the device.

Extends the `HardwareIdProvider` and overwrites only the `get_id` method:
```python
class PlatformIdProvider(HardwareIdProvider):
    def get_id(self):
        id = None

        if sys.platform == 'darwin':
            id = execute("ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'")

        if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'msys':
            id = read_win_registry('HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography', 'MachineGuid')
            if not id:
                id = execute('wmic csproduct get uuid').split('\n')[2].strip()

        if sys.platform.startswith('linux'):
            id = read_file('/var/lib/dbus/machine-id')
            if not id:
                id = read_file('/etc/machine-id')

        if sys.platform.startswith('openbsd') or sys.platform.startswith('freebsd'):
            id = read_file('/etc/hostid')
            if not id:
                id = execute('kenv -q smbios.system.uuid')

        if not id:
            id = super().get_id()

        return id
```

### Customization

Extend any of the preconfigured hardware identity providers, overwrite the methods you want and provide it when initializing the APIClient:
```python
class CustomHardwareIdProvider(HardwareIdProvider):
    def get_id(self):
        return "_my_id_"

api_client = APIClient(api_key="_your_api_key_", shared_key="_your_shared_key_", hardware_id_provider=CustomHardwareIdProvider)
```

## APIClient Usage Examples

### Set app version
```python
import licensespring

licensespring.app_version = "MyApp 1.0.0"
```

### Create APIClient
```python
from licensespring.api import APIClient

api_client = APIClient(api_key="_your_api_key_", shared_key="_your_shared_key_")
```

### Activate key based license
```python
product = "lkprod1"
license_key = "GPB7-279T-6MNK-CQLK"
license_data = api_client.activate_license(product=product, license_key=license_key)

print(license_data)
```

### Activate user based license
```python
product = "uprod1"
username = "user1@email.com"
password = "nq64k1!@"

license_data = api_client.activate_license(
    product=product, username=username, password=password
)

print(license_data)
```

### Deactivate key based license
```python
product = "lkprod1"
license_key = "GPUB-J4PH-CGNK-C7LK"
is_deactivated = api_client.deactivate_license(product=product, license_key=license_key)

print(is_deactivated)
```

### Deactivate user based license
```python
product = "uprod1"
username = "user1@email.com"
password = "nq64k1!@"

license_data = api_client.deactivate_license(
    product=product, username=username, password=password
)

print(license_data)
```

### Check key based license
```python
product = "lkprod1"
license_key = "GPBQ-DZCP-E9SK-CQLK"

license_data = api_client.check_license(product=product, license_key=license_key)

print(license_data)
```

### Check user based license
```python
product = "uprod1"
username = "user2@email.com"
password = "1l48y#!b"

license_data = api_client.check_license(product=product, username=username)

print(license_data)
```

### Add consumption
```python
product = "lkprod1"
license_key = "GPSU-QTKQ-HSSK-C9LK"

# Add 1 consumption
consumption_data = api_client.add_consumption(
    product=product, license_key=license_key
)

# Add 3 consumptions
consumption_data = api_client.add_consumption(
    product=product, license_key=license_key, consumptions=3
)

# Add 1 consumption, allow overages and define max overages
consumption_data = api_client.add_consumption(
    product=product, license_key=license_key, allow_overages=True, max_overages=10
)

print(consumption_data)
```

### Add feature consumption
```python
product = "lkprod1"
license_key = "GPTJ-LSYZ-USEK-C8LK"
feature = "lkprod1cf1"

# Add 1 consumption
feature_consumption_data = api_client.add_feature_consumption(
    product=product, license_key=license_key, feature=feature
)

# Add 3 consumptions
feature_consumption_data = api_client.add_feature_consumption(
    product=product, license_key=license_key, feature=feature, consumptions=3
)

print(feature_consumption_data)
```

### Trial key
```python
product = "lkprod2"

trial_license_data = api_client.trial_key(product=product)

print(trial_license_data)
```

### Product details
```python
product = "lkprod1"

product_data = api_client.product_details(product=product)

print(product_data)
```

### Track device variables
```python
product = "lkprod1"
license_key = "GPUB-SZF9-AB2K-C7LK"
variables = {"variable_1_key": "variable_1_value", "variable_2_key": "variable_2_value"}

is_tracked = api_client.track_device_variables(product=product, license_key=license_key, variables=variables)

print(is_tracked)
```

### Get device variables
```python
product = "lkprod1"
license_key = "GPUB-SZF9-AB2K-C7LK"

device_variables = api_client.get_device_variables(product=product, license_key=license_key)

print(device_variables)
```

### Floating borrow
```python
product = "lkprod1"
license_key = "GPUC-NGWU-3NJK-C7LK"

# Borrow for 2 hours
borrowed_until = (datetime.utcnow() + timedelta(hours=2)).isoformat()
floating_borrow_data = api_client.floating_borrow(product=product, license_key=license_key, borrowed_until=borrowed_until)

print(floating_borrow_data)
```

### Floating release
```python
product = "lkprod1"
license_key = "GPUC-NGWU-3NJK-C7LK"

is_released = api_client.floating_release(product=product, license_key=license_key)

print(is_released)
```

### Change password
```python
username = "user4@email.com"
password = "_old_password_"
new_password = "_new_password_"

is_password_changed = api_client.change_password(username=username, password=password, new_password=new_password)

print(is_password_changed)
```

### Versions
```python
product = "lkprod1"
license_key = "GPB7-279T-6MNK-CQLK"

# Get versions for all environments
versions_data = api_client.versions(product=product, license_key=license_key)

# Get versions for mac environment
mac_versions_data = api_client.versions(
    product=product, license_key=license_key, env="mac"
)

print(versions_data)
```

### Installation file
```python
product = "lkprod1"
license_key = "GPB7-279T-6MNK-CQLK"

# Get the latest installation file
installation_file_data = api_client.installation_file(
    product=product, license_key=license_key
)

# Get the latest installation file for linux environment
installation_file_data = api_client.installation_file(
    product=product, license_key=license_key, env="linux"
)

# Get the latest installation file for version 1.0.0
installation_file_data = api_client.installation_file(
    product=product, license_key=license_key, version="1.0.0"
)

print(installation_file_data)
```

### Customer license users
```python
product = "uprod1"
customer = 'c1@c.com'

customer_license_users_data = api_client.customer_license_users(
    product=product, customer=customer
)

print(customer_license_users_data)
```

### SSO URL
```python
product = "uprod1"
customer_account_code = "ccorp"

sso_url_data = api_client.sso_url(
    product=product, customer_account_code=customer_account_code
)

print(sso_url_data)
```


### SSO URL with `code` response type
```python
product = "uprod1"
customer_account_code = "ccorp"

sso_url_data = api_client.sso_url(
    product=product,
    customer_account_code=customer_account_code,
    response_type="code",
)

print(sso_url_data)
```

### Activate offline
```python
product = "lkprod1"
license_key = "GPY7-VHX9-MDSK-C3LK"

# Generate data for offline activation
activate_offline_data = api_client.activate_offline_dump(
    product=product, license_key=license_key
)

# Write to file
with open('activate_offline.req', mode='w') as f:
    print(activate_offline_data, file=f)

# Activate offline
license_data = api_client.activate_offline(data=activate_offline_data)

print(license_data)
```

### Activate offline load
```python
# Read from file
with open('./ls_activation.lic') as file:
    ls_activation_data = file.read()

license_data = api_client.activate_offline_load(ls_activation_data)

print(license_data)
```

### Deactivate offline
```python
product = "lkprod1"
license_key = "GPYC-X5J2-L5SK-C3LK"

# Generate data for offline deactivation
deactivate_offline_data = api_client.deactivate_offline_dump(
    product=product, license_key=license_key
)

# Write to file
with open('deactivate_offline.req', mode='w') as f:
    print(deactivate_offline_data, file=f)

# Deactivate offline
is_deactivated = api_client.deactivate_offline(data=deactivate_offline_data)

print(is_deactiavted)
```
