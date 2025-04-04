#!/bin/bash

URL="https://api.coingecko.com/api/v3/simple/price?ids=dogecoin&vs_currencies=usd"
RESPONSE=$(curl -s "$URL")

# Debug : afficher la réponse JSON
echo "Réponse API : $RESPONSE" >> debug.log

PRICE=$(echo "$RESPONSE" | grep -oP '(?<="usd":)[0-9]+(\.[0-9]+)?')

if [ -z "$PRICE" ]; then
    PRICE="N/A"
fi

TIMESTAMP=$(date +'%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP,$PRICE" >> data.csv
echo "[$TIMESTAMP] Dogecoin USD = $PRICE"
