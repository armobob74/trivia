from website import create_app, db, Game, CompletedQuestion, Question, Player, Answer
import pdb
import random
from flask_socketio import SocketIO, join_room
from sqlalchemy.exc import IntegrityError
from website.string_utils import uniquify
from flask import request, render_template

def create_all():
    """ Create all db tables. Meant to be called from command line."""
    with app.app_context():
        db.create_all()

app = create_app()

socketio = SocketIO(app)
create_all()


@socketio.on('question_card_request')
def question_card(question_id):
    """
    let's implement an infinite scroll, because why not?
    """
    question = Question.query.get(question_id)
    if question is None:
        #front end will know to stop infinite scroll
        socketio.emit('question_card_response',False) 
    else:
        card_data = {
                    'question':question.text,
                    'answer':question.__dict__[question.correct],
                    'question_id':question_id
                }
        question_card_html = render_template('question_card.html', **card_data)
        msg = {
                "question_card":question_card_html,
                }
        socketio.emit('question_card_response',msg,room=request.sid)

@socketio.on('join')
def on_join(data):
    """
    When client requests to join a room, add them to the room. Rooms are the same as game_id.
    Also emit a response letting all room members know that another player has joined.
    """
    room = data['room']
    username = data['username']
    join_room(room)
    socketio.emit('join_room_response',f'User {username} has joined game room {room}',room=room)

@socketio.on('refresh_order')
def refresh_order(data):
    """
    When server recieves refresh_order from a manager client, it will change the game's current_question and then
    send a refresh_order to all clients connected to the game room.

    This is how the game moves to the next question.
    """
    room = data['room'] # room format is: f'managing {game_id}'
    game_id = int(room.split(' ')[-1])
    if room.startswith('managing'): #only send refresh if being sent from a manager
        game = Game.query.get(game_id)
        completed_question = CompletedQuestion(
                game=game_id,
                question=game.current_question
                )

        db.session.add(completed_question)
        db.session.commit()

        # select a new question that has not yet been attempted
        completed_question_ids = {q.question for q in game.completed_questions}

        game_question_ids = {q.id for q in game.questions}
        unseen_question_ids = game_question_ids - completed_question_ids

        if len(unseen_question_ids) == 0:
            socketio.emit('game_completed_notification', room=room)
            socketio.emit('game_completed_notification', room=game_id)
            return
        

        next_question_id = random.choice(list(unseen_question_ids))
        game.current_question = next_question_id

        #refresh all players' submitted_answer fields
        for player in game.players:
            player.submitted_answer = False

        db.session.commit()

        # order refresh
        room_to_refresh = game_id
        question = Question.query.get(next_question_id)
        new_question_msg = {
        'question_text':question.text,
        'answer_text':question.__dict__[question.correct],
                }
        socketio.emit('refresh_order','REFRESH',room=room_to_refresh)
        socketio.emit('refresh_order_response',new_question_msg,room=request.sid)


#doing this because I don't want form to be re-eneabled by a simple url-change or refresh.
@socketio.on('check_answer_submitted')
def checkAnswerSubmitted(data):
    username = data['username']
    game_id = data['game_id']
    question_id = data['question_id']

    player = Player.query.filter_by(username=username).first()
    game_answers = [a for a in player.answers if a.game == game_id]
    answered_question_ids = [a.question for a in game_answers]

    if question_id in answered_question_ids:
        answer_submitted = True
        i = answered_question_ids.index(question_id)
        answer = game_answers[i].answer_letter
    else:
        answer_submitted = False
        answer = ''

    socketio.emit('check_answer_submitted_response',{'bool':answer_submitted,'answer':answer})

@socketio.on('update_manager_request')
def updateManager(data):
    """
    update the manager when a player submits an answer
    """
    print("\n"*3)
    print("Recieved update_manager_request from", data['username'])
    print("\n"*3)
    username = data['username']
    game_id = data['game_id']
    question_id = data['question_id']

    current_question = Question.query.get_or_404(question_id)
    answer_letter = data['answer_letter']
    correct_tf = answer_letter == current_question.correct

    player = Player.query.filter_by(username=username).first()
    player.submitted_answer = True
    db.session.commit()
    room = f'managing {game_id}'
    msg = {
            'username':username,
            'game_id':game_id,
            'question_id':question_id,
            'correct_tf':correct_tf
    }
    socketio.emit('update_manager_response', msg, room=room)


@socketio.on('create_player_request')
def createPlayer(msg):
    """
    creates a non-manager player
    lets the relevant management console know that a player has been created.
    msg = {
        'username':str,
        'game_id':str
    }
    """
    # make sure username is unique.
    # add a special code after the username, like (2).

    player = Player(
            game=msg['game_id'],
            manager=False,
            username=msg['username'],
            )
    try:
        db.session.add(player)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        usernames = [p.username for p in Player.query.all()]
        username = uniquify(msg['username'],usernames) 
        msg['username'] = username
        player = Player(
                game=msg['game_id'],
                manager=False,
                username=username,
                )
        db.session.add(player)
        db.session.commit()

    room = f'managing {msg["game_id"]}'

    # notifies client that username was created. Necessary in case there is a 
    # conflict and the username cookie needs to be different than the one originally
    # requested.
    socketio.emit('create_player_response', {'username':msg['username']}, room=request.sid)

    # notifies the manager console.
    socketio.emit('player_created_notification', msg, room=room)


@socketio.on('submit_answer_request')
def submitAnswer(msg):
    print("submitting answer")
    username = msg['username']
    game_id = msg['game_id']
    question_id = msg['question_id']
    answer_letter = msg['answer_letter']

    current_question = Question.query.get(question_id)
    isCorrect = current_question.correct == answer_letter
    player = Player.query.filter_by(username=username).first()

    if player is None: # should be impossible, but just in case.
        createPlayer(msg={
            'game_id':game_id,
            'username':username,
            })
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

    #socketio.emit('submit_answer_response','Answer submitted',room=game_id)

@socketio.on('create_game_request')
def create_game(msg):
        all_games = Game.query.all()
        if len(all_games) == 0:
            max_id = 0
        else:
            max_id = max([x.id for x in all_games])
        new_game_id = max_id + 1

        new_game = Game(
                id=new_game_id,
                total_questions=len(msg['selected_questions']),
                questions=[Question.query.get(qid) for qid in msg['selected_questions']],
                current_question=1,
                )

        username = msg['username']
        # set the creator as manager
        creator = Player.query.filter_by(username=username).first()
        if creator is None:
            unique_username = username
        else:
            usernames = [p.username for p in Player.query.all()]
            unique_username = uniquify(username,usernames)
        creator = Player(
                username=unique_username
                )
        creator.manager = True
        creator.game = new_game.id
        db.session.add(creator)
        db.session.add(new_game)
        db.session.commit()
        msg['username'] = unique_username
        response_message = {
                    'username':unique_username,
                    'game_id':new_game_id
                }
        socketio.emit('create_game_response', response_message, room=request.sid)



if __name__ == '__main__':
    socketio.run(app,debug=True)
