
# Zetis — Backend

Backend de la plateforme de débat live contradictoire 1v1 structuré par IA.

---

## Stack Technique

| Composant              | Technologie                          | Version |
|------------------------|--------------------------------------|---------|
| Framework              | **FastAPI**                          | 0.115+  |
| Langage                | Python                               | 3.11+   |
| Base de données        | PostgreSQL                           | 16      |
| ORM                    | SQLAlchemy 2.0 + Alembic             | -       |
| Cache / Queue          | Redis                                | 7       |
| Authentification       | Supabase Auth (JWT + OAuth2)         | -       |
| Temps réel             | WebSocket + WebRTC Signaling         | -       |
| IA                     | Anthropic Claude Haiku 3.5 + Gemini 2.0 Flash | - |
| Validation             | Pydantic v2                          | -       |
| Linting / Format       | Ruff + Black                         | -       |
| Tests                  | Pytest + pytest-asyncio              | -       |
| Déploiement            | Railway                              | -       |

---

## Structure du Projet

```bash
backend/
├── app/
│   ├── api/                    # Routes FastAPI (endpoints)
│   ├── core/                   # Configuration, settings, security, dependencies
│   ├── db/                     # Base de données (session, engine, base model)
│   ├── models/                 # Modèles SQLAlchemy
│   ├── schemas/                # Schémas Pydantic (request/response)
│   ├── services/               # Logique métier (matching, IA, rating, etc.)
│   ├── repositories/           # Couche d'accès aux données (optionnel)
│   ├── websocket/              # Gestion WebSocket (queue + debate rooms)
│   ├── tasks/                  # Tâches asynchrones (Celery ou background tasks)
│   ├── utils/                  # Utilitaires généraux
│   ├── exceptions/             # Exceptions personnalisées
│   └── main.py
├── alembic/                    # Migrations de base de données
├── tests/                      # Tests unitaires et d'intégration
├── scripts/                    # Scripts utiles (seed, backup, etc.)
├── .env.example
├── .env                        # (non commité)
├── pyproject.toml              # Configuration Ruff, Pytest, etc.
├── requirements.txt
├── README.md
└── Dockerfile
```

---

## Installation Locale (Développement)

### 1. Cloner et accéder au dossier

```bash
git clone 
cd zetis/backend
```

### 2. Créer l’environnement virtuel

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
# ou avec pip-tools : pip-sync
```

### 4. Configuration

```bash
cp .env.example .env
```

Remplis le fichier `.env` avec les valeurs nécessaires (voir section ci-dessous).

### 5. Base de données

```bash
# Appliquer les migrations
alembic upgrade head

# (Optionnel) Charger des données de test
python scripts/seed_data.py
```

### 6. Lancement du serveur

```bash
uvicorn app.main:app --reload 
```

**URLs utiles :**
- API : http://localhost:8000
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

---

## Variables d’Environnement (.env)

Copie `.env.example` et configure :

```env
# Application
ENVIRONMENT=development
DEBUG=true
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Base de données
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/zetis

# Redis
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6380

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...

# Auth
JWT_SECRET=super-long-random-secret-key

# IA
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...

# WebRTC TURN
TURN_USERNAME=...
TURN_CREDENTIAL=...

# Monitoring / Logs
SENTRY_DSN=...
```

---

## Comment Développer sur le Backend

### 1. Ajouter une nouvelle fonctionnalité

**Étapes recommandées :**

1. **Définir les modèles** (`app/models/`)
2. **Créer les schémas** (`app/schemas/`)
3. **Ajouter la logique métier** dans `app/services/`
4. **Créer les endpoints** dans `app/api/routes/`
5. **Ajouter les WebSocket events** si nécessaire (`app/websocket/`)
6. **Écrire les tests** (`tests/`)
7. **Créer une migration** si modification de la BDD

Exemple :
```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "add new feature xyz"
```

### 2. Debugging

- Utilise le mode `--reload`
- Active `DEBUG=true` dans `.env`
- Utilise les logs structurés (loguru ou logging)
- Utilise le debugger de VS Code / PyCharm
- Accède à `/docs` pour tester les endpoints

**Point d’entrée principal :** `app/main.py`

### 3. Tests

```bash
# Tous les tests
pytest

# Tests avec coverage
pytest --cov=app --cov-report=html

# Un seul fichier
pytest tests/api/test_debates.py -v
```

---

## Conventions de Code

- **Linting & Format** : Ruff (configuré dans `pyproject.toml`)
- **Import sorting** : Ruff + isort
- **Type checking** : `pyright` ou `mypy`
- **Nommage** : snake_case pour Python, CamelCase pour Pydantic
- **Docstrings** : Google style

Commandes utiles :

```bash
ruff check . --fix
ruff format .
```

---

## Architecture & Bonnes Pratiques

- **FastAPI Best Practices** (Dependency Injection, APIRouter)
- Séparation claire : `schemas` → `services` → `repositories` → `models`
- Utilisation systématique des `Depends()` pour les dépendances
- Gestion des erreurs centralisée (`app/exceptions/`)
- Background tasks pour les opérations asynchrones lourdes (IA, résumés)
- Logging détaillé des appels IA (coût, tokens, latence)

---

## Scripts Utiles (`scripts/`)

- `seed_data.py` — Initialiser des données de test
- `check_health.py` — Vérifier la santé des services externes
- `cleanup_old_debates.py` — Nettoyage périodique

---

## Déploiement

Le backend est déployé sur **Railway**.

```bash
# Build local (optionnel)
docker build -t zetis-backend .

# Variables d'environnement à configurer sur Railway :
# DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY, etc.
```

---

## Support & Debugging Avancé

### Problèmes fréquents :

1. **Erreur de connexion Redis** → Vérifier `REDIS_URL` et le firewall
2. **JWT invalide** → Vérifier `JWT_SECRET` et les claims Supabase
3. **Modèle IA en erreur** → Consulter les logs dans `ai_logs` table
4. **Problème WebRTC** → Vérifier le signaling et les TURN credentials

### Outils recommandés :

- **Postman** / **Thunder Client** pour tester l’API
- **pgAdmin** ou **TablePlus** pour explorer la BDD
- **Redis Insight** pour inspecter Redis
- **Sentry** pour le monitoring en production

---

**Zetis** — *Opposez vos idées. Questionnez la vérité.*

© 2026 Zetis — Usage interne

