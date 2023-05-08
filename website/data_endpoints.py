from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from website.models import *
import pdb
import os
import json
from .string_utils import randstr, uniquify

data_endpoints = Blueprint('data_endpoints', __name__)

@data_endpoints.route('/get-current-question/<game_id>', methods=['GET'])
def getCurrentQuestion(game_id):
    """
    Not used rn, but kept as example.

    Originally was gonna use this to update management console when "next question" was pressed,
    but it's easier to do that with websocket right now. This is because all of the infrastructure
    is already in place for that.
    """
    game = Game.query.get_or_404(game_id)
    question = Question.query.get_or_404(game.current_question)
    d = {
        'question_text':question.text,
        'answer_text':question.__dict__[question.correct],
    }
    return d
