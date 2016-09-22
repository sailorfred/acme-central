# acme-central
ACME client that keeps your Let's Encrypt account keys off your server

The [Let's Encrypt](https://letsencrypt.org/) organization is aiming make it
easy to use HTTPS with free X.509 certificates when you meet certain
standardized requirements.

Unfortunately, some of those requirements for certbot make it difficult to
follow secure practices.

The [Let's Encrypt NoSudo](https://github.com/diafygi/letsencrypt-nosudo)
project is a step in the right direction, but still requires manual steps
and a short outage of your website.

Here are some issues that this project aims to improve on:

* Let's Encrypt account private key is present on the web server
* Certbot modifies your webserver configuration
* Certbot installs software on your machine
* A web server is briefly run on your domain, bringing down your site
* Root access is required
* Does not easily support multiple accounts

##Requirements

### GNU Make
* Linux will have this already installed
* FreeBSD has a port
* Mac OSX has Xcode or [Command Line Tools](http://osxdaily.com/2014/02/12/install-command-line-tools-mac-os-x/)
* Windows 10 [Bash on Ubuntu](https://msdn.microsoft.com/en-us/commandline/wsl/about) should have it

### OpenSSL

### Python
2.7 or 3.x should work.

### awk
If you have the others, you'll likely have this, too.

### ssh/scp
You'll want to be able to copy challenge responses and certificates to your web servers.

### Remote write access to http://&lt;domain&gt;/.well-known/acme-challenge/
The Let's Encrypt ACME server will look here for a token signed by your private key.

You must configure your web server to serve static files from that location and
be writable by scp from your key management machine.

### Optionally - Remote write access to the cert location
After you are comfortable with this utility you can have it push the new cert to your server(s).

## Usage
Clone this repo and execute these commands:

```
cd acme-central
make
```

will give you the current help text.

Here is an example that registers an account and generates the .pem file:

```
make ACCOUNT=sailorfred CERT=example.com SAN_DOMAINS=example.com,www.example.com WELL_KNOWN_DIR=/var/www/example/.well-known/acme-challenge/ pem
```

After running this, you should have your necessary files in your $(ACCOUNT) subdir.

##Sandbox Testing

You may edit the Makefile to change the LE_SERVER to the staging server,
or override it in the make params.
