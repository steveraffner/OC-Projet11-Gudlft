import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    """
    Charge la liste des clubs depuis le fichier clubs.json.

    Returns:
        list: Liste des dictionnaires contenant les informations des clubs
              (name, email, points)
    """
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    """
    Charge la liste des compétitions depuis le fichier competitions.json.

    Returns:
        list: Liste des dictionnaires contenant les informations des compétitions
              (name, date, numberOfPlaces)
    """
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    """
    Page d'accueil de l'application.
    Affiche le formulaire de connexion par email.

    Returns:
        str: Template HTML de la page d'accueil
    """
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    """
    Authentifie un secrétaire de club via son email.
    Affiche le tableau de bord avec les compétitions disponibles.

    Form Data:
        email (str): Adresse email du secrétaire du club

    Returns:
        str: Template HTML du tableau de bord si l'email existe,
             redirection vers l'accueil avec message d'erreur sinon
    """
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html', club=club, competitions=competitions)
    except IndexError:
        flash("Sorry, that email was not found.")
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    """
    Affiche la page de réservation pour une compétition spécifique.

    Args:
        competition (str): Nom de la compétition
        club (str): Nom du club

    Returns:
        str: Template HTML de la page de réservation si le club et la compétition
             existent, sinon retour au tableau de bord avec message d'erreur
    """
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    """
    Traite une réservation de places pour une compétition.

    Validations effectuées:
    - La compétition doit être future (pas passée)
    - Maximum 12 places par réservation
    - Le club doit avoir suffisamment de points (1 place = 3 points)

    Form Data:
        competition (str): Nom de la compétition
        club (str): Nom du club
        places (int): Nombre de places à réserver

    Returns:
        str: Template HTML du tableau de bord avec message de confirmation
             ou d'erreur selon le résultat de la validation
    """
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    # Calculer le coût en points (1 place = 3 points)
    points_cost = placesRequired * 3
    club_points = int(club['points'])

    # Validation 1 : vérifier que la compétition est dans le futur
    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < datetime.now():
        flash('Cannot book places for past competitions.')
        return render_template('welcome.html', club=club, competitions=competitions)

    # Validation 2 : maximum 12 places par réservation
    if placesRequired > 12:
        flash('You cannot book more than 12 places per competition.')
        return render_template('welcome.html', club=club, competitions=competitions)

    # Validation 3 : vérifier que le club a assez de points
    if points_cost > club_points:
        flash(f'Not enough points. You need {points_cost} points but only have {club_points}.')
        return render_template('welcome.html', club=club, competitions=competitions)

    # Déduire les places de la compétition
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired

    # Déduire les points du club
    club['points'] = str(club_points - points_cost)

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/leaderboard')
def leaderboard():
    """
    Affiche le tableau des points de tous les clubs
    Accessible sans authentification (Phase 2)
    """
    # Trier les clubs par points décroissants
    sorted_clubs = sorted(clubs, key=lambda x: int(x['points']), reverse=True)
    return render_template('leaderboard.html', clubs=sorted_clubs)


@app.route('/logout')
def logout():
    """
    Déconnecte l'utilisateur et redirige vers la page d'accueil.

    Returns:
        werkzeug.wrappers.Response: Redirection vers la page d'accueil
    """
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
