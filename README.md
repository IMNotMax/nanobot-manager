# 🐈 Nanobot Manager

Interface web intuitive pour configurer et gérer les agents IA de [Nanobot](https://github.com/HKUDS/nanobot).

## ✨ Fonctionnalités

### Configuration Multi-Agents

Nanobot Manager permet de configurer **trois types d'agents** de manière indépendante:

- **Par Défaut** - Configuration globale utilisée par tous les agents
- **🔧 Coder** - Optimisé pour la génération et l'analyse de code
- **👁️ Vision** - Optimisé pour l'analyse d'images et la vision par ordinateur

<p align="center">
  <img src="img/Default.png" width="50%" />
</p>

### Paramètres Configurables

#### Tous les agents

- **Provider**: Sélection du fournisseur (OpenAI, Anthropic, OpenRouter, custom Ollama)
- **Modèle**: Choisir parmi les modèles Ollama disponibles ou saisir manuellement

#### Agent Coder & Vision

- **Contexte (maxTokens)**: Taille maximale du contexte avec **8 valeurs prédéfinies**
  - 2K, 4K, 8K, 16K (par défaut), 32K, 64K, 128K
  - Support des valeurs personnalisées
- Vision: maxTokens est optionnel (conforme à la spec Nanobot)

### Autres Fonctionnalités

- 📡 Lecture des modèles disponibles sur Ollama en temps réel
- 🔄 Redémarrage de nanobot-gateway directement depuis l'interface
  - **Mode Docker**: Via l'API Docker Socket Proxy
  - **Mode Host**: Via SSH + systemctl sur la machine hôte
- ⚙️ **Paramètres** (nouvel onglet):
  - **Sélection du mode d'exécution** (Docker ou Machine hôte)
  - **Génération et gestion des clés SSH** (1-clic)
  - **Lecteur de logs** (Docker ou SSH, 100 dernières lignes)
- 💾 Sauvegarde automatique dans `config.json`
- 🎨 Interface dark mode responsive et moderne
- ✅ Validation complète côté serveur
- 📄 Configuration via fichier `.env` pour persistance

## 🚀 Quick Start

### Prérequis

- Docker & Docker Compose
- Nanobot configuré et en cours d'exécution
- Accès au fichier de configuration Nanobot

### Démarrage Rapide

1. **Copier le fichier de configuration**

```bash
cp .env.example .env
```

1. **Éditer `.env` avec vos paramètres**

```bash
# .env
OLLAMA_URL=http://ollama:11434
DOCKER_PROXY_URL=http://socket-proxy-nbt-mngr:2375
HOST_SSH_USER=your_username
HOST_SSH_HOST=localhost
HOST_SSH_PORT=22
HTTP_PORT=8899
```

1. **Construire et lancer**

```bash
docker compose build --no-cache
docker compose up -d
```

1. **Accéder à l'interface**

```
http://localhost:8899
```

### Configuration via Fichier `.env` (Recommandé)

Le fichier `.env` permet une persistance des paramètres lors des mises à jour. Copiez `.env.example` en `.env` et personnalisez :

```bash
# URL de l'instance Ollama
OLLAMA_URL=http://ollama:11434

# Mode Docker (Socket Proxy)
DOCKER_PROXY_URL=http://socket-proxy-nbt-mngr:2375

# Mode Host (SSH + systemctl)
HOST_SSH_USER=your_username          # Utilisateur sur l'hôte
HOST_SSH_HOST=localhost              # Adresse/hostname de l'hôte
HOST_SSH_PORT=22                     # Port SSH

# Port Flask
HTTP_PORT=8899
```

## 📋 Configuration Complète

### Structure du Projet

```
nanobot-manager/
├── app.py                    # Application Flask (routes API)
├── requirements.txt          # Dépendances Python
├── Dockerfile               # Image Docker
├── templates/
│   └── index.html          # Interface web
└── .gitignore

compose.yaml                 # Configuration Docker Compose
README.md                    # Ce fichier
FEATURES.md                  # Documentation détaillée des fonctionnalités
TESTING_GUIDE.md            # Guide de test
AGENTS.md                    # Conventions de code pour les agents
```

### Fichier config.json (Structure)

Après configuration via Nanobot Manager, votre `config.json` ressemblera à:

```json
{
  "agents": {
    "defaults": {
      "model": "gpt-4-turbo",
      "provider": "openai"
    },
    "coder": {
      "model": "gpt-4-turbo",
      "provider": "openai",
      "maxTokens": 32768
    },
    "vision": {
      "model": "gpt-4-vision",
      "provider": "openai",
      "maxTokens": 16384
    }
  },
  "channels": { ... },
  "providers": { ... },
  "tools": { ... }
}
```

## 🎯 Cas d'Usage

### Scenario 1: Développement Local avec Ollama

```json
{
  "agents": {
    "defaults": {
      "model": "qwen3.5:9b-16k",
      "provider": "custom"
    },
    "coder": {
      "model": "qwen3.5:9b-16k",
      "provider": "custom",
      "maxTokens": 16384
    },
    "vision": {
      "model": "llava",
      "provider": "custom"
    }
  }
}
```

### Scenario 2: Production avec OpenAI

```json
{
  "agents": {
    "defaults": {
      "model": "gpt-4-turbo",
      "provider": "openai"
    },
    "coder": {
      "model": "gpt-4-turbo",
      "provider": "openai",
      "maxTokens": 32768
    },
    "vision": {
      "model": "gpt-4-vision",
      "provider": "openai",
      "maxTokens": 16384
    }
  }
}
```

### Scenario 3: Hybride (Meilleur des deux mondes)

```json
{
  "agents": {
    "defaults": {
      "model": "qwen3.5:9b-16k",
      "provider": "custom"
    },
    "coder": {
      "model": "gpt-4-turbo",
      "provider": "openai",
      "maxTokens": 32768
    },
    "vision": {
      "model": "gpt-4-vision",
      "provider": "openai",
      "maxTokens": 16384
    }
  }
}
```

## 🔌 API Endpoints

### Configuration des Agents

- `GET /api/config` - Récupérer la configuration par défaut
- `GET /api/models` - Récupérer les modèles Ollama disponibles
- `POST /api/update` - Mettre à jour le modèle/provider par défaut
- `GET /api/coder` - Récupérer la configuration Coder
- `POST /api/coder/update` - Mettre à jour la configuration Coder
- `GET /api/vision` - Récupérer la configuration Vision
- `POST /api/vision/update` - Mettre à jour la configuration Vision

### Paramètres & Exécution

- `GET /api/execution-type` - Récupérer le mode d'exécution (docker ou host)
- `POST /api/execution-type/update` - Configurer le mode d'exécution
- `POST /api/restart` - Redémarrer nanobot-gateway (adapte le mode automatiquement)

### SSH Key Management

- `GET /api/ssh-key` - Récupérer la clé SSH publique
- `POST /api/ssh-key/generate` - Générer une nouvelle paire de clés SSH

### Logs & Diagnostic

- `GET /api/logs` - Récupérer les logs de nanobot-gateway (Docker ou SSH)

## 🧪 Tester Localement

### Sans Docker

```bash
# Installer les dépendances
pip install -r nanobot-manager/requirements.txt

# Lancer l'application
cd nanobot-manager
python3 app.py
```

L'application sera accessible à `http://localhost:8899`

### Avec Docker

```bash
# Construire
docker compose build

# Lancer
docker compose up -d

# Voir les logs
docker compose logs -f nanobot-manager

# Arrêter
docker compose down
```

## 📚 Documentation

- **[FEATURES.md](FEATURES.md)** - Description complète de toutes les fonctionnalités
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Guide de test avec checklists
- **[AGENTS.md](AGENTS.md)** - Conventions de code pour les agents développeurs

## 🔐 Sécurité

- ✅ Validation côté serveur de tous les champs
- ✅ Pas de gestion des API keys (utiliser le config.json directement)
- ✅ Aucune donnée sensible stockée en navigateur
- ✅ Messages d'erreur informatifs
- ✅ Support de Docker Socket Proxy pour l'accès sécurisé

## 🐛 Dépannage

### Configuration ne s'applique pas

1. Vérifier la sauvegarde dans l'onglet approprié
2. Cliquer sur "🔄 Redémarrer Nanobot"
3. Attendre le redémarrage
4. Vérifier les logs: `docker compose logs nanobot-manager`

### Les modèles Ollama n'apparaissent pas

- Vérifier que Ollama est en cours d'exécution
- Vérifier l'URL Ollama: `curl $OLLAMA_URL/api/tags`
- Les modèles doivent être téléchargés: `ollama pull llama2`

### Mode Host: Erreur "SSH error" ou "Host not reachable"

- Vérifier que la clé SSH est générée: `docker exec nanobot-manager ls -la /root/.ssh/`
- Vérifier que la clé publique est dans `~/.ssh/authorized_keys` sur l'hôte
- Tester la connexion SSH depuis le container:

  ```bash
  docker exec nanobot-manager ssh -o StrictHostKeyChecking=no user@localhost "systemctl --user status nanobot-gateway"
  ```

- Vérifier les permissions: `chmod 600 ~/.ssh/authorized_keys`

### Erreurs de permission

- Vérifier l'accès au fichier config.json
- Vérifier les permissions Docker: `docker ps` (mode Docker)
- Vérifier le socket proxy: `curl $DOCKER_PROXY_URL/version` (mode Docker)
- Vérifier les logs SSH: `docker exec nanobot-manager ssh -v ...` (mode Host)

### Port 8899 déjà en utilisation

```bash
# Trouver le processus
lsof -i :8899

# Ou modifier dans compose.yaml:
# ports:
#   - "8900:8899"  # Nouveau port
```

## 🔄 Workflow Typique

### Mode Docker (Recommandé pour commencer)

1. **Configuration initiale** (une seule fois)
   - Aller à l'onglet **⚙️ Paramètres**
   - Sélectionner **🐳 Docker (Container)**
   - Sauvegarder les paramètres

2. **Configurer les agents**
   - Onglet **Par Défaut** : sélectionner provider et modèle
   - Onglet **🔧 Coder** : configurer le modèle et tokens
   - Onglet **👁️ Vision** : configurer le modèle vision
   - Cliquer "💾 Sauvegarder" après chaque onglet

3. **Redémarrer & Vérifier**
   - Cliquer **🔄 Redémarrer Nanobot**
   - Attendre le redémarrage du container
   - Les badges affichent la configuration actuelle

### Mode Host (Machine hôte avec systemctl)

1. **Setup SSH (une seule fois)**
   - Aller à **⚙️ Paramètres** → Section **🔑 Clé SSH**
   - Cliquer **[🔑 Générer une clé SSH]**
   - Cliquer **[📋 Copier]**
   - Sur l'hôte : `echo "clé" >> ~/.ssh/authorized_keys`

2. **Configurer le mode**
   - Aller à **⚙️ Paramètres** → Section **🔄 Mode d'exécution**
   - Sélectionner **🖥️ Machine hôte (Systemctl)**
   - Sauvegarder les paramètres

3. **Configurer les agents & redémarrer** (même qu'en Docker)
   - Configurer chaque agent (Par Défaut, Coder, Vision)
   - Cliquer **🔄 Redémarrer Nanobot**
   - Redémarrage via SSH + systemctl

## 📈 Performance & Limitations

- ✅ Interface responsive sur tous les appareils
- ✅ Chargement < 2s pour chaque onglet
- ✅ Support de contextes jusqu'à 128K tokens
- ✅ Validation automatique de tous les champs
- ⚠️ Nécessite Docker pour le redémarrage du container
- ⚠️ Ollama doit être accessible pour charger les modèles

## 🤝 Contribution

Les contributions sont bienvenues! Consultez [AGENTS.md](AGENTS.md) pour les conventions de code.

### Développement

```bash
git clone https://github.com/IMNotMax/nanobot-manager.git
cd nanobot-manager
pip install -r nanobot-manager/requirements.txt
cd nanobot-manager
python3 app.py  # Démarrer le serveur
```

## 📄 Licence

Ce projet est fourni tel quel pour la gestion de Nanobot.

## 🙋 Support

- 📖 Consultez la [documentation Nanobot officielle](https://github.com/HKUDS/nanobot)
- 🐛 Signalez les bugs dans les issues GitHub
- 💬 Questions? Consultez [FEATURES.md](FEATURES.md) ou [TESTING_GUIDE.md](TESTING_GUIDE.md)

## 🗺️ Roadmap

- [ ] Mode clair/sombre amélioré
- [x] Port configurable
- [ ] Export/import de configurations
- [ ] Historique des modification
- [ ] Support multilingue

---

**Dernière mise à jour**: 2026-03-06  
**Version**: 0.3 (Paramètres, SSH, Logs, Docker/Host)  
**Support Nanobot**: v0.1.4+
