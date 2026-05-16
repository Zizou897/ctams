# CTAMS — Architecture du projet

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.12 + Django 5.x |
| Base de données | SQLite (dev) / MySQL ou PostgreSQL (prod) |
| CSS | Tailwind CSS v4 standalone CLI (`src/tailwindcss.exe`) |
| JS | Vanilla JS |
| Tâches async | Celery + Redis |
| Serveur | Nginx + Gunicorn |
| Admin | django-jazzmin (thème cyborg) |

## Arborescence

```
ctams/
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── tailwind.config.js
└── src/
    ├── manage.py
    ├── config/                   ← Configuration Django (settings, urls, wsgi)
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   ├── asgi.py
    │   ├── constants.py          ← Constantes globales (chemins upload, SECTORS)
    │   └── utils.py              ← Utilitaires globaux (email async, IP)
    ├── apps/                     ← Apps métier
    │   ├── core/                 ← Pages publiques (accueil, à propos, contact, SEO)
    │   │   ├── functions.py
    │   │   └── templatetags/core_tags.py
    │   ├── fleet/                ← Gestion de flotte & véhicules
    │   │   ├── functions.py
    │   │   └── templatetags/fleet_tags.py
    │   ├── services/             ← Catalogue services & tarifs
    │   │   ├── functions.py
    │   │   └── templatetags/services_tags.py
    │   ├── quotes/               ← Demandes de devis
    │   │   ├── functions.py
    │   │   └── templatetags/quotes_tags.py
    │   └── accounts/             ← Authentification & profils clients
    │       ├── functions.py
    │       └── templatetags/accounts_tags.py
    ├── templates/
    │   ├── base.html             ← Layout principal (nav, footer, SEO)
    │   ├── includes/             ← Navbar, footer
    │   ├── core/                 ← Accueil, à propos, contact
    │   ├── fleet/                ← Dashboard flotte, détail véhicule
    │   ├── services/             ← Liste & détail services
    │   ├── quotes/               ← Formulaire devis, confirmation
    │   ├── accounts/             ← Profil, connexion
    │   └── emails/               ← Templates emails transactionnels
    ├── static/
    │   └── css/
    │       ├── input.css         ← Source Tailwind v4
    │       └── main.css          ← Build Tailwind (commité)
    ├── static_cdn/               ← collectstatic (gitignored)
    ├── media_cdn/                ← Uploads utilisateurs (gitignored)
    └── data/                     ← Fixtures, exports, données de démo
```

## Convention de base des modèles

Tous les modèles publiables héritent de `Convention` (défini dans `apps.core.models`) :

```python
class Convention(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish = models.BooleanField(default=False)

    class Meta:
        abstract = True
```

## Apps métier

### `apps.core` — Pages publiques
- `HomeView` → `/`
- `AboutView` → `/a-propos/`
- `ContactView` → `/contact/`
- `RobotsView` → `/robots.txt`

### `apps.fleet` — Flotte & véhicules
- Modèle `Vehicle` (immatriculation, marque, modèle, type VL/PL, km)
- Modèle `MaintenanceRecord` (date, technicien, km, travaux, coût)
- Dashboard flotte client (protégé par login)

### `apps.services` — Catalogue
- Modèle `Service` (nom, slug, catégorie, prix VL/PL, sur devis)
- Vue liste & détail

### `apps.quotes` — Devis
- Modèle `QuoteRequest` (entreprise, contact, email, téléphone, nb véhicules, service, message)
- Formulaire → email → confirmation

### `apps.accounts` — Authentification
- Modèle `ClientProfile` lié à `auth.User`
- Vue profil client

## URLs namespaces

```python
app_name = 'core'      # {% url 'core:home' %}
app_name = 'fleet'     # {% url 'fleet:dashboard' %}
app_name = 'services'  # {% url 'services:list' %}
app_name = 'quotes'    # {% url 'quotes:request' %}
app_name = 'accounts'  # {% url 'accounts:profile' %}
```

## Règles de code

- PEP 8 + `ruff check .` + `ruff format`
- Type hints sur les services et utils
- Logique métier dans `functions.py`, jamais dans les vues
- CBV en priorité, FBV si logique simple
- Pas de `print()` → `logging`
- `select_related` / `prefetch_related` systématique

## Build CSS (Tailwind v4)

```bash
# Build unique
src\tailwindcss.exe -i src\static\css\input.css -o src\static\css\main.css --minify

# Watch (rebuild automatique)
src\tailwindcss.exe -i src\static\css\input.css -o src\static\css\main.css --watch
```

## Déploiement VPS

```bash
# Service Gunicorn (systemd)
WorkingDirectory=/var/www/project/ctams/src
ExecStart=/var/www/project/ctams/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    config.wsgi:application

EnvironmentFile=/var/www/project/ctams/.env.prod
```

## Commandes essentielles

```bash
python manage.py runserver
python manage.py makemigrations <app>
python manage.py migrate
python manage.py test apps/
python manage.py collectstatic --noinput
src\tailwindcss.exe -i src\static\css\input.css -o src\static\css\main.css --minify
```
