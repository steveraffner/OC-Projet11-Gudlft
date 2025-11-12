"""
Tests unitaires pour la fonction purchasePlaces de server.py
"""
import pytest
from datetime import datetime, timedelta
from server import app, clubs, competitions


class TestPurchasePlaces:
    """Tests pour la route /purchasePlaces"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.client = app.test_client()
        app.config['TESTING'] = True
        
        # Sauvegarder l'état initial pour restauration
        self.initial_clubs = [club.copy() for club in clubs]
        self.initial_competitions = [comp.copy() for comp in competitions]
        
        # S'assurer que Spring Festival et Fall Classic sont dans le futur pour les tests
        for comp in competitions:
            if comp['name'] == 'Spring Festival':
                future_date = datetime.now() + timedelta(days=30)
                comp['date'] = future_date.strftime('%Y-%m-%d %H:%M:%S')
            elif comp['name'] == 'Fall Classic':
                future_date = datetime.now() + timedelta(days=90)
                comp['date'] = future_date.strftime('%Y-%m-%d %H:%M:%S')
            elif comp['name'] == 'Winter Marathon':
                # Celle-ci reste dans le passé pour tester la validation
                past_date = datetime.now() - timedelta(days=365)
                comp['date'] = past_date.strftime('%Y-%m-%d %H:%M:%S')
    
    def teardown_method(self):
        """Restaurer l'état initial après chaque test"""
        clubs.clear()
        clubs.extend(self.initial_clubs)
        competitions.clear()
        competitions.extend(self.initial_competitions)
    
    def test_purchase_places_deducts_points_from_club(self):
        """
        Test : les points du club doivent être déduits lors d'un achat
        Bug identifié : ligne 48 server.py ne déduit pas les points
        1 place = 3 points (selon spécifications)
        """
        # État initial
        club_name = "Simply Lift"
        initial_points = int([c for c in clubs if c['name'] == club_name][0]['points'])
        
        # Achat de 2 places (devrait coûter 6 points)
        response = self.client.post('/purchasePlaces', data={
            'club': club_name,
            'competition': 'Spring Festival',
            'places': '2'
        })
        
        # Vérifier que les points ont été déduits
        club_after = [c for c in clubs if c['name'] == club_name][0]
        expected_points = initial_points - (2 * 3)  # 2 places × 3 points
        
        assert int(club_after['points']) == expected_points, \
            f"Points should be {expected_points} but got {club_after['points']}"
    
    def test_purchase_places_deducts_competition_places(self):
        """
        Test : les places de la compétition doivent être déduites
        """
        competition_name = "Spring Festival"
        initial_places = int([c for c in competitions if c['name'] == competition_name][0]['numberOfPlaces'])
        
        response = self.client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': competition_name,
            'places': '3'
        })
        
        comp_after = [c for c in competitions if c['name'] == competition_name][0]
        expected_places = initial_places - 3
        
        assert int(comp_after['numberOfPlaces']) == expected_places
    
    def test_purchase_more_than_12_places_should_be_rejected(self):
        """
        Test : un club ne peut pas réserver plus de 12 places par compétition
        Bug identifié : pas de validation dans purchasePlaces
        """
        response = self.client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '13'  # Plus de 12 places
        }, follow_redirects=True)
        
        # Vérifier qu'un message d'erreur est affiché
        assert b'cannot book more than 12 places' in response.data.lower() or \
               b'maximum' in response.data.lower()
    
    def test_purchase_with_insufficient_points_should_be_rejected(self):
        """
        Test : un club ne peut pas dépenser plus de points qu'il n'en possède
        Bug identifié : pas de validation dans purchasePlaces
        Iron Temple a 4 points (peut acheter 1 place max)
        """
        response = self.client.post('/purchasePlaces', data={
            'club': 'Iron Temple',  # 4 points
            'competition': 'Spring Festival',
            'places': '2'  # Coûte 6 points, mais le club n'en a que 4
        }, follow_redirects=True)
        
        # Vérifier qu'un message d'erreur est affiché
        assert b'not enough points' in response.data.lower() or \
               b'insufficient' in response.data.lower()
    
    def test_purchase_for_past_competition_should_be_rejected(self):
        """
        Test : un club ne peut réserver que pour des compétitions futures
        Bug identifié : pas de vérification de date dans purchasePlaces
        Winter Marathon est en 2020 (passée)
        """
        response = self.client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Winter Marathon',  # Date : 2020-12-15 (passée)
            'places': '1'
        }, follow_redirects=True)
        
        # Vérifier qu'un message d'erreur est affiché
        assert b'past' in response.data.lower() or \
               b'cannot book' in response.data.lower() or \
               b'competition has already' in response.data.lower()
