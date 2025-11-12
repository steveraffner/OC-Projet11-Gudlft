"""
Tests unitaires pour la route /leaderboard (tableau d'affichage des clubs)
Phase 2 du projet
"""
import pytest
from server import app, clubs


class TestLeaderboard:
    """Tests pour la route /leaderboard"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.client = app.test_client()
        app.config['TESTING'] = True
    
    def test_leaderboard_accessible_without_login(self):
        """
        Test : le tableau d'affichage doit être accessible sans connexion
        """
        response = self.client.get('/leaderboard')
        assert response.status_code == 200
        assert b'Leaderboard' in response.data or b'Points Board' in response.data
    
    def test_leaderboard_displays_all_clubs(self):
        """
        Test : le tableau doit afficher tous les clubs avec leurs points
        """
        response = self.client.get('/leaderboard')
        
        # Vérifier que tous les clubs sont affichés
        for club in clubs:
            assert club['name'].encode() in response.data
            assert club['points'].encode() in response.data
    
    def test_leaderboard_shows_updated_points(self):
        """
        Test : le tableau doit afficher les points à jour
        """
        # Modifier temporairement les points d'un club
        original_points = clubs[0]['points']
        clubs[0]['points'] = '999'
        
        response = self.client.get('/leaderboard')
        assert b'999' in response.data
        
        # Restaurer
        clubs[0]['points'] = original_points
