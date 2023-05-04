from website import create_app, db, Game, CompletedQuestion, Question, Player
import pdb
import random
from flask_socketio import SocketIO, join_room

def create_all():
    """ Create all db tables. Meant to be called from command line."""
    with app.app_context():
        db.create_all()

app = create_app()
socketio = SocketIO(app)
create_all()

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

        #game = Game.query.get(game_id) #reload the query to get the relevant completed_questions (is this necessary?)
        # select a new question that has not yet been attempted
        # [TODO] find a way to do this more efficiently lol
        completed_question_ids = {q.question for q in game.completed_questions}
        all_question_ids = {q.id for q in Question.query.all()}
        unseen_question_ids = all_question_ids - completed_question_ids
        next_question_id = random.choice(list(unseen_question_ids))
        game.current_question = next_question_id

        #refresh all players' submitted_answer fields
        for player in game.players:
            player.submitted_answer = False

        db.session.commit()

        # order refresh
        room_to_refresh = game_id
        socketio.emit('refresh_order','REFRESH',room=room_to_refresh)


#doing this with socketio instead of a route because I don't want form to be re-eneabled by a simple url-change or refresh.
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

# [TODO] add a submitted_question field to Player if possible, in order to prevent count from resetting with each page refresh.
# [TODO] add something on the front end (manage_game.html) to handle this message
@socketio.on('update_manager')
def updateManager(data):
    username = data['username']
    game_id = data['game_id']
    question_id = data['question_id']
    player = Player.query.filter_by(username=username).first()
    pdb.set_trace() 
    player.submitted_answer = True
    db.session.commit()
    room = f'managing {game_id}'
    msg = {
            'username':username,
            'game_id':game_id,
            'question_id':question_id
    }
    socketio.emit('update_manager', msg, room=room)



if __name__ == '__main__':
    socketio.run(app,debug=True)
