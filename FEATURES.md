# Nanobot Manager - Fonctionnalités Complètes

## 📋 Vue d'ensemble

Nanobot Manager est une interface web complète pour gérer les agents IA de Nanobot. Il permet de :
- Configurer les modèles, providers et contextes
- Gérer l'exécution (Docker container ou service Host)
- Générer et gérer des clés SSH
- Consulter les logs en temps réel
- Persister la configuration via fichier `.env`

## ✨ Fonctionnalités principales

### 1. Configuration par Défaut
Configure le modèle et provider par défaut pour tous les agents Nanobot.

**Paramètres:**
- **Provider**: Sélection du fournisseur (custom, openai, anthropic, openrouter)
- **Modèle**: Liste des modèles Ollama ou saisie manuelle

**Utilité**: Définit le comportement par défaut lorsqu'un agent n'a pas de configuration spécifique.

---

### 2. Configuration Coder 🔧
Optimise la configuration spécifiquement pour la génération et l'analyse de code.

**Paramètres:**
- **Provider**: Fournisseur d'IA (custom, openai, anthropic, openrouter)
- **Modèle**: Modèle dédié pour le code (ex: `qwen3.5:9b-16k`, `gpt-4-turbo`)
- **Contexte (maxTokens)**: Taille maximale du contexte

**Valeurs de contexte prédéfinies:**
- **2K** (Conversation rapide) - Pour des snippets courts
- **4K** (Standard) - Pour des fichiers de taille normale
- **8K** (Code long) - Pour des fichiers de taille moyenne
- **16K** (Code complet) - Pour les projets plus larges ⭐ *Recommandé*
- **32K** (Très long) - Pour analyser plusieurs fichiers
- **64K** (Ultra long) - Pour des bases de code complètes
- **128K** (Maximum) - Pour les plus grands contextes
- **Personnalisé** - Entrée manuelle

**Utilité**: Nanobot utilise ce modèle avec ce contexte quand il génère ou analyse du code.

---

### 3. Configuration Vision 👁️
Optimise la configuration pour l'analyse d'images et la vision par ordinateur.

**Paramètres:**
- **Provider**: Fournisseur d'IA
- **Modèle**: Modèle compatible avec la vision (ex: `llava`, `gpt-4-vision`)
- **Contexte (maxTokens)**: *(Optionnel)* - Taille du contexte pour l'analyse

**Valeurs de contexte:**
- **Aucun** (par défaut) - Utilise la valeur par défaut du modèle
- **2K** (Rapide)
- **4K** (Standard)
- **8K** (Détaillé)
- **16K** (Très détaillé)
- **32K** (Analyse complète)
- **Personnalisé** - Entrée manuelle

**Utilité**: Nanobot utilise ce modèle quand il analyse des images, des captures d'écran ou des diagrammes.

---

### 4. Paramètres & Exécution ⚙️ (NOUVEAU)

Onglet centralisé pour gérer l'exécution de nanobot-gateway.

**Sections:**
- **🔄 Mode d'exécution** : Sélectionner Docker ou Machine hôte
- **🔑 Clé SSH** : Générer/copier clés SSH pour mode Host
- **📜 Logs** : Afficher les 100 dernières lignes (Docker ou SSH)

**Utilité**: Configuration centralisée de tous les paramètres système.

---

## 🎨 Interface utilisateur

### Navigation par onglets
L'interface est organisée en **4 onglets** pour faciliter la navigation:
- **Par Défaut** - Configuration globale
- **🔧 Coder** - Configuration pour la génération de code
- **👁️ Vision** - Configuration pour l'analyse d'images
- **⚙️ Paramètres** - Gestion du système, SSH, logs

### Indicateur de configuration actuelle
Chaque onglet affiche un badge avec la configuration actuelle:
```
Config actuelle — Provider : openai | Modèle : gpt-4-turbo
```

### Gestion des tokens
- Sélection par dropdown avec valeurs prédéfinies
- Option de saisie manuelle en cliquant sur "✏️ Personnalisé..."
- Validation automatique (valeur doit être > 0)

---

## 🔄 Actions disponibles

### Sauvegarder la configuration
Chaque onglet a un bouton "💾 Sauvegarder" qui:
1. Valide les données saisies
2. Envoie une requête à l'API (`/api/{agent}/update`)
3. Affiche un message de confirmation
4. Met à jour le badge de configuration actuelle

### Redémarrer nanobot-gateway
- Bouton "🔄 Redémarrer Nanobot" (en bas)
- **Mode Docker** : Redémarre le container via Docker API
- **Mode Host** : Redémarre le service via SSH + systemctl
- Adapte automatiquement selon la configuration
- Affiche le statut du redémarrage

### Générer une clé SSH
- Bouton "🔑 Générer une clé SSH" dans l'onglet **⚙️ Paramètres**
- Génère une paire de clés ed25519
- Affiche la clé publique pour la copier
- Bouton "📋 Copier" intégré
- Persiste dans `~/.ssh/nanobot-manager/`

