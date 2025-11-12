# Guide de Présentation Orale - Projet 11 GÜDLFT

## Vue d'ensemble du projet

**Projet** : Amélioration et tests d'une application Flask de réservation pour compétitions sportives  
**Nom** : GÜDLFT Registration System  
**Objectif** : Corriger 5 bugs critiques + ajouter une fonctionnalité + tests complets  

---

## Structure de la présentation (suggestions)

### 1. Introduction (2 minutes)
- Présenter le contexte : plateforme de réservation pour clubs sportifs
- Expliquer les 2 phases : **Phase 1** (bugs) + **Phase 2** (nouvelle fonctionnalité)

### 2. Démo de l'application (3 minutes)
- Montrer l'application en fonctionnement
- Parcours utilisateur : login → réservation → leaderboard

### 3. Présentation des corrections (10 minutes)
- Expliquer chaque bug et sa correction (détails ci-dessous)

### 4. Méthodologie TDD (3 minutes)
- Expliquer l'approche Test-Driven Development utilisée

### 5. Tests et couverture (5 minutes)
- Montrer les résultats des tests
- Présenter le rapport de couverture

### 6. Conclusion et questions (2 minutes)

---

## Les 5 Bugs Corrigés - Explications Détaillées

### Bug #1 : Crash avec email invalide

#### Problème technique
```python
# Code original (LIGNE 29)
club = [club for club in clubs if club['email'] == request.form['email']][0]
```
- **Que fait ce code ?** : Cherche dans la liste `clubs` le club dont l'email correspond
- **Le problème** : Si l'email n'existe pas, la liste est vide `[]`, et `[0]` provoque `IndexError`

#### Explication newbie
Imagine une bibliothèque : tu cherches un livre par son ISBN. Si le livre n'existe pas, la bibliothécaire te dit "désolé, introuvable". Le code original faisait comme si le livre existait TOUJOURS, ce qui plantait le système quand ce n'était pas le cas.

#### Solution implémentée
```python
try:
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html', club=club, competitions=competitions)
except IndexError:
    flash("Sorry, that email was not found.")
    return redirect(url_for('index'))
```

**Explication** : On "enveloppe" le code dans un `try/except` :
- **try** : "Essaie de trouver le club"
- **except IndexError** : "Si tu ne trouves rien, affiche un message et reviens à l'accueil"

#### Test associé : `test_show_summary_with_invalid_email_should_not_crash`
```python
def test_show_summary_with_invalid_email_should_not_crash(self):
    response = self.client.post('/showSummary', data={
        'email': 'invalid@email.com'
    })
    # Ne doit PAS retourner 500 (erreur serveur)
    assert response.status_code != 500
```

---

### Bug #2 : Points non déduits lors d'une réservation

#### Problème technique
Le code original ne contenait AUCUNE ligne déduisant les points du club.
```python
# Ligne 48 originale - manquait complètement
# Aucune déduction de points !
```

#### Explication newbie
Tu vas à la boulangerie, tu prends un pain (2€), mais la boulangère ne te fait pas payer. Tu pars avec ton pain gratuit ! C'est génial pour toi, mais pas pour la boulangerie...

#### Solution implémentée
```python
# Calculer le coût (1 place = 3 points selon spécifications)
points_cost = placesRequired * 3
club_points = int(club['points'])

# ... validations ...

# DÉDUCTION DES POINTS
club['points'] = str(club_points - points_cost)
```

**Explication** :
1. On calcule combien ça coûte : `2 places × 3 points = 6 points`
2. On récupère les points actuels du club : `13 points`
3. On soustrait : `13 - 6 = 7 points restants`
4. On met à jour : `club['points'] = '7'`

#### Test associé : `test_purchase_places_deducts_points_from_club`
```python
initial_points = int(club['points'])  # Ex: 13
# ... réservation de 2 places ...
expected_points = initial_points - (2 * 3)  # 13 - 6 = 7
assert int(club['points']) == expected_points
```

---

### Bug #3 : Pas de limite sur le nombre de places

#### Problème technique
Aucune validation n'empêchait un club de réserver 100, 1000, ou même 1 million de places d'un coup.

#### Explication newbie
Imagine un concert avec 500 places. Sans limite, une personne pourrait réserver les 500 places pour elle seule, et personne d'autre ne pourrait aller au concert. Pas cool !

#### Solution implémentée
```python
# VALIDATION : maximum 12 places par réservation
if placesRequired > 12:
    flash('You cannot book more than 12 places per competition.')
    return render_template('welcome.html', club=club, competitions=competitions)
```

**Explication** :
- Avant de traiter la réservation, on vérifie : "Est-ce que le nombre demandé dépasse 12 ?"
- Si OUI → message d'erreur et on arrête
- Si NON → on continue le processus

#### Test associé : `test_purchase_more_than_12_places_should_be_rejected`
```python
response = self.client.post('/purchasePlaces', data={
    'places': '13'  # TROP !
})
assert b'cannot book more than 12 places' in response.data.lower()
```

