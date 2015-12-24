# Mockbox
Free, ephemeral, and fast online SMTP server mock. The no frills, no sign-up alternative to [Mailtrap](https://mailtrap.io/): just quick and easy verification that your application is sending the emails you expect.

# [Use it now! →](https://mockbox.io)

## Get Started
```bash
$ git clone https://github.com/jkingsman/Mockbox.git # Clone the mockbox repo
$ pip install -r Requirements.txt # install dependencies
$ sudo python Mockbox.py # run that puppy
```

Runs by default on ports 80 (HTTP), 9000 (HTTP/WebSockets), and 587 (SMTP).

If you configure SSL, make sure you enable it and point it to valid keys in `Config.py`. Note that port 25 is often blocked, hence the use of the 'standard' SMTP backup port of 587.

## Development and Backend
`Mockbox.py` spawns two threads, a Web thread and a Mailbox thread. The Web thread serves static files from `/static/dist` and handles websocket serving. The Mailbox thread receives and parses emails, smacks the attachments around a little bit, and pushes a nice dictionary onto the shared thread queue for the Web thread to munch through and push down the websocket.

Front end development uses `gulp`; write your code in `/static/src/` and run `gulp` (for one-time static file generation) or `gulp watch` (for continuous background file watching and local file serving). The front end does some funky rolling of the JS and Jade files -- 99% of work is in `/static/src/jade/index.jade` and `/static/src/js/index.js`. New libraries go in the `/static/src/lib` folder and should be uglified in the `js-lib` gulp task.

To customize the site to your domain name, change the `domain` in `Config.py`, but it will still function correctly if you fail to set that; it will just generate email addresses at the `mockbox.io` domain.

### Future Development/TODO
* Testing
* Refactor front end (at least away from jQuery; ideally to a front end framework)
* Import SSMTPD to allow for encrypted SMTP connections

## Local Server
Don't need something web accessible? Run a local no-frills server with vanilla python:
```bash
sudo python -m smtpd -c DebuggingServer -n localhost:25
```
