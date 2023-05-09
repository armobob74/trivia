from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from website.models import *
import pdb
import os
import json
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
    The actual game creation part is handled by websocket
    """
    return render_template('create_game.html')

@views.route('/manage-game/<string:game_id>', methods=['GET'])
def manageGame(game_id):
    """
    Get the game from the database
    display the game's current question
    """
    game = Game.query.get_or_404(game_id)
    question = Question.query.get(game.current_question)
    players = game.players
    for player in players:
        player.total_correct = sum([answer.correct for answer in player.answers])
    users = [(player.username, player.submitted_answer,player.total_correct) for player in players if player.manager == False]
    d = {
        'num_players':len(users),
        'users':users,
        'answers_submitted':len([p for p in players if p.submitted_answer]),
        'question_text':question.text,
        'answer_text':question.__dict__[question.correct],
        'num_questions':len(game.questions),
        'num_completed_questions':len(game.completed_questions),
    }
    return render_template('manage_game.html', game_id=game_id,**d)

@views.route('/populate_db/',methods=['GET','POST'])
def populateDb():
    """
    populate the database when it gets destroyed
    """
    with open('website/static/questions_ready.json') as f:
        questions = json.load(f)

    for question in questions: 
        newQuestion = Question(**question)
        db.session.add(newQuestion)

    db.session.commit()
    return redirect('/')

@views.route('/game-completed/<string:game_id>', methods=['GET'])
def gameCompleted(game_id):
    """
    """
    game = Game.query.get_or_404(game_id)
    question = Question.query.get(game.current_question)
    players = game.players
    for player in players:
        player.total_correct = sum([answer.correct for answer in player.answers])
    users = [[player.username, player.total_correct] for player in players if player.manager == False]

    max_correct = max([p.total_correct for p in players])

    users.sort(key=lambda x: x[1],reverse=True)

    for i in range(len(users)):
        users[i].append(i+1)
        

    d = {
        'num_players':len(users),
        'users':users,
        'max_correct':max_correct,
        'num_questions':len(game.questions),
        'num_completed_questions':len(game.completed_questions),
    }

    if d['num_completed_questions'] >= d['num_questions']:
        return render_template('game_completed.html', game_id=game_id,**d)
    else:
        return "This game is not yet complete."
