#!/bin/sh
# Let's Encrypt tanúsítvány első beállítása a ccs_frontend számára.
#
# Futtasd EGYSZER, a szerveren (nem Windowson), miután a hg25ccs.hu (és a
# www.hg25ccs.hu) DNS A rekordja már erre a gépre mutat, és a 80/443 port
# elérhető kívülről:
#
#     ./init-letsencrypt.sh
#
# Ezután a docker compose up -d elég, a certbot automatikusan megújít.

set -e

DOMAINS="hg25ccs.hu www.hg25ccs.hu"
EMAIL="advanced.m.laboratory@gmail.com"   # értesítés lejáró tanúsítványról
STAGING=0                                 # 1 = Let's Encrypt teszt (rate limit ellen)

DATA_PATH="./certbot"
RSA_KEY_SIZE=4096

PRIMARY_DOMAIN=$(echo "$DOMAINS" | cut -d' ' -f1)

mkdir -p "$DATA_PATH/conf" "$DATA_PATH/www"

# 1) Ideiglenes önaláírt tanúsítvány, hogy az nginx el tudjon indulni.
CERT_PATH="/etc/letsencrypt/live/$PRIMARY_DOMAIN"
echo "### Ideiglenes tanúsítvány létrehozása: $PRIMARY_DOMAIN ..."
mkdir -p "$DATA_PATH/conf/live/$PRIMARY_DOMAIN"
docker compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 1 \
    -keyout '$CERT_PATH/privkey.pem' \
    -out '$CERT_PATH/fullchain.pem' \
    -subj '/CN=localhost'" certbot

# 2) Nginx indítása az ideiglenes tanúsítvánnyal.
echo "### Nginx indítása ..."
docker compose up -d ccs_frontend

# 3) Ideiglenes tanúsítvány törlése.
echo "### Ideiglenes tanúsítvány törlése ..."
docker compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$PRIMARY_DOMAIN && \
  rm -Rf /etc/letsencrypt/archive/$PRIMARY_DOMAIN && \
  rm -Rf /etc/letsencrypt/renewal/$PRIMARY_DOMAIN.conf" certbot

# 4) Valódi tanúsítvány kérése a Let's Encrypttől.
echo "### Let's Encrypt tanúsítvány kérése ..."
DOMAIN_ARGS=""
for d in $DOMAINS; do
  DOMAIN_ARGS="$DOMAIN_ARGS -d $d"
done

case "$EMAIL" in
  "") EMAIL_ARG="--register-unsafely-without-email" ;;
  *)  EMAIL_ARG="--email $EMAIL" ;;
esac

if [ "$STAGING" != "0" ]; then STAGING_ARG="--staging"; fi

docker compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $STAGING_ARG $EMAIL_ARG $DOMAIN_ARGS \
    --rsa-key-size $RSA_KEY_SIZE \
    --agree-tos \
    --force-renewal" certbot

# 5) Nginx újratöltése a valódi tanúsítvánnyal.
echo "### Nginx újratöltése ..."
docker compose exec ccs_frontend nginx -s reload

echo "### Kész. Indítsd az egészet: docker compose up -d"
