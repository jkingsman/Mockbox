# Mockbox
Free, ephemeral, and fast online SMTP server mock. The no frills, no sign-up alternative to [Mailtrap](https://mailtrap.io/): just quick and easy verification that your application is sending the emails you expect.

## Get Started
1. Clone the mockbox repo
2. `pip install` from the requirements file
3. `sudo python Mockbox.py`

## Local Server
Don't need something web accessible? Run a local no-frills server with vanilla python:
```bash
sudo python -m smtpd -c DebuggingServer -n localhost:25
```
