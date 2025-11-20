"""
Tests d'intégration pour les parcours utilisateur complets
Ces tests vérifient le fonctionnement de bout en bout de l'application
"""
from datetime import datetime, timedelta
from server import app, clubs, competitions


class TestUserFlow:
    """Tests d'intégration pour les parcours utilisateur"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Sauvegarder l'état initial
        self.initial_clubs = [club.copy() for club in clubs]
        self.initial_competitions = [comp.copy() for comp in competitions]

        # Configurer des dates futures pour les tests
        for comp in competitions:
            if comp['name'] == 'Spring Festival':
                future_date = datetime.now() + timedelta(days=30)
                comp['date'] = future_date.strftime('%Y-%m-%d %H:%M:%S')
            elif comp['name'] == 'Fall Classic':
                future_date = datetime.now() + timedelta(days=90)
                comp['date'] = future_date.strftime('%Y-%m-%d %H:%M:%S')

    def teardown_method(self):
        """Restaurer l'état initial après chaque test"""
        clubs.clear()
        clubs.extend(self.initial_clubs)
        competitions.clear()
        competitions.extend(self.initial_competitions)

    def test_complete_booking_flow_success(self):
        """
        Test d'intégration : parcours complet d'une réservation réussie
        1. Login avec email valide
        2. Affichage des compétitions
        3. Réservation de places
        4. Vérification des déductions (points + places)
        """
        # Étape 1 : Login
        response = self.client.post('/showSummary', data={
            'email': 'john@simplylift.co'
        })
        assert response.status_code == 200
        assert b'Welcome' in response.data

        # Vérifier les points initiaux
        club = [c for c in clubs if c['email'] == 'john@simplylift.co'][0]
        initial_points = int(club['points'])

        # Vérifier les places initiales
        competition = [c for c in competitions if c['name'] == 'Spring Festival'][0]
        initial_places = int(competition['numberOfPlaces'])

        # Étape 2 : Réservation de 3 places
        response = self.client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '3'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Great-booking complete!' in response.data

        # Étape 3 : Vérification des déductions
        # Points : 3 places × 3 points = 9 points déduits
        assert int(club['points']) == initial_points - 9

        # Places : 3 places déduites de la compétition
        assert int(competition['numberOfPlaces']) == initial_places - 3

    def test_complete_booking_flow_with_validations(self):
        """
        Test d'intégration : parcours avec tentatives de réservations invalides
        1. Login
        2. Tentative réservation > 12 places (doit échouer)
        3. Tentative réservation avec points insuffisants (doit échouer)
        4. Réservation valide (doit réussir)
        """
        # Login
        self.client.post('/showSummary', data={
            'email': 'admin@irontemple.com'
        })

        club = [c for c in clubs if c['name'] == 'Iron Temple'][0]
        initial_points = int(club['points'])  # Iron Temple a 4 points

        # Tentative 1 : Plus de 12 places (doit échouer)
        response = self.client.post('/purchasePlaces', data={
            'club': 'Iron Temple',
            'competition': 'Spring Festival',
            'places': '13'
        }, follow_redirects=True)

        assert b'cannot book more than 12 places' in response.data.lower()
        assert int(club['points']) == initial_points  # Points inchangés

        # Tentative 2 : Points insuffisants (doit échouer)
        # Iron Temple a 4 points, 2 places coûtent 6 points
        response = self.client.post('/purchasePlaces', data={
            'club': 'Iron Temple',
            'competition': 'Spring Festival',
            'places': '2'
        }, follow_redirects=True)

        assert b'not enough points' in response.data.lower()
        assert int(club['points']) == initial_points  # Points toujours inchangés

        # Tentative 3 : Réservation valide (1 place = 3 points, Iron Temple peut)
        response = self.client.post('/purchasePlaces', data={
            'club': 'Iron Temple',
            'competition': 'Spring Festival',
            'places': '1'
        }, follow_redirects=True)

        assert b'Great-booking complete!' in response.data
        assert int(club['points']) == initial_points - 3  # 1 place déduite

    def test_login_booking_leaderboard_flow(self):
        """
        Test d'intégration : parcours login -> booking -> vérification leaderboard
        Vérifie que les points mis à jour apparaissent dans le leaderboard
        """
        # Login
        self.client.post('/showSummary', data={
            'email': 'john@simplylift.co'
        })

        club = [c for c in clubs if c['name'] == 'Simply Lift'][0]
        initial_points = int(club['points'])

        # Réservation
        self.client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '2'
        })

        # Vérifier leaderboard
        response = self.client.get('/leaderboard')
        assert response.status_code == 200

        # Le leaderboard doit afficher les points mis à jour
        expected_points = initial_points - 6  # 2 places × 3 points
        assert str(expected_points).encode() in response.data
        assert b'Simply Lift' in response.data

    def test_invalid_email_flow(self):
        """
        Test d'intégration : parcours avec email invalide
        1. Tentative login avec email inexistant
        2. Redirection vers index
        3. Retour à la page d'accueil
        """
        response = self.client.post('/showSummary', data={
            'email': 'invalid@email.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Doit être redirigé vers la page d'accueil (index.html)
        assert b'Welcome to the GUDLFT' in response.data or b'email' in response.data.lower()
        # Ne doit PAS contenir la page welcome (pas d'authentification réussie)
        assert b'Points available' not in response.data

    def test_multiple_bookings_same_club(self):
        """
        Test d'intégration : plusieurs réservations successives du même club
        Vérifie que les points sont correctement déduits à chaque fois
        """
        # Login
        self.client.post('/showSummary', data={
            'email': 'john@simplylift.co'
        })

        club = [c for c in clubs if c['name'] == 'Simply Lift'][0]
        initial_points = int(club['points'])

        # Première réservation : 2 places
        self.client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '2'
        })

        points_after_first = int(club['points'])
        assert points_after_first == initial_points - 6

        # Deuxième réservation : 1 place pour Fall Classic
        self.client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Fall Classic',
            'places': '1'
        })

        points_after_second = int(club['points'])
        assert points_after_second == points_after_first - 3
        assert points_after_second == initial_points - 9  # Total : 6 + 3 = 9 points

    def test_leaderboard_accessible_without_login(self):
        """
        Test d'intégration : accès au leaderboard sans authentification
        Le leaderboard doit être accessible publiquement (Phase 2)
        """
        # Accès direct au leaderboard sans login
        response = self.client.get('/leaderboard')

        assert response.status_code == 200
        assert b'leaderboard' in response.data.lower() or b'points' in response.data.lower()

        # Vérifier que tous les clubs sont affichés
        for club in clubs:
            assert club['name'].encode() in response.data
            assert club['points'].encode() in response.data

    def test_booking_page_access(self):
        """
        Test d'intégration : accès à la page de réservation via URL directe
        """
        # Login d'abord
        self.client.post('/showSummary', data={
            'email': 'john@simplylift.co'
        })

        # Accès à la page de booking
        response = self.client.get('/book/Spring%20Festival/Simply%20Lift')

        assert response.status_code == 200
        assert b'Spring Festival' in response.data
        assert b'Simply Lift' in response.data
        assert b'Places' in response.data or b'places' in response.data
