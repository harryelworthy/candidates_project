from flask import *
import pandas as pd
import requests as req
import os

from .update_probs import get_current_cands

bp = Blueprint('table', __name__, url_prefix='/')

def html_dem_table():
    df = get_current_cands()
    # Drop low candidates, give dumb numbers
    df = df[df['presidentPrice'] > 0.02]
    df['image'] = '<img src="' + df['image'].astype(str) + '>'
    df['conditionalProbability'] = df['conditionalProbability']*100
    df['conditional chance to win'] = df['conditionalProbability'].map('{:,.2f}%'.format)
    df = df[df['dem'] == True]
    df = df[['name', 'conditional chance to win']]
    df = df.set_index('name')
    del df.index.name
    return df.to_html(classes='democrats')

def html_rep_table():
    df = get_current_cands()
    # Drop low candidates, give dumb numbers
    df = df[df['presidentPrice'] > 0.02]
    df['image'] = '<img src="' + df['image'].astype(str) + '>'
    df['conditionalProbability'] = df['conditionalProbability']*100
    df['conditional chance to win'] = df['conditionalProbability'].map('{:,.2f}%'.format)
    df = df[df['rep'] == True]
    df = df[['name', 'conditional chance to win']]
    df = df.set_index('name')
    del df.index.name
    return df.to_html(classes='republicans')


@bp.route("/")
def show_table():
    return render_template('view.html',tables=[html_dem_table(),html_rep_table()],
    titles = ['x','Democrats','Republicans'])

@bp.route("/about")
def show_about():
    return render_template('about.html')
