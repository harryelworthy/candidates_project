from flask import *
import pandas as pd
import requests as req
import os

from .db import get_db

# from .update_probs import get_current_cands

bp = Blueprint('table', __name__, url_prefix='/')

def get_most_recent():
    db = get_db()
    res = db.execute("""
        SELECT
          name,
          Pcond,
          Ppres,
          democrat
        FROM
          probability AS [data]
        WHERE
          dt = (SELECT MAX(dt) FROM probability)
    """).fetchall()
    df = pd.DataFrame(res)
    return df
    # select all records with that dt
    # get them into a DF

def html_dem_table():
    df = get_most_recent()
    df = df.rename(columns={0:"name", 1:"Pcond", 2:"Ppres", 3:"democrat"})
    # Drop low candidates, give dumb numbers
    df = df[df['Ppres'] > 0.02]
    df['Pcond'] = df['Pcond']*100
    df['conditional chance to win'] = df['Pcond'].map('{:,.2f}%'.format)
    df = df[df['democrat'] == True]
    df = df[['name', 'conditional chance to win']]
    df = df.set_index('name')
    df = df.sort_values(['conditional chance to win'], ascending=[False])
    del df.index.name
    return df.to_html(classes='democrats')

def html_rep_table():
    df = get_most_recent()
    df = df.rename(columns={0:"name", 1:"Pcond", 2:"Ppres", 3:"democrat"})
    # Drop low candidates, give dumb numbers
    df = df[df['Ppres'] > 0.02]
    df['Pcond'] = df['Pcond']*100
    df['conditional chance to win'] = df['Pcond'].map('{:,.2f}%'.format)
    df = df[df['democrat'] == False]
    df = df[['name', 'conditional chance to win']]
    df = df.set_index('name')
    df = df.sort_values(['conditional chance to win'], ascending=[False])
    del df.index.name
    return df.to_html(classes='republicans')


@bp.route("/")
def show_table():
    return render_template('view.html',tables=[html_dem_table(),html_rep_table()],
    titles = ['x','Democrats','Republicans'])

@bp.route("/about")
def show_about():
    return render_template('about.html')
