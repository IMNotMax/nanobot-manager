# Nanobot Manager - Fonctionnalités

## 📋 Vue d'ensemble

Nanobot Manager v0.9 est une interface web pour configurer les agents IA de [Nanobot](https://github.com/HKUDS/nanobot). Il permet de gérer les modèles, providers, et paramètres d'exécution via une interface intuitive.

**Configuration isolée**: Nanobot Manager utilise un fichier `manager.json` séparé pour ses propres paramètres, évitant de modifier la configuration principale de nanobot.

---

## 🎛️ Onglets de configuration

### ⚡ Général
Configuration globale utilisée par tous les agents nanobot par défaut.

**Mode Rapide:**
- Provider: Sélection dynamique depuis `config.json` de nanobot
- Modèle: Liste des modèles Ollama ou saisie manuelle
- Contexte (maxTokens): Slider 2K à 128K
- Température: Slider 0 à 2

**Mode Avancé:**
- Workspace path personnalisé
- MCP Servers (JSON)
- Execution Type override
- Extra Args

### 🔧 Coder
Configuration optimisée pour la génération et l'analyse de code.

**Paramètres:**
- Provider dynamique (custom, openai, anthropic, openrouter, etc.)
- Modèle dédié (ex: `qwen3.5:9b-16k`, `gpt-4-turbo`)
- Contexte (maxTokens): 2K à 128K ⭐ *Recommandé: 16K*

### 👁️ Vision
Configuration optimisée pour l'analyse d'images et la vision par ordinateur.

**Paramètres:**
- Provider dynamique
- Modèle compatible vision (ex: `llava`, `gpt-4-vision`)
- Contexte optionnel

### ⚙️ Paramètres
Gestion des paramètres système et de connexion.

#### Exécution
- **Type**: Docker ou Host (SSH)
- Affichage du type actuel

#### 🔌 Configuration des Providers
- Liste des providers disponibles
- Statut: ✅ Configuré / ❌ Non configuré
- Configuration de l'API Key et apiBase pour chaque provider

#### 🔑 Clé SSH
- Affichage de la clé publique actuelle
- Génération de nouvelle clé
- Utilisé pour le mode Host

#### 📡 Statut Ollama
- URL apiBase configurée
- Bouton de rafraîchissement des modèles

---

## 🔄 Mode Rapide / Avancé

### Mode Rapide (Quick Config)
Configuration simplifiée avec les paramètres essentiels:
- Provider et modèle
- Contexte et température

### Mode Avancé
Accès complet à tous les paramètres nanobot:
- Workspace path
- MCP Servers (Model Context Protocol)
- Execution Type override
- Extra Arguments

**Activation**: Toggle en haut de l'onglet Général

---

## 📡 API Endpoints

### Providers
- `GET /api/providers` - Liste des providers avec statut de configuration
- `POST /api/provider/config` - Configurer un provider (apiKey, apiBase)
- `DELETE /api/provider/config` - Supprimer un provider

### Configuration
- `GET /api/config` - Configuration de l'agent Général
- `POST /api/update` - Mettre à jour l'agent Général
- `GET /api/coder` - Configuration Coder
- `POST /api/coder/update` - Mettre à jour Coder
- `GET /api/vision` - Configuration Vision
- `POST /api/vision/update` - Mettre à jour Vision
- `GET /api/models` - Modèles Ollama disponibles
- `GET /api/ollama-config` - Configuration Ollama (apiBase)

### Configuration Avancée
- `GET /api/config/full` - Configuration complète de l'agent
- `POST /api/config/advanced` - Paramètres avancés (workspace, mcpServers, etc.)

### Système
- `GET/POST /api/execution-type` - Type d'exécution (docker/host)
- `GET /api/ssh-key` - Clé SSH publique
- `POST /api/ssh-key/generate` - Générer une clé SSH
- `GET /api/logs` - Logs de nanobot-gateway
- `POST /api/restart` - Redémarrer nanobot-gateway

---

## ⚙️ Structure de configuration

### config.json (nanobot principal)
```json
{
  "providers": {
    "custom": { "apiKey": "...", "apiBase": "http://..." },
    "openai": { "apiKey": "sk-..." }
  },
  "agents": {
    "defaults": { "model": "qwen3.5:9b-16k", "provider": "custom" },
    "coder": { "model": "gpt-4-turbo", "provider": "openai", "maxTokens": 16384 },
    "vision": { "model": "gpt-4-vision", "provider": "openai" }
  }
}
```

### manager.json (nanobot-manager)
```json
{
  "execution_type": "docker",
  "general_agent": { ... },
  "coder_agent": { ... },
  "vision_agent": { ... }
}
```

---

## 🚀 Cas d'usage recommandés

### Scénario 1: Développement local avec Ollama
```
Type d'exécution: Docker
General: qwen3.5:9b-16k (custom/Ollama)
Coder:   qwen3.5:9b-16k (custom/Ollama, 16K tokens)
Vision:  llava (custom/Ollama)
```

### Scénario 2: Production avec OpenAI
```
Type d'exécution: Docker
General: gpt-4-turbo (openai)
Coder:   gpt-4-turbo (openai, 32K tokens)
Vision:  gpt-4-vision (openai, 16K tokens)
```

### Scénario 3: Hybride (Local + Cloud)
```
Type d'exécution: Host (SSH)
General: qwen3.5 (custom/Ollama)
Coder:   gpt-4-turbo (openai, 32K tokens)
Vision:  gpt-4-vision (openai, 16K tokens)
```

---

## 🔐 Sécurité

- ✅ Validation côté serveur de tous les champs
- ✅ Configuration isolée (`manager.json` vs `config.json`)
- ✅ Support Docker Socket Proxy
- ✅ Permissions via PUID/PGID
- ✅ Aucune clé API stockée dans le code
- ✅ Validation des entrées (provider, modèle, tokens > 0)

---

## 🐛 Dépannage

### Configuration ne s'applique pas
1. Sauvegarder la configuration
2. Cliquer sur "🔄 Redémarrer Nanobot"
3. Vérifier les logs: `docker logs nanobot-gateway`

### Les modèles Ollama n'apparaissent pas
- Vérifier que Ollama est en cours d'exécution
- Vérifier l'URL dans "⚙️ Paramètres" → "📡 Statut Ollama"
- Télécharger les modèles: `ollama pull <model>`

### Erreur SSH "No user exists for uid"
- Configurer PUID/PGID dans `.env`
- Redémarrer le container

### Mode Host ne fonctionne pas
- Vérifier la clé SSH dans "⚙️ Paramètres" → "🔑 Clé SSH"
- Vérifier HOST_SSH_USER, HOST_SSH_HOST dans `.env`

---

## 📚 Références

- [Documentation Nanobot](https://github.com/HKUDS/nanobot)
- [Configuration Nanobot](https://github.com/HKUDS/nanobot#configuration)
- [Providers Nanobot](https://github.com/HKUDS/nanobot#providers)

---

**Version**: 0.9  
**Dernière mise à jour**: 2026-03-19
