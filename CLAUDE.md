# CTAMS — Centre Technique Auto & Multi-Services

Plateforme web Django pour la gestion de flotte et la proposition commerciale B2B d'un garage automobile professionnel basé à Abidjan (Angré nouveau CHU, non loin de Val d'Oise).

## Contexte métier
- Client : M. Savadogo Salif, Gérant CTAMS
- Services : entretien de flottes, réparation toutes natures, lavage, vente de pièces
- Cible : entreprises (mines, BTP, transport, ambassades, ONG) disposant de flottes
- Zone : Abidjan & Côte d'Ivoire
- Contact : 07 77 90 68 45 | Sasava221@gmail.com

## Règles du projet
Chaque fichier spécialisé ci-dessous remplace tout prompt générique sur le sujet :

- [Sécurité](.claude/rules/security.md) — règles Django/Python de sécurité, secrets, permissions
- [Stack & UI/UX](.claude/rules/stack.md) — conventions Django, design system, SEO, couleurs
- [Workflow](.claude/rules/workflow.md) — commandes de build/test, process de développement

## Commandes essentielles
```bash
python manage.py runserver          # Serveur de développement
python manage.py migrate            # Appliquer les migrations
python manage.py test               # Lancer les tests
python manage.py collectstatic      # Collecter les fichiers statiques
```

## Structure cible
```
ctams/
├── manage.py
├── config/             # settings/, urls.py, wsgi.py, asgi.py
├── apps/
│   ├── core/           # Pages publiques, accueil, SEO
│   ├── fleet/          # Gestion de flotte, véhicules
│   ├── services/       # Catalogue de services & tarifs
│   ├── quotes/         # Demandes de devis
│   └── accounts/       # Authentification clients
├── templates/          # Templates Django globaux
├── static/             # CSS, JS, images
└── requirements/       # base.txt, dev.txt, prod.txt
```
