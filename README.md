# OC-Projet11-Gudlft

Application web Flask de réservation de places pour compétitions sportives.

## Description du projet

GUDLFT est une plateforme de réservation permettant aux secrétaires de clubs sportifs de réserver des places pour des compétitions à venir. Ce projet fait partie de la formation Développeur d'application Python d'OpenClassrooms.

**Objectifs du projet :**

- Corriger 5 bugs critiques identifiés dans le code original
- Implémenter une fonctionnalité de leaderboard public
- Écrire une suite de tests complète (unitaires, intégration, Selenium, performance)
- Atteindre une couverture de code minimum de 60%

## Fonctionnalités

### Phase 1 - Corrections de bugs

1. Gestion des erreurs pour emails invalides
2. Déduction automatique des points lors des réservations (1 place = 3 points)
3. Limitation à 12 places maximum par réservation
4. Validation du solde de points disponibles
5. Impossibilité de réserver pour des compétitions passées

### Phase 2 - Leaderboard public

- Affichage des clubs classés par nombre de points
- Accessible sans authentification
- Mise à jour en temps réel après chaque réservation

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git
- Un navigateur web moderne
- Chrome/Chromium (pour les tests Selenium)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/steveraffner/OC-Projet11-Gudlft.git
cd OC-Projet11-Gudlft
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv .venv
```

### 3. Activer l'environnement virtuel




**Sur macOS/Linux :**
```bash
source .venv/bin/activate
```

**Sur Windows :**
```bash
.venv\Scripts\activate
```

### 4. Installer les dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Lancement de l'application

```bash
python server.py
```

L'application sera accessible à l'adresse : http://127.0.0.1:5000

### Connexion
Utilisez l'un des emails suivants pour vous connecter :
- john@simplylift.co (Simply Lift - 13 points)
- admin@irontemple.com (Iron Temple - 4 points)
- kate@shelifts.co.uk (She Lifts - 12 points)

## Exécution des tests

### Tests unitaires et d'intégration
```bash
pytest tests/ -v
```

### Tests avec rapport de couverture
```bash
pytest --cov=server --cov-report=html --cov-report=term tests/
```

Le rapport HTML sera généré dans le dossier `htmlcov/`. Ouvrez `htmlcov/index.html` dans un navigateur.

### Tests Selenium (nécessite que le serveur soit lancé)
**Terminal 1 :**
```bash
python server.py
```

**Terminal 2 :**
```bash
pytest tests/selenium/ -v
```

### Tests de performance avec Locust
**Terminal 1 :**
```bash
python server.py
```

**Terminal 2 - Mode interface web :**
```bash
locust -f locustfile.py --host=http://127.0.0.1:5000
```
Puis ouvrir http://localhost:8089

**Terminal 2 - Mode headless (génère un rapport HTML) :**
```bash
locust -f locustfile.py --host=http://127.0.0.1:5000 \
  --users 50 --spawn-rate 5 --run-time 2m \
  --html report_performance.html --headless
```

## Structure du projet

```
OC-Projet11-Gudlft/
├── server.py                   # Application Flask principale
├── clubs.json                  # Données des clubs
├── competitions.json           # Données des compétitions
├── requirements.txt            # Dépendances Python
├── .flake8                     # Configuration flake8
├── API_DOCUMENTATION.md        # Documentation complète de l'API
├── locustfile.py              # Tests de performance
├── templates/                  # Templates HTML
│   ├── index.html
│   ├── welcome.html
│   ├── booking.html
│   └── leaderboard.html
├── tests/                      # Suite de tests
│   ├── unit/                   # Tests unitaires
│   │   ├── test_show_summary.py
│   │   ├── test_purchase_places.py
│   │   └── test_leaderboard.py
│   ├── integration/            # Tests d'intégration
│   │   └── test_user_flow.py
│   └── selenium/               # Tests Selenium
│       └── test_browser_automation.py
├── htmlcov/                    # Rapport de couverture (généré)
├── GUIDE_SOUTENANCE.md        # Guide de présentation orale
└── README.md                   # Ce fichier
```

## Résultats des tests

- **Tests unitaires** : 10/10 PASS
- **Tests d'intégration** : 7/7 PASS
- **Tests Selenium** : 9 tests créés
- **Couverture de code** : 94% (objectif : 60%)

## Technologies utilisées

- **Backend** : Flask 3.1.2
- **Templates** : Jinja2 3.1.6
- **Tests** : pytest 8.4.2, pytest-cov 7.0.0
- **Automatisation browser** : Selenium 4.38.0
- **Tests de performance** : Locust 2.42.2
- **Couverture** : coverage 7.11.3

## Méthodologie

Le projet a été développé en suivant la méthodologie **TDD (Test-Driven Development)** :
1. Écriture d'un test qui échoue (RED)
2. Implémentation du code minimal pour faire passer le test (GREEN)
3. Refactorisation si nécessaire (REFACTOR)

Chaque bug a été corrigé sur une branche dédiée avec ses tests associés, puis intégré dans la branche `qa`.

## Branches Git

- `main` : Code initial avec corrections essentielles
- `qa` : Branche d'intégration avec toutes les corrections et fonctionnalités
- `bug/*` : Branches de correction de bugs individuels
- `feature/*` : Branches de développement de nouvelles fonctionnalités

## Qualité du code

### Linting avec Flake8

Le projet utilise Flake8 pour vérifier la qualité du code Python.

```bash
# Vérifier tout le projet
flake8

# Vérifier un fichier spécifique
flake8 server.py

# Générer un rapport HTML
flake8 --format=html --htmldir=flake8-report
```

Configuration dans `.flake8`:
- Longueur maximale de ligne: 100 caractères
- Complexité maximale: 10 (McCabe)

## Documentation

- **API Documentation**: Voir [API_DOCUMENTATION.md](API_DOCUMENTATION.md) pour la documentation complète des endpoints
- **Docstrings**: Toutes les fonctions sont documentées avec des docstrings au format Google

## Auteur

Projet réalisé dans le cadre de la formation Développeur d'application Python - OpenClassrooms

## Licence

Ce projet est à usage éducatif dans le cadre de la formation OpenClassrooms.
