# Nanobot Manager - Fonctionnalités

## 📋 Vue d'ensemble

Nanobot Manager est une interface web pour configurer les paramètres des agents IA de Nanobot. Il permet de configurer les modèles, providers et contextes pour différents cas d'usage.

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

## 🎨 Interface utilisateur

### Navigation par onglets
L'interface est organisée en 3 onglets pour faciliter la navigation:
- **Par Défaut** - Configuration globale
- **🔧 Coder** - Configuration pour la génération de code
- **👁️ Vision** - Configuration pour l'analyse d'images

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

### Redémarrer le container
- Bouton "🔄 Restart nanobot-gateway"
- Redémarre le container Docker `nanobot-gateway`
- Nécessaire après une modification de configuration
- Affiche l'état du redémarrage

---

## 📡 API Endpoints

### Configuration par Défaut
- `POST /api/update` - Mettre à jour le modèle/provider par défaut
- `GET /api/config` - Récupérer la configuration actuelle
- `GET /api/models` - Récupérer la liste des modèles Ollama

### Configuration Coder
- `GET /api/coder` - Récupérer la configuration Coder
- `POST /api/coder/update` - Mettre à jour la configuration Coder

### Configuration Vision
- `GET /api/vision` - Récupérer la configuration Vision
- `POST /api/vision/update` - Mettre à jour la configuration Vision

### Container
- `POST /api/restart` - Redémarrer nanobot-gateway

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

## 🐛 Dépannage

### Configuration ne s'applique pas
1. Sauvegarder la configuration dans l'onglet approprié
2. Cliquer sur "🔄 Restart nanobot-gateway"
3. Attendre que le container soit redémarré
4. Vérifier les logs: `docker logs nanobot-gateway`

### Erreurs lors de la sauvegarde
- Vérifier que le provider et le modèle sont non vides
- S'assure que maxTokens est un nombre positif
- Vérifier que le fichier de configuration est accessible

### Les modèles Ollama n'apparaissent pas
- Vérifier que Ollama est en cours d'exécution
- Vérifier l'URL Ollama dans les variables d'environnement
- Les modèles doivent être préalablement téléchargés avec `ollama pull`

---

## 📚 Références

- [Documentation officielle Nanobot](https://github.com/HKUDS/nanobot)
- Configuration complète: https://github.com/HKUDS/nanobot#configuration
- Providers disponibles: https://github.com/HKUDS/nanobot#providers

---

**Dernière mise à jour**: 2026-03-04
