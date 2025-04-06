#!/bin/bash
# daily_report.sh : Génère un rapport quotidien à partir de data.csv

# Définir la date d'aujourd'hui au format YYYY-MM-DD
TODAY=$(date +'%Y-%m-%d')

# Filtrer les lignes de data.csv pour la date d'aujourd'hui
grep "^$TODAY" /home/ec2-user/Projet_DogeCoin/data.csv > /home/ec2-user/Projet_DogeCoin/data_today.csv

# Vérifier si des données ont été collectées pour aujourd'hui
if [ -s /home/ec2-user/Projet_DogeCoin/data_today.csv ]; then
    # Le prix d'ouverture est le premier enregistrement
    OPEN=$(head -n 1 /home/ec2-user/Projet_DogeCoin/data_today.csv | cut -d',' -f2)
    # Le prix de clôture est le dernier enregistrement
    CLOSE=$(tail -n 1 /home/ec2-user/Projet_DogeCoin/data_today.csv | cut -d',' -f2)
    
    # Calculer la volatilité en pourcentage (si OPEN est numérique)
    if [[ "$OPEN" != "N/A" && "$OPEN" != "0" ]]; then
        VOLATILITY=$(echo "scale=2; (($CLOSE - $OPEN) / $OPEN) * 100" | bc)
    else
        VOLATILITY="N/A"
    fi
    
    # Écrire le rapport quotidien dans un fichier
    echo "$TODAY, Open: $OPEN, Close: $CLOSE, Volatility: $VOLATILITY%" > /home/ec2-user/Projet_DogeCoin/daily_report.csv
else
    echo "$TODAY, Aucune donnée disponible" > /home/ec2-user/Projet_DogeCoin/daily_report.csv
fi
