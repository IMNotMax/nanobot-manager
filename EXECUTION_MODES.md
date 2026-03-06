# 🔄 Modes d'Exécution de Nanobot Manager

Nanobot Manager supporte deux modes d'exécution pour redémarrer nanobot-gateway :

## 🐳 Mode Docker (Par défaut)

**Condition** : nanobot-gateway s'exécute dans un container Docker

**Fonctionnement** :
- Nanobot Manager communique avec le Docker Socket Proxy
- Trouve le container "nanobot-gateway"
- Envoie une requête HTTP POST au proxy pour redémarrer le container
- Redémarrage instantané du container

**Configuration** :
```yaml
environment:
  - DOCKER_PROXY_URL=http://socket-proxy-nbt-mngr:2375
```

**Avantages** :
- ✅ Simple et direct
- ✅ Pas de clés SSH à gérer
- ✅ Redémarrage rapide et fiable
- ✅ Sécurisé via socket-proxy

**Inconvénients** :
- ❌ Nécessite Docker Socket Proxy configuré
- ❌ Ne fonctionne que si nanobot-gateway est en container

---

## 🖥️ Mode Host (Machine hôte)

**Condition** : nanobot-gateway s'exécute comme un service `systemctl` sur la machine hôte

**Fonctionnement** :
- Nanobot Manager (dans un container) communique via SSH avec l'hôte
- Exécute `systemctl --user restart nanobot-gateway` sur l'hôte
- Le service systemctl redémarre normalement

**Configuration**:
```yaml
environment:
  - HOST_SSH_USER=your_username
  - HOST_SSH_HOST=localhost
  - HOST_SSH_PORT=22
volumes:
  - ~/.ssh/nanobot-manager:/root/.ssh:ro
```

**Avantages** :
- ✅ Flexible - fonctionne avec des services installés
- ✅ Moins d'overhead qu'un container
- ✅ Permet une gestion unitaire de nanobot-gateway

**Inconvénients** :
- ❌ Nécessite SSH configuré
- ❌ Nécessite des clés SSH
- ❌ Redémarrage légèrement plus lent que Docker

---

## 📋 Setup Détaillé : Mode Host

### Étape 1 : Installer openssh-client dans le container

Le Dockerfile inclut déjà `openssh-client` mais vous pouvez le vérifier :

```bash
docker exec nanobot-manager which ssh
```

### Étape 2 : Générer une clé SSH

**Option A : Dans le container existant**
```bash
docker exec nanobot-manager ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ""
```

**Option B : Avant de démarrer (créer le répertoire)**
```bash
mkdir -p ~/.ssh/nanobot-manager
ssh-keygen -t ed25519 -f ~/.ssh/nanobot-manager/id_ed25519 -N ""
```

### Étape 3 : Récupérer la clé publique

```bash
# Si généré dans le container
docker exec nanobot-manager cat /root/.ssh/id_ed25519.pub

# Si généré localement
cat ~/.ssh/nanobot-manager/id_ed25519.pub
```

Exemple de sortie :
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGj2... root@container
```

### Étape 4 : Ajouter la clé sur l'hôte

**Sur la machine hôte** (pas dans le container) :

```bash
# Créer le répertoire si nécessaire
mkdir -p ~/.ssh

# Ajouter la clé publique
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGj2..." >> ~/.ssh/authorized_keys

# Fixer les permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Étape 5 : Configurer docker-compose.yaml

Mettez à jour le service `nanobot-manager` :

```yaml
nanobot-manager:
  build: 
    context: .
    dockerfile: Dockerfile
  container_name: nanobot-manager
  ports:
    - "8899:8899"
  volumes:
    - ~/.nanobot:/root/.nanobot
    - ~/.ssh/nanobot-manager:/root/.ssh:ro  # ← Ajouter cette ligne
  environment:
    - CONFIG_PATH=/root/.nanobot/config.json
    - OLLAMA_URL=http://192.168.2.220:11434
    - DOCKER_PROXY_URL=http://socket-proxy-nbt-mngr:2375
    # ← Ajouter ces 3 variables pour le mode Host
    - HOST_SSH_USER=your_username
    - HOST_SSH_HOST=localhost
    - HOST_SSH_PORT=22
  restart: unless-stopped
```

**Remplacer les valeurs** :
- `your_username` : votre nom d'utilisateur sur l'hôte
- `localhost` : IP/hostname de l'hôte (127.0.0.1, 192.168.x.x, etc.)
- `22` : port SSH (généralement 22, mais peut être différent)

### Étape 6 : Reconstruire et redémarrer

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose logs -f nanobot-manager
```

### Étape 7 : Tester la connexion SSH

Vérifiez que la connexion SSH fonctionne :

```bash
# Test simple
docker exec nanobot-manager ssh -o StrictHostKeyChecking=no your_username@localhost "echo SSH OK"

