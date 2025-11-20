# Documentation API - GUDLFT

## Vue d'ensemble

API REST pour la gestion des réservations de places pour compétitions sportives.

**Base URL:** `http://127.0.0.1:5000`

---

## Endpoints

### 1. Page d'accueil

```
GET /
```

Affiche la page d'accueil avec le formulaire de connexion.

**Réponse:**
- Status: `200 OK`
- Content-Type: `text/html`
- Body: Page HTML avec formulaire de connexion par email

---

### 2. Authentification

```
POST /showSummary
```

Authentifie un secrétaire de club via son adresse email.

**Paramètres (Form Data):**
| Paramètre | Type   | Requis | Description                    |
|-----------|--------|--------|--------------------------------|
| email     | string | Oui    | Adresse email du secrétaire    |

**Exemples d'emails valides:**
- `john@simplylift.co`
- `admin@irontemple.com`
- `kate@shelifts.co.uk`

**Réponses:**

**Succès (200 OK):**
```html
Page de bienvenue avec:
- Informations du club (nom, points disponibles)
- Liste des compétitions disponibles
```

**Erreur (302 Redirect):**
```
Redirection vers / avec message flash:
"Sorry, that email was not found."
```

---

### 3. Page de réservation

```
GET /book/<competition>/<club>
```

Affiche le formulaire de réservation pour une compétition spécifique.

**Paramètres URL:**
| Paramètre   | Type   | Description                  |
|-------------|--------|------------------------------|
| competition | string | Nom de la compétition        |
| club        | string | Nom du club                  |

**Exemple:**
```
GET /book/Spring%20Festival/Simply%20Lift
```

**Réponse:**
- Status: `200 OK`
- Content-Type: `text/html`
- Body: Formulaire de réservation avec détails de la compétition

---

### 4. Réservation de places

```
POST /purchasePlaces
```

Traite une réservation de places pour une compétition.

**Paramètres (Form Data):**
| Paramètre   | Type    | Requis | Description                      |
|-------------|---------|--------|----------------------------------|
| competition | string  | Oui    | Nom de la compétition            |
| club        | string  | Oui    | Nom du club                      |
| places      | integer | Oui    | Nombre de places à réserver      |

**Règles de validation:**

1. **Compétition future uniquement**
   - La date de la compétition doit être postérieure à la date actuelle
   - Message d'erreur: `"Cannot book places for past competitions."`

2. **Maximum 12 places par réservation**
   - Une réservation ne peut pas excéder 12 places
   - Message d'erreur: `"You cannot book more than 12 places per competition."`

3. **Points suffisants**
   - Coût: 1 place = 3 points
   - Le club doit avoir assez de points disponibles
   - Message d'erreur: `"Not enough points. You need X points but only have Y."`

**Réponses:**

**Succès (200 OK):**
```html
Retour au dashboard avec message:
"Great-booking complete!"

Mises à jour effectuées:
- Points du club: déduction de (places × 3) points
- Places disponibles: réduction du nombre de places
```

**Erreur (200 OK avec flash message):**
```html
Retour au dashboard avec message d'erreur approprié
```

**Exemple de calcul:**
```
Réservation: 4 places
Coût: 4 × 3 = 12 points
Club avant: 13 points → Club après: 1 point
```

---

### 5. Classement des clubs

```
GET /leaderboard
```

Affiche le tableau des points de tous les clubs.

**Accès:** Public (pas d'authentification requise)

**Réponse:**
- Status: `200 OK`
- Content-Type: `text/html`
- Body: Tableau HTML avec liste des clubs triés par points (décroissant)

**Données affichées:**
- Nom du club
- Nombre de points
- Classement (position)

---

### 6. Déconnexion

```
GET /logout
```

Déconnecte l'utilisateur et retourne à la page d'accueil.

**Réponse:**
- Status: `302 Found`
- Location: `/`

---

## Codes de statut HTTP

| Code | Signification       | Utilisation                              |
|------|---------------------|------------------------------------------|
| 200  | OK                  | Requête réussie                          |
| 302  | Found (Redirect)    | Redirection après action ou erreur       |
| 404  | Not Found           | Ressource non trouvée                    |
| 500  | Internal Error      | Erreur serveur                           |

---

## Messages Flash

L'application utilise Flask's `flash()` pour les messages utilisateur:

**Types de messages:**
- ✅ **Succès:** `"Great-booking complete!"`
- ❌ **Erreurs:**
  - Email invalide
  - Compétition passée
  - Limite de places dépassée
  - Points insuffisants

---

## Modèles de données

### Club
```json
{
  "name": "Simply Lift",
  "email": "john@simplylift.co",
  "points": "13"
}
```

### Compétition
```json
{
  "name": "Spring Festival",
  "date": "2025-03-27 10:00:00",
  "numberOfPlaces": "25"
}
```

---

## Exemples d'utilisation

### Exemple 1: Connexion réussie

**Requête:**
```http
POST /showSummary HTTP/1.1
Content-Type: application/x-www-form-urlencoded

email=john@simplylift.co
```

**Réponse:**
```html
200 OK
Page de bienvenue avec liste des compétitions
```

### Exemple 2: Réservation valide

**Requête:**
```http
POST /purchasePlaces HTTP/1.1
Content-Type: application/x-www-form-urlencoded

competition=Spring+Festival&club=Simply+Lift&places=3
```

**Réponse:**
```html
200 OK
Message: "Great-booking complete!"
Points déduits: 9 (3 places × 3 points)
```

### Exemple 3: Réservation invalide (trop de places)

**Requête:**
```http
POST /purchasePlaces HTTP/1.1
Content-Type: application/x-www-form-urlencoded

competition=Spring+Festival&club=Simply+Lift&places=15
```

**Réponse:**
```html
200 OK
Message flash: "You cannot book more than 12 places per competition."
```

---

## Notes techniques

- **Format des dates:** `YYYY-MM-DD HH:MM:SS`
- **Persistence:** Les données sont stockées en mémoire pendant l'exécution
- **Session:** Pas de gestion de session (état maintenu via les paramètres de route)
- **CORS:** Non configuré par défaut
