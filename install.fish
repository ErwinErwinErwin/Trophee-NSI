#!/usr/bin/env fish

# Mettre à jour la liste des paquets et installer python et python-venv si besoin
sudo apt update
sudo apt install -y python3-pip python3-venv

# Créer un environnement virtuel
python3 -m venv .venv

# Activer l’environnement
source .venv/bin/activate.fish

# Installation des paquets
pip3 install -r requirements.txt

echo "Installation completed successfully."