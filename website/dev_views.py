# the routes here help us develop templates, macros, etc.

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from website.models import *
import pdb
import os
import json
from .string_utils import randstr, uniquify

dev_views = Blueprint('dev_views', __name__)

@dev_views.route('/timer-macro', methods=['GET','POST'])
def timerMacro():
    return render_template('timer_dev.html')
