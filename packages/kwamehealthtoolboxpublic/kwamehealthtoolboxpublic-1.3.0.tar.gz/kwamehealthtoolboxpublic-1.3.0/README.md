# kwamehealthtoolbox
Kwame Health toolbox with custom functions

## Instructions

```
python -m venv venv
./venv/scripts/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python setup.py install
```

python setup.py sdist bdist_wheel

twine check dist/*

twine upload dist/*

## Package: sendEmail
Contains the function sendCustomEmail.

Meant for sending custom emails.

## Package: sendWhatsAppMessage
Contains the function sendTwilioMessage.

sendTwilioMessage is used to send messages using Twilios WhatsApp API.

## Package: createDocument
Contains the function convertDoc.

convertDoc is used to convert a page into PDF using convertAPI.

## Package: getDateTime
Contains the function timeData.

timeData is used to get back variables for datetime.