from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from website.models import *
import pdb
import re
import random
from .string_utils import randstr

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


# could maybe be done better as a socketio event
@views.route('/submit-answer', methods=['POST'])
def submitAnswer():
    username = request.form['username']
    game_id = request.form['game_id']
    question_id = request.form['question_id']
    answer_letter = request.form['answer']
    current_question = Question.query.get(question_id)
    isCorrect = current_question.correct == answer_letter
    player = Player.query.filter_by(username=username).first()

    if player is None: #this is the case if player just submitted a new username
        player = Player(
                game=game_id,
                manager=False,
                username=username,
                )
        db.session.add(player)
        db.session.commit()
    elif player.game != game_id: # this is the case if player was playing a different game
        player.manager=False
        player.game = game_id
        db.session.add(player)
        db.session.commit()

    answer = Answer(
            question=question_id,
            game=game_id,
            player=player.id,
            answer_letter=answer_letter,
            correct=isCorrect
            )
    db.session.add(answer)
    db.session.commit()

    return redirect(f'/game/{game_id}')


@views.route('/create-game', methods=['GET','POST'])
def createGame():
    """
    Get the game from the database
    display the game's current question
    """
    if request.method == 'POST':
        all_games = Game.query.all()
        if all_games is None:
            max_id = 0
        else:
            max_id = max([x.id for x in all_games])
        new_game_id = max_id + 1
        new_game = Game(
                id=new_game_id,
                total_questions=int(request.form['total_questions']),
                current_question=1,
                )

        username = request.form['username']
        # set the creator as manager
        creator = Player.query.filter_by(username=username).first()
        if creator is None:
            creator = Player(
                    username=username
                    )
        creator.manager = True
        creator.game = new_game.id
        db.session.add(creator)
        db.session.add(new_game)
        db.session.commit()
        return redirect(f'/manage-game/{new_game.id}')
    return render_template('create_game.html')

@views.route('/manage-game/<string:game_id>', methods=['GET','POST'])
def manageGame(game_id):
    """
    Get the game from the database
    display the game's current question
    """
    #[TODO] implement a nice management interface thingy.
    game = Game.query.get_or_404(game_id)
    players = game.players
    d = {
        'num_players':len(players),
        'answers_submitted':len([p for p in players if p.submitted_answer]),
    }
    return render_template('manage_game.html', game_id=game_id,**d)

@views.route('/populate_db/',methods=['GET','POST'])
def populateDb():
    """
    populate the database when it gets destroyed
    """
    for _ in range(10):
        newQuestion = Question(
            text = randstr(16),
            A = '123',
            B = '123',
            C = 'abc',
            D = '123',
            correct = random.choice('ABCD')
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
