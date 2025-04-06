#!/bin/bash
# daily_report.sh : Génère un rapport quotidien en CSV

TODAY=$(date +'%Y-%m-%d')
DATA_FILE="/home/ec2-user/Projet_DogeCoin/data.csv"
OUTPUT_FILE="/home/ec2-user/Projet_DogeCoin/daily_report.csv"

# Extraire les données d'aujourd'hui depuis data.csv et les sauvegarder dans un fichier temporaire
grep "^$TODAY" "$DATA_FILE" > /home/ec2-user/Projet_DogeCoin/data_today.csv

if [ -s /home/ec2-user/Projet_DogeCoin/data_today.csv ]; then
    # Le prix d'ouverture est celui du premier enregistrement, et le prix de clôture celui du dernier.
    OPEN=$(head -n 1 /home/ec2-user/Projet_DogeCoin/data_today.csv | cut -d',' -f2 | tr -d ' ')
    CLOSE=$(tail -n 1 /home/ec2-user/Projet_DogeCoin/data_today.csv | cut -d',' -f2 | tr -d ' ')
    
    if [[ "$OPEN" != "N/A" && "$OPEN" != "0" ]]; then
         VOLATILITY=$(echo "scale=2; (($CLOSE - $OPEN) / $OPEN) * 100" | bc)
    else
         VOLATILITY="N/A"
    fi
    
    # Écrire l'en-tête et la ligne de données formatée dans le fichier CSV
    echo "date,open,close,volatility" > "$OUTPUT_FILE"
    echo "$TODAY,$OPEN,$CLOSE,$VOLATILITY%" >> "$OUTPUT_FILE"
else
    echo "date,open,close,volatility" > "$OUTPUT_FILE"
    echo "$TODAY,No data,No data,No data" >> "$OUTPUT_FILE"
fi
