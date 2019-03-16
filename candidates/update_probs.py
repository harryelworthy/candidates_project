import pandas as pd
import requests as req
import datetime
import click

from .db import get_db
from flask.cli import with_appcontext
from flask import Blueprint

BASE_URL = "https://www.predictit.org/api/marketdata/markets/"
DEM_NOM_ID = 3633
REP_NOM_ID = 3653
PRES_ID = 3698
PARTY_ID = 2721

HEADERS = {'Content-Type':'application/json'}
PARAMETERS = {'id': str(id), 'responseType': 'JSON'}

bp = Blueprint('update', __name__, url_prefix='/u')


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

@click.command('update-probs')
@with_appcontext
def add_to_db():
    db = get_db()
    dt = datetime.datetime.now()
    error = None
    df = get_current_cands()
    if error is None:
        for index, c in df.iterrows():
            db.execute(
                'INSERT INTO probability (dt, name, democrat, Pnom, Ppres, Pcond) VALUES (?, ?, ?, ?, ?, ?)',
                    (dt,
                    c['name'],
                    c['dem'],
                    c['nominationPrice'],
                    c['presidentPrice'],
                    c['conditionalProbability'])
            )
    db.commit()
    click.echo('Updated probabilities')
