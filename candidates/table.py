from flask import *
import pandas as pd
import requests as req
import os

from .db import get_db

# from .update_probs import get_current_cands

BASE_URL = "https://www.predictit.org/api/marketdata/markets/"
DEM_NOM_ID = 3633
REP_NOM_ID = 3653
PRES_ID = 3698
PARTY_ID = 2721

HEADERS = {'Content-Type':'application/json'}
PARAMETERS = {'id': str(id), 'responseType': 'JSON'}

bp = Blueprint('table', __name__, url_prefix='/')

def request_api(id):
    # Make request
    response = req.get(url=BASE_URL + str(id), json=PARAMETERS, headers=HEADERS)
    df = pd.DataFrame(response.json())
    df = pd.concat([df.drop(['contracts', 'shortName', 'name', 'image'], axis=1), df['contracts'].apply(pd.Series)], axis=1)
    return df

def get_current_cands():
    # Get presidential candidate list, add new columns with defaults
    df = request_api(PRES_ID)[['name','image','lastTradePrice']].rename(columns={'lastTradePrice':'presidentPrice'})
    df['dem'] = False
    df['rep'] = False
    df['nominationPrice'] = None

    # Get party candidates
    dem_candidates = request_api(DEM_NOM_ID)[['name','image','lastTradePrice']].rename(columns={'lastTradePrice':'nominationPrice'})
    rep_candidates = request_api(REP_NOM_ID)[['name','image','lastTradePrice']].rename(columns={'lastTradePrice':'nominationPrice'})

    # Loop through each, merge in nomination price and set party
    for name in df['name']:
        if name in dem_candidates['name'].unique():
            df.loc[df['name'] == name,'dem'] = True
            df.loc[df['name'] == name,'nominationPrice'] = dem_candidates.loc[dem_candidates['name'] == name,'nominationPrice'].unique()

    for name in df['name']:
        if name in rep_candidates['name'].unique():
            df.loc[df['name'] == name,'rep'] = True
            df.loc[df['name'] == name,'nominationPrice'] = rep_candidates.loc[rep_candidates['name'] == name,'nominationPrice'].unique()

    # Calculate conditional probability
    df['conditionalProbability'] = df['presidentPrice']/df['nominationPrice']

    return df

def get_most_recent():
    db = get_db()
    res = db.execute("""
        SELECT
          name,
          Pcond,
          Ppres,
          democrat
        FROM (
          SELECT
            *,
            MAX(dt) as max_date
          FROM probability
        ) AS s
        WHERE dt = max_date
    """).fetchall()
    df = pd.DataFrame(res)
    return df
    # select all records with that dt
    # get them into a DF

def html_dem_table():
    df = get_most_recent()
    print(df)
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
