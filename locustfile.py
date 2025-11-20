"""
Tests de performance avec Locust
Simule des utilisateurs concurrents pour tester la charge du serveur

Usage:
    locust -f locustfile.py --host=http://127.0.0.1:5000

    Puis ouvrir http://localhost:8089 pour l'interface web Locust

    Ou en mode headless :
    locust -f locustfile.py --host=http://127.0.0.1:5000 --users 10 --spawn-rate 2 --run-time 60s --html report_performance.html
"""

from locust import HttpUser, task, between
import random


class GudlftUser(HttpUser):
    """
    Classe représentant un utilisateur du système GUDLFT
    Simule le comportement d'un secrétaire de club effectuant des réservations
    """

    # Temps d'attente entre chaque tâche (entre 1 et 5 secondes)
    wait_time = between(1, 5)

    # Emails des clubs disponibles
    club_emails = [
        "john@simplylift.co",
        "admin@irontemple.com",
        "kate@shelifts.co.uk"
    ]

    def on_start(self):
        """
        Méthode appelée au démarrage de chaque utilisateur simulé
        """
        # Choisir un email aléatoire pour cet utilisateur
        self.email = random.choice(self.club_emails)

    @task(5)
    def view_homepage(self):
        """
        Tâche : accéder à la page d'accueil
        Poids : 5 (exécutée 5 fois plus souvent que les autres tâches poids 1)
        """
        self.client.get("/")

    @task(10)
    def login(self):
        """
        Tâche : se connecter avec un email de club
        Poids : 10 (tâche la plus fréquente)
        """
        self.client.post("/showSummary", data={
            "email": self.email
        })

    @task(3)
    def view_leaderboard(self):
        """
        Tâche : consulter le leaderboard public
        Poids : 3
        """
        self.client.get("/leaderboard")

    @task(2)
    def book_places(self):
        """
        Tâche : réserver des places pour une compétition
        Poids : 2 (moins fréquent car nécessite d'être connecté)
        """
        # D'abord se connecter
        self.client.post("/showSummary", data={
            "email": self.email
        })

        # Ensuite réserver des places (entre 1 et 5 places)
        competitions = ["Spring Festival", "Fall Classic"]
        clubs = ["Simply Lift", "Iron Temple", "She Lifts"]

        places = random.randint(1, 5)
        competition = random.choice(competitions)
        club = random.choice(clubs)

        # Tenter la réservation
        with self.client.post(
            "/purchasePlaces",
            data={
                "club": club,
                "competition": competition,
                "places": str(places)
            },
            catch_response=True
        ) as response:
            # Vérifier si la réservation a réussi ou échoué proprement
            if response.status_code == 200:
                if b"Great-booking complete" in response.content:
                    response.success()
                elif b"Not enough points" in response.content or b"cannot book" in response.content:
                    # Échec attendu (validation métier), pas une erreur serveur
                    response.success()
                else:
                    response.failure("Unexpected response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def access_booking_page(self):
        """
        Tâche : accéder à la page de réservation directement
        Poids : 1 (moins fréquent)
        """
        clubs = ["Simply%20Lift", "Iron%20Temple", "She%20Lifts"]
        competitions = ["Spring%20Festival", "Fall%20Classic"]

        club = random.choice(clubs)
        competition = random.choice(competitions)

        self.client.get(f"/book/{competition}/{club}")

    @task(1)
    def logout(self):
        """
        Tâche : se déconnecter
        Poids : 1
        """
        self.client.get("/logout")


class InvalidEmailUser(HttpUser):
    """
    Classe représentant un utilisateur avec email invalide
    Teste la robustesse du système face aux erreurs
    """

    wait_time = between(2, 6)

    @task
    def login_with_invalid_email(self):
        """
        Tente de se connecter avec un email invalide
        """
        invalid_emails = [
            "invalid@email.com",
            "test@test.com",
            "notfound@example.org"
        ]

        email = random.choice(invalid_emails)

        with self.client.post(
            "/showSummary",
            data={"email": email},
            catch_response=True
        ) as response:
            # L'email invalide devrait rediriger (302) ou retourner 200 avec message
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Expected 200 or 302, got {response.status_code}")


class LeaderboardOnlyUser(HttpUser):
    """
    Classe représentant un visiteur consultant uniquement le leaderboard
    Simule l'accès public sans authentification
    """

    wait_time = between(3, 8)

    @task
    def view_leaderboard_repeatedly(self):
        """
        Consulte le leaderboard de manière répétée
        """
        self.client.get("/leaderboard")


# Configuration pour les tests de charge
# Pour lancer un test complet en ligne de commande :
# locust -f locustfile.py --host=http://127.0.0.1:5000 \
#        --users 50 --spawn-rate 5 --run-time 2m \
#        --html report_performance.html --headless
