from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for

errorhandler = Blueprint('errorhandler', __name__)

@errorhandler.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return '404', 404
