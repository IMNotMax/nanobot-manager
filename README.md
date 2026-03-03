# Nanobot Manager #

La V0.1 fait exactement le travail attendu.

- Ça lit les modèles dispo sur Ollama en local
- Ça lit les providers configurés pour nanobot
- Ça met à jour le fichier de config
- Ça relance le container docker

Structure du projet

compose.yaml  (ou ajout dans le compose nanobot)
nanobot-manager/
├── app.py
├── templates/
│   └── index.html
├── requirements.txt
└── Dockerfile
