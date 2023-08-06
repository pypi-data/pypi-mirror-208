# python-sdk
Python SDK for GetTestMail

This Python client library allows you to interact with the GetTestMail API, which provides a simple way to create temporary email addresses and receive messages sent to them.

To use this library, you will need to have a GetTestMail account. If you don't have one, you can sign up for a free [account](https://gettestmail.com).

## Installation

```bash
pip install gettestmail
```


## Usage

```python
from gettestmail.client import GetTestMailClient

# optional parameters
expires_at = "2023-04-01T00:00:00Z"

client = GetTestMailClient("your-api-key")
test_mail = client.create_new()
print(test_mail.emailAddress)

# This will wait for a message to be received up until expires_at time
test_mail = client.wait_for_message(test_mail.id)
print(test_mail.message)

```

## Models

### GetTestMail

The GetTestMail model represents a disposable email address. It has the following attributes:

* id - The id of the email address
* emailAddress - The email address
* expiresAt - The time at which the email address will expire
* message - The message received by the email address

### Message

The Message received by the email address. It has the following attributes:

* id - The id of the message
* from - The sender of the message
* to - The recipient of the message
* subject - The subject of the message
* text - Text representation of the message
* html - HTML representation of the message
* attachments - List of attachments

### Attachment

The Attachment received by the email address. It has the following attributes:

* filename - The filename of the attachment
* mimeType - The mime type of the attachment
* content - The content of the attachment


## API Documentation

TODO

## License

This project is licensed under the MIT License. See the LICENSE file for details.