### Consulter les logs
- Bouton "🔄 Rafraîchir les logs" dans l'onglet **⚙️ Paramètres**
- Affiche les **100 dernières lignes** de nanobot-gateway
- **Mode Docker** : Récupère les logs du container
- **Mode Host** : Récupère les logs via `journalctl --user`
- Affichage scrollable avec police monospace

---

## 📡 API Endpoints

### Configuration des Agents
- `GET /api/config` - Récupérer configuration par défaut
- `GET /api/models` - Récupérer les modèles Ollama
- `POST /api/update` - Mettre à jour modèle/provider par défaut
- `GET /api/coder` - Récupérer configuration Coder
- `POST /api/coder/update` - Mettre à jour configuration Coder
- `GET /api/vision` - Récupérer configuration Vision
- `POST /api/vision/update` - Mettre à jour configuration Vision

### Paramètres & Exécution
- `GET /api/execution-type` - Récupérer le mode (docker ou host)
- `POST /api/execution-type/update` - Changer le mode d'exécution
- `POST /api/restart` - Redémarrer nanobot-gateway

### SSH & Gestion des Clés
- `GET /api/ssh-key` - Récupérer la clé SSH publique
- `POST /api/ssh-key/generate` - Générer une nouvelle paire de clés SSH

### Logs & Diagnostic
- `GET /api/logs` - Récupérer les logs de nanobot-gateway

---

## ⚙️ Structure de configuration (config.json)

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
      "maxTokens": 16384
    },
    "vision": {
      "model": "gpt-4-vision",
      "provider": "openai",
      "maxTokens": 8192
    }
  }
}
```

---

## 💡 Cas d'usage recommandés

### Scénario 1: Développement local avec Ollama
```
Defaults: qwen3.5:9b-16k (custom/Ollama)
Coder:    qwen3.5:9b-16k (custom/Ollama, 16K tokens)
Vision:   llava (custom/Ollama)
```

### Scénario 2: Production avec OpenAI
```
Defaults: gpt-4-turbo (openai)
Coder:    gpt-4-turbo (openai, 32K tokens)
Vision:   gpt-4-vision (openai, 16K tokens)
```

### Scénario 3: Hybride (Local + Cloud)
```
Defaults: qwen3.5 (custom/Ollama)
Coder:    gpt-4-turbo (openai, 32K tokens) - Meilleur pour le code
Vision:   gpt-4-vision (openai, 16K tokens) - Meilleur pour les images
```

---

## 🔐 Notes de sécurité

- Les configurations sont stockées dans `/opt/stacks/nanobot/config/config.json`
- Les API keys ne sont pas gérées par Nanobot Manager
- Les validations sont effectuées côté serveur
- Aucune donnée sensible n'est sauvegardée dans le navigateur

---

## 🔧 Configuration via `.env` (NOUVEAU)

Le fichier `.env` permet une persistance des paramètres lors des mises à jour:

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos valeurs
CONFIG_PATH=/opt/stacks/nanobot/config/config.json
OLLAMA_URL=http://ollama:11434
DOCKER_PROXY_URL=http://socket-proxy-nbt-mngr:2375
HOST_SSH_USER=your_username
HOST_SSH_HOST=localhost
HOST_SSH_PORT=22
```

**Avantage** : Les variables persistent après `git pull` et mises à jour.

---

## 🐛 Dépannage

### Configuration ne s'applique pas
1. Sauvegarder la configuration dans l'onglet approprié
2. Cliquer sur "🔄 Redémarrer Nanobot"
3. Attendre le redémarrage (Docker ou SSH selon mode)
4. Vérifier les logs dans l'onglet **⚙️ Paramètres** → **📜 Logs**

### Erreurs lors de la sauvegarde
- Vérifier que le provider et le modèle sont non vides
- S'assure que maxTokens est un nombre positif
- Vérifier que le fichier de configuration est accessible

### Les modèles Ollama n'apparaissent pas
- Vérifier que Ollama est en cours d'exécution
- Vérifier l'URL Ollama dans `.env` : `curl $OLLAMA_URL/api/tags`
- Les modèles doivent être préalablement téléchargés : `ollama pull llama2`

### Mode Host : Erreur SSH
- Vérifier la clé SSH est générée (voir logs)
- Vérifier la clé publique dans `~/.ssh/authorized_keys` sur l'hôte
- Vérifier permissions SSH : `chmod 600 ~/.ssh/authorized_keys`
- Tester SSH manuellement : `ssh -v user@host "systemctl --user status nanobot-gateway"`

### Volume SSH Read-only
- Vérifier que `compose.yaml` n'a **PAS** `:ro` sur le volume SSH
- Doit être : `~/.ssh/nanobot-manager:/root/.ssh` (sans :ro)
- Sinon impossible de générer les clés

---

## 📚 Références

- [Documentation officielle Nanobot](https://github.com/HKUDS/nanobot)
- [EXECUTION_MODES.md](EXECUTION_MODES.md) - Guide détaillé Docker vs Host
- [AGENTS.md](AGENTS.md) - Conventions de code

---

**Dernière mise à jour**: 2026-03-06  
**Version**: 0.3 (Paramètres, SSH, Logs, Docker/Host)
