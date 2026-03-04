# Guide de Test - Configuration Coder et Vision

## 🧪 Tests Manuels

### 1. Démarrage du serveur

```bash
# Installer les dépendances
pip install -r nanobot-manager/requirements.txt

# Lancer l'application
cd nanobot-manager
python3 app.py
```

Le serveur sera accessible à `http://localhost:8899`

### 2. Tests de l'interface

#### Tab Default (Existant)
- [x] Sélectionner un provider dans la liste
- [x] Choisir un modèle Ollama ou saisir manuellement
- [x] Cliquer "Sauvegarder"
- [x] Vérifier le message de succès
- [x] Vérifier le badge "Config actuelle" mis à jour

#### Tab Coder (Nouveau)
- [x] Cliquer sur l'onglet "🔧 Coder"
- [x] Saisir un provider (ex: `custom`)
- [x] Saisir un modèle (ex: `qwen3.5:9b-16k`)
- [x] Sélectionner un contexte prédéfini (ex: `16384`)
- [x] Cliquer "Sauvegarder Coder"
- [x] Vérifier le message de succès
- [x] Vérifier le badge mis à jour

#### Tab Coder - Contexte personnalisé
- [x] Sélectionner "✏️ Personnalisé..." dans la liste
- [x] Saisir une valeur personnalisée (ex: `24000`)
- [x] Cliquer "Sauvegarder Coder"
- [x] Vérifier que la valeur est acceptée

#### Tab Vision (Nouveau)
- [x] Cliquer sur l'onglet "👁️ Vision"
- [x] Saisir un provider (ex: `custom`)
- [x] Saisir un modèle (ex: `llava`)
- [x] Sélectionner "Aucun" ou un contexte (optionnel)
- [x] Cliquer "Sauvegarder Vision"
- [x] Vérifier le message de succès

### 3. Tests des validations

#### Erreurs attendues:
```javascript
// Provider vide
// Error: "Modèle et provider requis"

// Modèle vide
// Error: "Modèle et provider requis"

// maxTokens invalide
// Error: "maxTokens invalide"

// maxTokens <= 0
// Error: "maxTokens doit être > 0"
```

### 4. Tests de configuration (config.json)

```bash
# Après avoir sauvegardé les configurations,
# vérifier le fichier config.json
cat /opt/stacks/nanobot/config/config.json

# Vérifier la structure:
{
  "agents": {
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

## 🔌 Tests d'API

### Récupérer la config Coder
```bash
curl http://localhost:8899/api/coder
# Response: {"model": "...", "provider": "...", "maxTokens": ...}
```

### Mettre à jour la config Coder
```bash
curl -X POST http://localhost:8899/api/coder/update \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4-turbo", "provider": "openai", "maxTokens": 32768}'
# Response: {"success": true, "message": "✅ Coder configuré: ..."}
```

### Récupérer la config Vision
```bash
curl http://localhost:8899/api/vision
# Response: {"model": "...", "provider": "...", "maxTokens": null}
```

### Mettre à jour la config Vision
```bash
curl -X POST http://localhost:8899/api/vision/update \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4-vision", "provider": "openai", "maxTokens": 16384}'
# Response: {"success": true, "message": "✅ Vision configurée: ..."}
```

## 📋 Checklist de Vérification

### Backend (app.py)
- [x] Toutes les routes API retournent du JSON valide
- [x] Les validations rejettent les données invalides
- [x] Les messages d'erreur sont informatifs
- [x] Les configurations sont sauvegardées dans config.json
- [x] maxTokens est validation (nombre, > 0)

### Frontend (index.html)
- [x] Les 3 onglets sont visibles
- [x] L'onglet "Par Défaut" fonctionne comme avant
- [x] L'onglet "Coder" charge/sauve la config
- [x] L'onglet "Vision" charge/sauve la config
- [x] Les dropdowns token fonctionnent
- [x] L'option "Personnalisé" permet une saisie manuelle
- [x] Les badges affichent la config actuelle
- [x] Le bouton "Restart" fonctionne

### UX/Design
- [x] L'interface est responsive
- [x] Les messages toast s'affichent correctement
- [x] Les spinners s'affichent pendant le chargement
- [x] Le thème sombre est cohérent

## 🐛 Débogage

### Pour voir les logs du serveur Flask:
```bash
cd nanobot-manager
python3 app.py  # Les logs s'affichent dans la console
```

### Pour vérifier les appels API:
1. Ouvrir DevTools (F12 ou Cmd+Shift+I)
2. Aller à l'onglet "Network"
3. Effectuer une action (sauvegarder config)
4. Vérifier les requêtes POST/GET
5. Vérifier les réponses JSON

### Pour tester localement sans Docker:
```bash
# Créer un fichier config.json de test
mkdir -p /opt/stacks/nanobot/config/

# Ou modifier CONFIG_PATH dans app.py pour un test local
export CONFIG_PATH="./config-test.json"
python3 app.py
```

## 📈 Tests de Performance

Les tests suivants ne sont pas critiques mais utiles:
- [x] Interface responsive sur mobile
- [x] Chargement < 2s pour chaque onglet
- [x] Pas de fuite mémoire lors de multiples sauvegardes

## ✅ Critères d'Acceptation

- [x] Toutes les routes API fonctionnent
- [x] Configuration Coder peut être définie/mise à jour
- [x] Configuration Vision peut être définie/mise à jour
- [x] Vision.maxTokens est optionnel
- [x] Les dropdowns token offrent 7+ options pour Coder
- [x] Les dropdowns token offrent 6+ options pour Vision
- [x] Validation côté serveur robuste
- [x] Messages d'erreur clairs
- [x] Config.json est mise à jour correctement
- [x] Aucun erreur JavaScript en console

## 🚀 Prêt pour Production?

Répondez à ces questions:
1. ✅ Toutes les fonctionnalités testées manuellement?
2. ✅ Aucune erreur en console (F12)?
3. ✅ Config.json correctement mise à jour?
4. ✅ Messages d'erreur affichés clairement?
5. ✅ Interface responsive testé?

Si tout est ✅, l'implémentation est prête pour:
```bash
docker compose -f compose.yaml build
docker compose -f compose.yaml up -d
```

---

**Dernière mise à jour**: 2026-03-04
