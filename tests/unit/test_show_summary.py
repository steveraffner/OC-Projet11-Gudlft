"""
Tests unitaires pour la fonction showSummary de server.py
"""
import pytest
from server import app, clubs


class TestShowSummary:
    """Tests pour la route /showSummary"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.client = app.test_client()
        app.config['TESTING'] = True
    
    def test_show_summary_with_valid_email(self):
        """Test : affichage du résumé avec un email valide"""
        response = self.client.post('/showSummary', data={
            'email': 'john@simplylift.co'
        })
        assert response.status_code == 200
        assert b'Welcome' in response.data
        assert b'john@simplylift.co' in response.data
    
    def test_show_summary_with_invalid_email_should_not_crash(self):
        """
        Test : un email inexistant ne doit PAS faire crasher l'application
        Bug identifié : IndexError quand email n'existe pas (ligne 29 server.py)
        """
        response = self.client.post('/showSummary', data={
            'email': 'nonexistent@email.com'
        })
        # L'application ne doit pas crasher (code 500)
        # Elle doit renvoyer une erreur propre (flash message + redirection)
        assert response.status_code != 500
        assert b'Sorry' in response.data or response.status_code == 302
