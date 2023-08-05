# zebedee-python-lib
A python library that makes building with the ZBD API easy and fast. To sign-up for the ZBD API, use https://dashboard.zebedee.io .

To get started, you'll need to create a project using using the Developer Dashboard. Once you have a project, grab the API key from the API key tab. We will now assume that you have an API Key.

## features
The ZBD class has the following methods:

- get_wallet_details(): retrieves details of the user's wallet
create_charge(amount_of_seconds_to_expire_after, amount_msats, description, internal_id=None): creates a charge request with the specified parameters

- get_charge_details(zbd_id): retrieves details of a charge request with the specified ID
create_static_charge(allowedSlots, min_amount_msats, max_amount_msats, description, internal_id, success_message): creates a static charge request with the specified parameters

- update_static_charge_details(min_amount_msats, max_amount_msats, description, success_message, allowed_slots=None): updates the details of a static charge request with the specified ID

- get_static_charge_details(zbd_id): retrieves details of a static charge request with the specified ID
create_withdrawal_request(amount_of_seconds_to_expire_after, amount_msats, description, internal_id): creates a withdrawal request with the specified parameters

- get_withdrawal_request_details(zbd_id): retrieves details of a withdrawal request with the specified ID
send_keysend_payment(public_key, amount_msats, metadata=None, tlv_records=None): sends a keysend payment with the specified parameters

- pay_invoice(invoice, description, internal_id, amount=None): pays an invoice with the specified parameters.

- & much more!

## example usage
Install the package using:
`pip install zebedee`

Now you're ready to get started!

```
from zebedee import *

# create a new ZBD object with callback URL to get updates after there is a status update.
project_a = zebedee.ZBD("your_api_key", "https://your-website.com/zbd/webhook/")

# Call the get_wallet_details function to retrieve your wallet details
wallet_details = project_a.get_wallet_details()

# Create a new charge for 1 hour with an amount of 5000 msats and a description
charge_details = project_a.create_charge(amount_of_seconds_to_expire_after=3600, amount_msats=5000, description='Test Charge')

# Get the details of a charge with the specified ZBD ID
charge_id = charge_details["id"]
charge_details = project_a.get_charge_details(charge_id)

# Create a new static charge with the specified parameters
static_charge_details = project_a.create_static_charge(allowed_slots=10, min_amount_msats=1000, max_amount_msats=10000, description='Test Static Charge', internal_id='123', success_message='Payment successful')

# Update the details of an existing static charge
static_charge_id = static_charge_details["id"]
updated_static_charge_details = project_a.update_static_charge_details(id=static_charge_id,allowed_slots=None, min_amount_msats=2000, max_amount_msats=20000, description='Updated Static Charge', success_message='Payment successful')

# Get the details of a static charge with the specified ZBD ID
static_charge_id = static_charge_details["id"]
static_charge_details = project_a.get_static_charge_details(static_charge_id)

# Create a new withdrawal request with the specified parameters
withdrawal_request_details = project_a.create_withdrawal_request(amount_of_seconds_to_expire_after=3600, amount_msats=10000, description='Test Withdrawal Request', internal_id='123')

# Get the details of a withdrawal request with the specified ZBD ID
withdrawal_request_id = withdrawal_request_details["id"]
withdrawal_request_details = project_a.get_withdrawal_request_details(withdrawal_request_id)

# Send a keysend payment to the specified public key with the specified amount and metadata
public_key = 'your_public_key_here'
amount_msats = 1000
metadata = {'key': 'value'}
payment_details = project_a.send_keysend_payment(public_key, amount_msats, metadata=metadata)
print(payment_details)

# Pay an invoice with the specified parameters
invoice = 'your_invoice_here'
description = 'Test Invoice Payment'
internal_id = '123'
payment_details = project_a.pay_invoice(invoice, description, internal_id)

# get payment details for a Zebedee payment with zbd_id=123
get_payment_details = project_a.get_payment_details(zbd_id=payment_details["id"])

# validate a lightning address
validate_lightning_address = project_a.validate_lightning_address(lightning_address="santos@zbd.gg")

# send a payment to a lightning address
payment_response = project_a.send_payment_to_lightning_address(
    lightning_address="santos@zbd.gg", amount_msats=10000, comment="payment comment", internal_id="test:1"
)

# fetch a charge for a lightning address
charge_response = project_a.fetch_charge_from_lightning_address(
    lightning_address="santos@zbd.gg", amount_msats=10000, description="charge description"
)

# send a payment to a gamertag
gamertag_payment_details = project_a.send_payment_to_gamertag(gamertag="santos", amount_msats=1000, description="payment description")

# get details for a gamertag transaction with zbd_id=123
transaction_details = project_a.get_gamertag_transaction_details(zbd_id=gamertag_payment_details["transactionId"])

# get the user ID associated with a gamertag
user_id = project_a.get_user_id_from_gamertag(gamertag="santos")

# get the gamertag associated with a user ID
gamertag = project_a.get_gamertag_from_user_id(user_id=user_id)

# fetch a charge for a gamertag
charge_response = project_a.fetch_charge_from_gamertag(
    gamertag="santos", amount_msats=1000, description="charge description", internal_id="internal_id"
)

# check if an IP is in a supported region
supported = project_a.is_supported_region(ip="123.45.67.89")

# get the IP address of the ZBD production server
prod_server_ip = project_a.get_zbd_prod_server_ip()

# get the current BTC-USD exchange rate
btc_usd_price = project_a.get_btc_usd_quote_price()

# convert sats to msats
amount_msats = project_a.convert_sats_to_msats(amount_sats=1000)

# convert msats to sats
amount_sats = project_a.convert_msats_to_sats(amount_msats=1)

# transfer funds between ZBD wallets
transfer_response = project_a.transfer_zbd_funds(amount_msats=1000, recevier_wallet_id="receiver_wallet_id")
```

## best practices

- use an environmental variable for each apikey before going live with this code. 