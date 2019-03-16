from flask import *
import pandas as pd
import requests as req
import os

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
    df = df.sort_values(['conditional chance to win'], ascending=[False])
    del df.index.name
    return df.to_html(classes='democrats')

def html_rep_table():
    df = get_current_cands()
    # Drop low candidates, give dumb numbers
    df = df[df['presidentPrice'] > 0.02]
    df['image'] = '<img src="' + df['image'].astype(str) + '>'
    df['conditionalProbability'] = df['conditionalProbability']*100
    df['conditional chance to win'] = df['conditionalProbability'].map('{:,.2f}'.format)
    df = df[df['rep'] == True]
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
