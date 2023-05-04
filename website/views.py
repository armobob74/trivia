from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from website.models import *
import pdb
import re
import random
from .string_utils import randstr, uniquify

views = Blueprint('views', __name__)

@views.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        game_id = request.form['game_id']
        # [TODO] On front-end day, check if game exists. if it does, redirect. If not, flash message and refresh.
        return redirect(f'/game/{game_id}')
    return render_template('index.html')

@views.route('/game/<string:game_id>', methods=['GET'])
def game(game_id):
    """
    Get the game from the database
    display the game's current question
    """
    game = Game.query.get(game_id)
    if game is None:
        abort(404)
    current_question = Question.query.get(game.current_question)
    d = {
            'id':current_question.id,
            'text':current_question.text,
            'A':current_question.A,
            'B':current_question.B,
            'C':current_question.C,
            'D':current_question.D,
        }
    return render_template('game.html',question=d,game_id=game_id)



@views.route('/create-game', methods=['GET','POST'])
def createGame():
    """
    Get the game from the database
    display the game's current question
    """
    if request.method == 'POST':
        return redirect(f'/manage-game/{new_game.id}')
    return render_template('create_game.html')

@views.route('/manage-game/<string:game_id>', methods=['GET'])
def manageGame(game_id):
    """
    Get the game from the database
    display the game's current question
    """
    #[TODO] implement a nice management interface thingy.
    game = Game.query.get_or_404(game_id)
    players = game.players
    for player in players:
        player.total_correct = sum([answer.correct for answer in player.answers])
    d = {
        'num_players':len(players),
        'users':[(player.username, player.submitted_answer,player.total_correct) for player in players],
        'answers_submitted':len([p for p in players if p.submitted_answer]),
    }
    return render_template('manage_game.html', game_id=game_id,**d)

@views.route('/populate_db/',methods=['GET','POST'])
def populateDb():
    """
    populate the database when it gets destroyed
    """
    for _ in range(50):
        newQuestion = Question(
            text = randstr(16),
            A = '123',
            B = '123',
            C = 'abc',
            D = '123',
            correct = 'C'
            )
        db.session.add(newQuestion)
    db.session.commit()
    new_game = Game(
            total_questions=10,
            current_question=1,
            )
    db.session.add(new_game)
    db.session.commit()
    return redirect('/')
