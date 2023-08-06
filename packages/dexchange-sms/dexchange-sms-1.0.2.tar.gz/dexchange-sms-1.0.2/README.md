# DSMS Package

DSMS is a Python package that provides a simple way to interact with the Dexchange SMS API. With DSMS, you can send SMS messages and authenticate users via SMS.

[https://dexchange-sms.com](https://dexchange-sms.com/)

## Installation

You can install the DSMS package using pip:


## Usage
### To use DSMS, you need to have an API key. You can get one by signing up at [Dexchange](https://dexchange-sms.com/auth/signup).

```python
from dsms import DSMS

# Create an instance of DSMS with your API key
dsms = DSMS(api_key='your-api-key')

# Send an SMS
sms_data = {
    'number': ['1234567890'],  # List of recipient numbers
    'signature': 'YourApp',
    'content': 'Hello, World!'
}
response = dsms.send_sms(data=sms_data)
print(response)

# Send an authentication SMS
auth_data = {
    'number': '1234567890',
    'service': 'YourApp',
    'lang': 'en'
}
response = dsms.send_auth_sms(data=auth_data)
print(response)

# Verify an authentication SMS
verify_data = {
    'number': '1234567890',
    'service': 'YourApp',
    'otp': '123456'
}
response = dsms.verify_auth_sms(data=verify_data)
print(response)

### Make sure to replace 'your-api-key' with your actual DSMS API key.

