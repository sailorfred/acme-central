LE_SERVER=acme-v01.api.letsencrypt.org
#LE_SERVER=acme-staging.api.letsencrypt.org

ACCOUNT=account
CERT=example.com
SAN_DOMAINS=example.com,www.example.com

WELL_KNOWN_DIR=/var/www/html/.well-known/acme-challenge/

CERT_DIR=/etc/nginx/ssl/

help:
	@echo Run:
	@echo
	@echo  make ACCOUNT=$(ACCOUNT) CERT=$(CERT) SAN_DOMAINS=$(SAN_DOMAINS) pem
	@echo
	@echo where ACCOUNT is your account name, perhaps your name
	@echo and CERT is the Subject CN and cert base name
	@echo and SAN_DOMAINS is a comma separated list of supported domain names, repeating the primary domain name
	@echo
	@echo Set WELL_KNOWN_DIR if other than /var/www/html/.well-known/acme-challenge/

.SECONDARY: $(ACCOUNT)/account.key $(ACCOUNT)/$(CERT).key # Don't remove my .key file when making the .csr

COMMA := ,
SPACE :=
SPACE +=

pem: $(ACCOUNT)/$(CERT).pem

bundle: $(ACCOUNT)/$(CERT).bundle.crt

$(ACCOUNT)/account.key:
	-mkdir -p $(ACCOUNT)
	openssl genrsa 4096 > $@

$(ACCOUNT)/%.key:
	openssl genrsa 4096 > $@

$(ACCOUNT)/registered: $(ACCOUNT)/account_jwk.py
	LE_SERVER=$(LE_SERVER) python ./send_request.py $(ACCOUNT) new-reg '{"resource":"new-reg", "agreement": "'$$(curl -sI https://acme-staging.api.letsencrypt.org/terms | grep Location: | awk -F '[ \\r\\n]+' 'BEGIN {ORS=""} {print $$2}')'"}' > $@
	@echo 'import json; response = json.loads("""'`cat $@`'"""); print("\\n\\nRead and agree with agreement at " + response["agreement"] + "\\n\\n")' | python

# When Boulder supports contact info
# $(ACCOUNT)/registered: $(ACCOUNT)/reg.email $(ACCOUNT)/account.key
# 	LE_SERVER=$(LE_SERVER) python ./send_request.py $(ACCOUNT) new-reg '{"resource":"new-reg", "contact": ["'`cat $(ACCOUNT)/reg.email`'"]}'
# 	touch $@

$(ACCOUNT)/reg.email:
	@echo Create a config file, $(ACCOUNT)/reg.email, with your contact email a la:
	@echo user@example.com
	@echo then rerun this make command
	@false
# End section for future contact info

$(ACCOUNT)/account_jwk.py: $(ACCOUNT)/account.key $(ACCOUNT)/__init__.py
	openssl rsa -in $< -noout -text | python ./key_to_jwk.py > $@

$(ACCOUNT)/__init__.py:
	@mkdir -p $(ACCOUNT)
	touch $@

$(ACCOUNT)/$(CERT).csr: $(ACCOUNT)/registered $(ACCOUNT)/account.key $(ACCOUNT)/$(CERT).key
	bash -c 'openssl req -new -sha256 -key $(ACCOUNT)/$(CERT).key -subj "/CN=$(CERT)" -reqexts SAN -config <(python ./ssl_conf.py $(SAN_DOMAINS))' > $@

$(ACCOUNT)/$(CERT).csr.der: $(ACCOUNT)/$(CERT).csr
	openssl req -in $< -outform DER > $@

$(ACCOUNT)/$(CERT).pem: $(ACCOUNT)/$(CERT).key $(ACCOUNT)/$(CERT).bundle.crt
	cat $^ > $@

$(ACCOUNT)/$(CERT).bundle.crt: $(ACCOUNT)/$(CERT).crt
	cat $< $(ACCOUNT)/acme_ca.crt > $@

$(ACCOUNT)/$(CERT).crt: $(ACCOUNT)/$(CERT).crt.der
	openssl x509 -inform DER -in $< -out $@

$(ACCOUNT)/$(CERT).crt.der: $(ACCOUNT)/$(CERT).csr.der $(foreach domain,$(subst $(COMMA),$(SPACE),$(SAN_DOMAINS)),$(ACCOUNT)/$(domain).challenged)
	LE_SERVER=$(LE_SERVER) python ./fetch_cert.py $(ACCOUNT) $< > $@
	openssl x509 -inform DER -in $(ACCOUNT)/acme_ca.crt.der -out $(ACCOUNT)/acme_ca.crt

$(ACCOUNT)/%.challenge: $(ACCOUNT)/$(CERT).csr
	LE_SERVER=$(LE_SERVER) python ./send_request.py $(ACCOUNT) new-authz '{"resource":"new-authz", "identifier": {"type": "dns", "value": "$*"}}' > $@

$(ACCOUNT)/%.challenged: $(ACCOUNT)/%.challenge
	LE_SERVER=$(LE_SERVER) python ./do_challenge.py $(ACCOUNT) $* $< $@

push_challenge:
	scp ./$(FILE) $(DOMAIN):$(WELL_KNOWN_DIR)

push_pem: $(ACCOUNT)/$(CERT).pem
	scp $< $(CERT):$(CERT_DIR)

push_bundle: $(ACCOUNT)/$(CERT).bundle.crt
	scp $< $(CERT):$(CERT_DIR)
