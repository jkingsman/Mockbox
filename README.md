# mockmail.io
Free, ephemeral, and fast online SMTP server mock. The easy and free alternative to [Mailtrap](https://mailtrap.io/) - no sign up needed; just quick and easy verification that your application is sending the emails you expect. 

## Local Server
Don't need something web accessible? Run a local no-frills server with vanilla python:
```bash
sudo python -m smtpd -c DebuggingServer -n localhost:25
```
