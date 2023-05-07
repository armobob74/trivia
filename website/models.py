from flask_sqlalchemy import SQLAlchemy
import pdb

db = SQLAlchemy()

# gameQuestions is a helper table to manage the many-to-many relationship between Game and Question
# (each game has multiple questions and each question can be in multiple games)
# using Table instead of Model because Table doesn't require db.session.add()
# you can directly append() and remove()
# for example: 
# question = Question.query.first()
# game = Game.query.first()
# game.questions.append(question)
# db.session.commit()
gameQuestions = db.Table('game_question',
                    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True),
                    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
                )

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    total_questions = db.Column(db.Integer)
    players = db.relationship('Player')
    completed_questions = db.relationship('CompletedQuestion')
    current_question = db.Column(db.Integer, db.ForeignKey('question.id'))
    questions = db.relationship('Question', secondary=gameQuestions, lazy='subquery',
                                backref=db.backref('pages', lazy=True))

class CompletedQuestion(db.Model):
    """
    Store the completed questions for each game
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    game = db.Column(db.Integer, db.ForeignKey('game.id'))
    question = db.Column(db.Integer, db.ForeignKey('question.id'))
    

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    game = db.Column(db.Integer, db.ForeignKey('game.id'))
    answers = db.relationship('Answer')
    manager = db.Column(db.Boolean, default=False)
    submitted_answer = db.Column(db.Boolean, default=False) # keep track of if player has submitted an answer to game's current_question
    username = db.Column(db.String,unique=True)


class Answer(db.Model):
    """
    each answer submitted by a player
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    question = db.Column(db.Integer, db.ForeignKey('question.id'))
    game = db.Column(db.Integer, db.ForeignKey('game.id'))
    player = db.Column(db.Integer, db.ForeignKey('player.id'))
    answer_letter = db.Column(db.String(length=1))
    correct = db.Column(db.Boolean)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    text = db.Column(db.String)
    A = db.Column(db.String)
    B = db.Column(db.String)
    C = db.Column(db.String)
    D = db.Column(db.String)
    correct = db.Column(db.String(length=1), nullable=False) #the letter of the correct answer
    difficulty = db.Column(db.Integer)

