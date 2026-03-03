# Nanobot Manager #

La V0.1 fait exactement le travail attendu.

- Ça lit les modèles dispo sur Ollama en local
- Ça lit les providers configurés pour nanobot
- Ça met à jour le fichier de config
- Ça relance le container docker

L'URL est accessible sur le port 8899 de la machine
http://IP_DE_LA_MACHINE:8899

``
Structure du projet

compose.yaml  (ou ajout dans le compose nanobot)
nanobot-manager/
├── app.py
├── templates/
│   └── index.html
├── requirements.txt
└── Dockerfile
``

## Initialisation ##

Valider la création de l'image du container

``
docker compose -f $PWD/compose.yaml build
``

Lancer le container en autonome

``
docker compose -f $PWD/compose.yaml up -d
``

## Todo ##

- rendre le port paramétrable
- ajouter un light/dark mode
- faire le café
