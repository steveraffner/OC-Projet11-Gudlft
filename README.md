# OC-Projet11-Güdlft# gudlift-registration



Application web Flask de réservation de places pour compétitions sportives.1. Why



## Description du projet

    This is a proof of concept (POC) project to show a light-weight version of our competition booking platform. The aim is the keep things as light as possible, and use feedback from the users to iterate.

GÜDLFT est une plateforme de réservation permettant aux secrétaires de clubs sportifs de réserver des places pour des compétitions à venir. Ce projet fait partie de la formation Développeur d'application Python d'OpenClassrooms.

2. Getting Started

**Objectifs du projet :**

- Corriger 5 bugs critiques identifiés dans le code original    This project uses the following technologies:

- Implémenter une fonctionnalité de leaderboard public

- Écrire une suite de tests complète (unitaires, intégration, Selenium, performance)    * Python v3.x+

- Atteindre une couverture de code minimum de 60%

    * [Flask](https://flask.palletsprojects.com/en/1.1.x/)

## Fonctionnalités

        Whereas Django does a lot of things for us out of the box, Flask allows us to add only what we need. 

### Phase 1 - Corrections de bugs     

1. Gestion des erreurs pour emails invalides

2. Déduction automatique des points lors des réservations (1 place = 3 points)    * [Virtual environment](https://virtualenv.pypa.io/en/stable/installation.html)

3. Limitation à 12 places maximum par réservation

4. Validation du solde de points disponibles        This ensures you'll be able to install the correct packages without interfering with Python on your machine.

5. Impossibilité de réserver pour des compétitions passées

        Before you begin, please ensure you have this installed globally. 

### Phase 2 - Leaderboard public

- Affichage des clubs classés par nombre de points

- Accessible sans authentification3. Installation

- Mise à jour en temps réel après chaque réservation

    - After cloning, change into the directory and type <code>virtualenv .</code>. This will then set up a a virtual python environment within that directory.

## Prérequis

    - Next, type <code>source bin/activate</code>. You should see that your command prompt has changed to the name of the folder. This means that you can install packages in here without affecting affecting files outside. To deactivate, type <code>deactivate</code>

- Python 3.8 ou supérieur

- pip (gestionnaire de paquets Python)    - Rather than hunting around for the packages you need, you can install in one step. Type <code>pip install -r requirements.txt</code>. This will install all the packages listed in the respective file. If you install a package, make sure others know by updating the requirements.txt file. An easy way to do this is <code>pip freeze > requirements.txt</code>

- Git

- Un navigateur web moderne    - Flask requires that you set an environmental variable to the python file. However you do that, you'll want to set the file to be <code>server.py</code>. Check [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application) for more details

- Chrome/Chromium (pour les tests Selenium)

    - You should now be ready to test the application. In the directory, type either <code>flask run</code> or <code>python -m flask run</code>. The app should respond with an address you should be able to go to using your browser.

## Installation

4. Current Setup

### 1. Cloner le repository

```bash    The app is powered by [JSON files](https://www.tutorialspoint.com/json/json_quick_guide.htm). This is to get around having a DB until we actually need one. The main ones are:

git clone https://github.com/[votre-username]/OC-Projet11-Güdlft.git     

cd OC-Projet11-Güdlft    * competitions.json - list of competitions

```    * clubs.json - list of clubs with relevant information. You can look here to see what email addresses the app will accept for login.



### 2. Créer un environnement virtuel5. Testing

```bash

python3 -m venv .venv    You are free to use whatever testing framework you like-the main thing is that you can show what tests you are using.

```

    We also like to show how well we're testing, so there's a module called 

### 3. Activer l'environnement virtuel    [coverage](https://coverage.readthedocs.io/en/coverage-5.1/) you should add to your project.



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
OC-Projet11-Güdlft/
├── server.py                   # Application Flask principale
├── clubs.json                  # Données des clubs
├── competitions.json           # Données des compétitions
├── requirements.txt            # Dépendances Python
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

## Auteur

Projet réalisé dans le cadre de la formation Développeur d'application Python - OpenClassrooms

## Licence

Ce projet est à usage éducatif dans le cadre de la formation OpenClassrooms.