# Test systemctl
docker exec nanobot-manager ssh -o StrictHostKeyChecking=no your_username@localhost "systemctl --user status nanobot-gateway"
```

Si vous voyez une erreur, consultez la section **Dépannage** ci-dessous.

### Étape 8 : Configurer dans Nanobot Manager

1. Ouvrir <http://localhost:8899>
2. Aller à l'onglet **⚙️ Paramètres**
3. Sélectionner **🖥️ Machine hôte (Systemctl)**
4. Cliquer **💾 Sauvegarder les paramètres**

Maintenant, le bouton **🔄 Redémarrer Nanobot** utilisera SSH + systemctl.

---

## 🔍 Dépannage : Mode Host

### Erreur : "SSH not found"

```bash
# L'image Docker doit avoir openssh-client
docker exec nanobot-manager which ssh

# Si manquant, reconstruire l'image
docker compose down
docker compose build --no-cache
```

### Erreur : "Host not reachable" ou "Connection refused"

1. **Vérifier que SSH est accessible depuis le container**
   ```bash
   docker exec nanobot-manager ssh -v your_username@localhost
   ```

2. **Vérifier l'adresse et le port**
   ```bash
   # Depuis l'hôte
   ip addr show
   
   # Mettre à jour compose.yaml avec la bonne adresse
   ```

3. **Vérifier le pare-feu**
   ```bash
   # Linux
   sudo ufw allow 22
   
   # macOS
   System Preferences > Security & Privacy > Firewall
   ```

### Erreur : "Permission denied (publickey)"

1. **Vérifier la clé SSH existe dans le container**
   ```bash
   docker exec nanobot-manager ls -la /root/.ssh/
   # Doit afficher: id_ed25519 et authorized_keys
   ```

2. **Vérifier les permissions sur l'hôte**
   ```bash
   ls -la ~/.ssh/
   # ~/.ssh doit avoir 700
   # authorized_keys doit avoir 600
   ```

3. **Vérifier que la clé publique est dans authorized_keys**
   ```bash
   cat ~/.ssh/authorized_keys
   # Doit contenir la clé ssh-ed25519...
   ```

4. **Si rien n'a changé, régénérer la clé**
   ```bash
   # Nettoyer
   rm -rf ~/.ssh/nanobot-manager
   
   # Régénérer
   mkdir -p ~/.ssh/nanobot-manager
   ssh-keygen -t ed25519 -f ~/.ssh/nanobot-manager/id_ed25519 -N ""
   
   # Reconfigurer tout
   ```

### Erreur : "systemctl command not found"

```bash
# La commande systemctl n'existe que sur Linux
# Vérifier l'OS de l'hôte
uname -a
```

### Erreur : "systemctl: unrecognized service"

```bash
# Vérifier que le service nanobot-gateway existe
systemctl --user status nanobot-gateway

# Si manquant, le créer ou installer le service
# Consulter la documentation Nanobot pour installer le service systemctl
```

### Erreur : "SSH timeout" ou "Operation timed out"

1. **Vérifier la latence réseau**
   ```bash
   docker exec nanobot-manager ping localhost
   ```

2. **Augmenter le timeout dans le code** (app/app.py ligne ~260)
   ```python
   timeout=60  # Par défaut 30, augmenter si nécessaire
   ```

### Logs détaillés

```bash
# Voir les logs du container
docker compose logs -f nanobot-manager

# Logs SSH avec verbose
docker exec nanobot-manager ssh -v -v user@host "echo test" 2>&1
```

---

## 🔄 Basculer entre les modes

Vous pouvez changer de mode à tout moment :

1. Ouvrir <http://localhost:8899>
2. Onglet **⚙️ Paramètres**
3. Sélectionner le mode souhaité
4. Cliquer **💾 Sauvegarder**
5. Utiliser le bouton **🔄 Redémarrer Nanobot** (s'adapte automatiquement)

---

## 📊 Comparaison des modes

| Aspect | Docker | Host |
|--------|--------|------|
| **Installation** | Socket proxy requis | SSH requis |
| **Complexité** | Basse | Moyenne |
| **Vitesse** | Très rapide | Rapide |
| **Sécurité** | Socket proxy | SSH avec clés |
| **Cas d'usage** | Conteneurs | Services système |
| **Dépendances** | Docker socket | SSH + systemctl |

---

## 💡 Recommandations

- **Utilisez Docker** si nanobot-gateway est en container
  - Plus simple à configurer
  - Pas de clés SSH à gérer
  
- **Utilisez Host** si nanobot-gateway est un service system
  - Meilleur contrôle du service
  - Économise les ressources conteneur
  - Idéal pour développement natif

- **Vous pouvez supporter les deux** grâce au sélecteur ⚙️
  - Basculer dynamiquement selon les besoins
  - Pas de reconfiguration majeure
