# acme-central
ACME client that keeps your Let's Encrypt account keys off your server
and supports centralized certificate management.
Your cert management happens on one machine (desktop or laptop, not your web servers)
allowing you to push certs to production machines via scp, chef, puppet, ansible, etc.

The [Let's Encrypt](https://letsencrypt.org/) organization is making it
easy to use HTTPS with free X.509 certificates when you meet certain
standardized requirements via their certbot client.

Unfortunately, some of those requirements for certbot make it difficult to
follow secure practices.

The [Let's Encrypt NoSudo](https://github.com/diafygi/letsencrypt-nosudo)
and [acme-tiny](https://github.com/diafygi/acme-tiny) projects are a step in
the right direction, but still require manual steps
and a short outage of your website.

## Motivation

Here are some issues with the existing projects that
this project aims to improve on:

* Most natural for a single webserver
* Let's Encrypt account private key is present on the web server
* Certbot in auto mode modifies your webserver configuration
* Certbot in auto mode installs software on your machine
* Do not easily support multiple Let's Encrypt accounts

Here are the acme-central features that help:

* Easily customizable methods for pushing challenges and certificates to web servers to fit your environment.
* Multiple web servers easily supported.
* Small code base (~300 SLOC) for easy auditing.
* Small dependency set - Most Linux boxes already have bash, openssl, python, make, awk, and ssh. Mac only needs make installed.

## Expected use case for acme-central user

Separation of certificate management from web servers - one management
machine that holds the Let's Encrypt account private key and performs
the certificate management vs. the web servers that get the challenge
files and certificates pushed to them.

##Requirements

### Bash
* Linux defaults to bash
* FreeBSD has a port
* Mac OSX has bash since Panther
* Windows 10 [Bash on Ubuntu](https://msdn.microsoft.com/en-us/commandline/wsl/about) should have it

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

### find
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
make ACCOUNT=sailorfred EMAIL=admin@example.com CERT=example.com SAN_DOMAINS=example.com,www.example.com WELL_KNOWN_DIR=/var/www/example/.well-known/acme-challenge/ pem
```

After running this with the appropriate substitutions, you should have your necessary files in your $(ACCOUNT)/expires subdir.

This command does the initial registration only (usually, you would let the pem generation do the registration):

```
make ACCOUNT=sailorfred EMAIL=admin@example.com sailorfred/registered
```

Doing this means you can skip the email address for the domain registration.

### Renewal
Clear up the files that need to be regenerated for renewal:

```
make clean_old
```

This defaults to cleaning up 60 day old certificates.

Then redo the registration process:

```
make ACCOUNT=sailorfred CERT=example.com SAN_DOMAINS=example.com,www.example.com WELL_KNOWN_DIR=/var/www/example/.well-known/acme-challenge/ pem
```

Your Let's Encrypt registration, private keys, CSR, etc. won't be regenerated.

These can be combined in one make run:

```
make clean_old ACCOUNT=sailorfred CERT=example.com SAN_DOMAINS=example.com,www.example.com WELL_KNOWN_DIR=/var/www/example/.well-known/acme-challenge/ pem
```

##Sandbox Testing

You may edit the Makefile to change the LE_SERVER to the staging server,
or override it in the make params.