---

### Bug #4 : Possibilité de dépenser plus de points que disponible

#### Problème technique
Un club avec 4 points pouvait réserver 2 places (coût : 6 points), résultant en **-2 points** (dette impossible).

#### Explication newbie
Tu as 4€ dans ton porte-monnaie. Tu veux acheter quelque chose à 6€. Le système devrait te dire "Désolé, pas assez d'argent", mais au lieu de ça, il te laisse acheter et tu te retrouves avec -2€ de dette !

#### Solution implémentée
```python
# VALIDATION : vérifier solde suffisant
if points_cost > club_points:
    flash(f'Not enough points. You need {points_cost} points but only have {club_points}.')
    return render_template('welcome.html', club=club, competitions=competitions)
```

**Explication** :
1. On calcule le coût : `2 places = 6 points`
2. On vérifie : "Est-ce que 6 > 4 ?" → OUI
3. Message : "Désolé, tu as besoin de 6 points mais tu n'en as que 4"

#### Test associé : `test_purchase_with_insufficient_points_should_be_rejected`
```python
response = self.client.post('/purchasePlaces', data={
    'club': 'Iron Temple',  # 4 points
    'places': '2'  # Coûte 6 points
})
assert b'not enough points' in response.data.lower()
```

---

### Bug #5 : Réservation possible pour compétitions passées

#### Problème technique
Les compétitions dans `competitions.json` ont des dates (exemple : `2020-03-27`), mais aucune vérification n'empêchait de réserver pour une compétition en 2020 alors qu'on est en 2025.

#### Explication newbie
Tu essaies d'acheter un billet pour un concert qui a eu lieu il y a 5 ans. C'est impossible ! Le code original te laissait faire, comme si on pouvait remonter le temps.

#### Solution implémentée
```python
from datetime import datetime  # Import en haut du fichier

# VALIDATION : compétition dans le futur uniquement
competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
if competition_date < datetime.now():
    flash('Cannot book places for past competitions.')
    return render_template('welcome.html', club=club, competitions=competitions)
```

**Explication** :
1. `datetime.strptime()` : Convertit le texte "2020-03-27 10:00:00" en objet date
2. `datetime.now()` : Donne la date/heure actuelle
3. Comparaison : "Est-ce que 2020 < 2025 ?" → OUI → REJET

#### Test associé : `test_purchase_for_past_competition_should_be_rejected`
```python
response = self.client.post('/purchasePlaces', data={
    'competition': 'Winter Marathon'  # Date : 2020 (passée)
})
assert b'past' in response.data.lower()
```

---

## Phase 2 : Leaderboard Public

### Objectif
Afficher un tableau de classement montrant tous les clubs avec leurs points, accessible sans authentification.

### Implémentation

#### 1. Route Flask
```python
@app.route('/leaderboard')
def leaderboard():
    # Trier les clubs par points (du plus grand au plus petit)
    sorted_clubs = sorted(clubs, key=lambda x: int(x['points']), reverse=True)
    return render_template('leaderboard.html', clubs=sorted_clubs)
```

**Explication** :
- `sorted(clubs, ...)` : Trie la liste des clubs
- `key=lambda x: int(x['points'])` : Critère de tri = les points
- `reverse=True` : Du plus grand au plus petit (ordre décroissant)

#### 2. Template HTML (`leaderboard.html`)
```html
<table>
    <thead>
        <tr>
            <th>Rank</th>
            <th>Club Name</th>
            <th>Points</th>
        </tr>
    </thead>
    <tbody>
        {% for club in clubs %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ club.name }}</td>
            <td>{{ club.points }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Explication** :
- `{% for club in clubs %}` : Boucle sur chaque club
- `{{ loop.index }}` : Numéro d'itération (1, 2, 3...)
- `{{ club.name }}` : Affiche le nom du club

### Explication newbie
Imagine un tableau des scores dans un jeu vidéo : tous les joueurs sont listés avec leur score, du meilleur au moins bon. C'est exactement pareil ici, mais avec des clubs sportifs et leurs points.

---

## Méthodologie TDD (Test-Driven Development)

### Principe
1. **RED** : Écrire un test qui ÉCHOUE
2. **GREEN** : Écrire le code minimal pour faire PASSER le test
3. **REFACTOR** : Améliorer le code (si besoin)

### Application concrète

#### Exemple : Bug #2 (points non déduits)

**Étape 1 - RED** : Écrire le test
```python
def test_purchase_places_deducts_points_from_club(self):
    initial_points = 13
    # Acheter 2 places
    self.client.post('/purchasePlaces', data={'places': '2'})
    # Vérifier déduction
    assert club['points'] == 7  # 13 - 6 = 7
