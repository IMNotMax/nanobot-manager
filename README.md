# 🐈 Nanobot Manager v0.9

Interface web intuitive pour configurer et gérer les agents IA de [Nanobot](https://github.com/HKUDS/nanobot).

## ✨ Fonctionnalités

### Configuration Multi-Agents
Nanobot Manager permet de configurer **trois types d'agents** de manière indépendante:

- **⚡ Général** - Configuration globale utilisée par tous les agents
- **🔧 Coder** - Optimisé pour la génération et l'analyse de code
- **👁️ Vision** - Optimisé pour l'analyse d'images et la vision par ordinateur

### Configuration Rapide & Avancée
- **Mode Rapide** : Configuration simplifiée avec les paramètres essentiels
- **Mode Avancé** : Accès à tous les paramètres (workspace, MCP servers, etc.)

### Paramètres Configurables

#### Tous les agents
- **Provider**: Sélection dynamique depuis les providers configurés dans nanobot
- **Modèle**: Liste des modèles Ollama ou saisie manuelle selon le provider
- **Contexte (maxTokens)**: Slider avec valeurs prédéfinies (2K à 128K)
- **Température**: Slider de 0 à 2

### Autre Fonctionnalités
- 📡 Lecture dynamique des providers depuis `config.json` de nanobot
- 🔄 Redémarrage du container `nanobot-gateway` (Docker ou Host via SSH)
- 💾 Sauvegarde automatique dans `config.json`
- 🎨 Interface dark mode responsive et moderne
- 🔐 Configuration des providers (clé API, URL de base)
- 📜 Visualisation des logs en temps réel
- 🔑 Génération de clés SSH pour le mode Host

## 🚀 Installation

### Prérequis
- Docker & Docker Compose
- Nanobot configuré et en cours d'exécution
- Accès au fichier de configuration Nanobot (`~/.nanobot/config.json`)

### Démarrage

1. **Récupérer UID/GID pour les permissions**
```bash
echo "PUID=$(id -u)" >> .env
echo "PGID=$(id -g)" >> .env
```

2. **Configurer le fichier `.env`**
```bash
cp .env.example .env
# Éditer les variables selon votre configuration
```

3. **Lancer le container**
```bash
docker compose up -d --build
```

4. **Accéder à l'interface**
```
http://localhost:8899
```

### Configuration via Variables d'Environnement

```bash
# Permissions utilisateur (IMPORTANT)
PUID=1001
PGID=1001

# URL de l'instance Ollama
OLLAMA_URL=http://192.168.2.220:11434

# URL du proxy Docker Socket
DOCKER_PROXY_URL=http://socket-proxy-nbt-mngr:2375

# SSH pour le mode Host
HOST_SSH_USER=agent_smith
HOST_SSH_HOST=192.168.2.202
HOST_SSH_PORT=22

# Mode debug (optionnel)
DEBUG=false
```

## 📋 Structure du Projet

```
nanobot-manager/
├── nanobot-manager/
│   ├── app.py              # Application Flask (routes API)
│   ├── requirements.txt   # Dépendances Python
│   ├── Dockerfile         # Image Docker
│   └── templates/
│       └── index.html    # Interface web
├── compose.yaml           # Configuration Docker Compose
├── .env.example           # Template de configuration
├── .gitignore
├── README.md
├── FEATURES.md
└── AGENTS.md
```

## 🎯 Workflow Typique

1. **Configurer les providers** (si nécessaire)
   - Aller dans "⚙️ Paramètres" → "🔌 Configuration des Providers"
   - Ajouter les clés API

2. **Configurer l'agent Général**
   - Aller dans "⚡ Général"
   - Choisir le provider et le modèle
   - Configurer contexte et température
   - Sauvegarder

3. **Configurer les agents Coder et Vision**
   - Procéder de même pour chaque onglet

4. **Redémarrer Nanobot**
   - Cliquer "🔄 Redémarrer Nanobot"

## 🔌 API Endpoints

### Configuration
- `GET /api/providers` - Liste des providers avec statut
- `GET /api/config` - Configuration de l'agent Général
- `POST /api/update` - Mettre à jour l'agent Général
- `GET /api/coder` - Configuration Coder
- `POST /api/coder/update` - Mettre à jour Coder
- `GET /api/vision` - Configuration Vision
- `POST /api/vision/update` - Mettre à jour Vision
- `GET /api/models` - Modèles Ollama disponibles
- `GET /api/ollama-config` - Configuration Ollama

### Système
- `GET /api/execution-type` - Type d'exécution (docker/host)
- `POST /api/execution-type/update` - Changer le type
- `GET /api/ssh-key` - Clé SSH publique
- `POST /api/ssh-key/generate` - Générer une clé SSH
- `GET /api/logs` - Logs de nanobot-gateway
- `POST /api/restart` - Redémarrer nanobot-gateway

### Configuration Avancée
- `GET /api/config/full` - Configuration complète
- `POST /api/config/advanced` - Paramètres avancés
- `POST /api/provider/config` - Configurer un provider
- `DELETE /api/provider/config` - Supprimer un provider

## 🐛 Dépannage

### Les providers n'apparaissent pas
- Vérifier que `~/.nanobot/config.json` contient une section `providers`

### Erreurs de permission sur config.json
- Vérifier que PUID/PGID sont correctement configurés dans `.env`
- Vérifier les droits sur le fichier: `ls -la ~/.nanobot/config.json`

### SSH erreur "No user exists for uid"
- Le container doit être lancé avec `user: "${PUID:-1000}:${PGID:-1000}"` dans compose.yaml

### Logs non accessibles en mode Host
- Vérifier que la clé SSH est correctement configurée sur l'hôte
- Vérifier que `HOST_SSH_USER` est configuré

## 🔐 Sécurité

- ✅ Validation côté serveur de tous les champs
- ✅ Aucune clé API stockée (dans le fichier nanobot)
- ✅ Aucune donnée sensible en navigateur
- ✅ Support de Docker Socket Proxy
- ✅ Configuration en lecture seule du fichier nanobot (sauf modifications explicites)

---

**Version**: 0.9  
**Dernière mise à jour**: 2026-03-19  
**Support Nanobot**: v0.1.4+