```
→ Le test **ÉCHOUE** car aucun code ne déduit les points

**Étape 2 - GREEN** : Implémenter la correction
```python
points_cost = placesRequired * 3
club['points'] = str(int(club['points']) - points_cost)
```
→ Le test **PASSE** maintenant

**Étape 3 - REFACTOR** : Code déjà propre, rien à améliorer

### Avantages de TDD
- **Confiance** : Les tests prouvent que le code fonctionne
- **Documentation** : Les tests expliquent comment le code doit se comporter
- **Régression** : Si on casse quelque chose, un test échouera immédiatement

---

## Résultats des Tests

### Tests Unitaires : 10/10 PASS
- `test_show_summary.py` : 2 tests (email validation)
- `test_purchase_places.py` : 5 tests (toutes les validations)
- `test_leaderboard.py` : 3 tests (affichage public)

### Tests d'Intégration : 7/7 PASS
- Parcours utilisateur complets (login → booking → leaderboard)
- Gestion des erreurs et validations
- Réservations multiples

### Tests Selenium : 9 tests
- Automatisation browser (Chrome headless)
- Navigation complète
- Mode responsive

### Tests de Performance : Locust
- Simulation d'utilisateurs concurrents
- 3 types d'utilisateurs (normal, erreurs, public)
- Rapport HTML généré

### Couverture de Code : 94%
- **Requis** : 60%
- **Obtenu** : 94%
- **Détail** : 64 lignes, 4 non couvertes (edge cases + main)

---

## Démonstration Technique

### Lancer l'application
```bash
cd OC-Projet11-Güdlft
source .venv/bin/activate  # ou : .venv/bin/activate (Linux/Mac)
python server.py
```
→ Ouvre http://127.0.0.1:5000

### Lancer les tests
```bash
# Tests unitaires + intégration
pytest tests/ -v

# Avec couverture
pytest --cov=server --cov-report=html tests/

# Tests Selenium (serveur doit tourner)
pytest tests/selenium/ -v
```

### Lancer Locust
```bash
# Interface web
locust -f locustfile.py --host=http://127.0.0.1:5000

# Mode headless (rapport HTML)
locust -f locustfile.py --host=http://127.0.0.1:5000 \
  --users 50 --spawn-rate 5 --run-time 2m \
  --html report_performance.html --headless
```

---

## Phrases Clés pour la Soutenance

### Concernant les bugs
> "J'ai identifié 5 bugs critiques dans le code original. Pour chaque bug, j'ai d'abord écrit un test qui reproduisait le problème, puis j'ai implémenté la correction en suivant la méthodologie TDD."

### Concernant les tests
> "J'ai écrit 17 tests automatisés qui couvrent 94% du code. Ces tests garantissent que les bugs corrigés ne réapparaîtront pas et que les nouvelles fonctionnalités fonctionnent correctement."

### Concernant la Phase 2
> "J'ai ajouté un leaderboard public accessible sans authentification. Les clubs sont triés par points décroissants, permettant à n'importe qui de consulter le classement en temps réel."

### Concernant la qualité
> "J'ai adopté une approche TDD stricte : chaque correction a été validée par au moins un test. Le code est maintenable, documenté, et la couverture de 94% dépasse largement les 60% requis."

---

## Questions Probables et Réponses

### Q: Pourquoi TDD plutôt que coder puis tester ?
**R:** TDD force à réfléchir aux comportements attendus AVANT d'écrire le code. Cela évite le sur-engineering et garantit que chaque ligne de code a une raison d'être validée par un test.

### Q: Comment gérez-vous les données de test ?
**R:** J'utilise `setup_method()` et `teardown_method()` dans pytest pour sauvegarder et restaurer l'état initial des données entre chaque test. Cela garantit l'isolation des tests.

### Q: Pourquoi 1 place = 3 points ?
**R:** C'est une spécification métier du projet. J'ai implémenté cette règle telle qu'elle était définie dans les spécifications fonctionnelles.

### Q: Comment améliorer encore l'application ?
**R:** Plusieurs pistes :
- Persister les données dans une vraie base de données (SQLite, PostgreSQL)
- Ajouter une authentification sécurisée (sessions, tokens)
- Implémenter une limitation par compétition (pas plus de 12 places au TOTAL par club et par compétition)
- Ajouter des logs pour tracer les réservations

---

## Livrables du Projet

1. **Code source** sur GitHub : OC-Projet11-Güdlft
2. **Rapport de couverture** : PNG du tableau HTML
3. **Rapport de performance** : HTML généré par Locust
4. **Documentation** : Ce guide + README.md + Journal_de_travail.md

---

## Checklist Finale

- [x] Les 5 bugs sont corrigés
- [x] Phase 2 (leaderboard) implémentée
- [x] 17 tests automatisés (tous passent)
- [x] Couverture 94% (> 60% requis)
- [x] Tests Selenium créés
- [x] Tests Locust créés
- [x] Code versionné sur Git avec branches
- [x] Documentation complète

---

**Bonne chance pour votre soutenance !**
