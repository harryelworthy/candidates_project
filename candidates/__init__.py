import os

from flask import Flask
from . import db

from flask_apscheduler import APScheduler

from flask import *
import pandas as pd
import requests as req

from .db import get_db
#from .update_probs import add_to_db

import datetime
import click

from flask.cli import with_appcontext

#from apscheduler.schedulers.background import BackgroundScheduler

BASE_URL = "https://www.predictit.org/api/marketdata/markets/"
DEM_NOM_ID = 3633
REP_NOM_ID = 3653
PRES_ID = 3698
PARTY_ID = 2721

HEADERS = {'Content-Type':'application/json'}
PARAMETERS = {'id': str(id), 'responseType': 'JSON'}




class Config(object):
    JOBS = [
        {
            'id': 'update_probs',
            'func': '__init__:update_probs',
            'args': (),
            'trigger': 'interval',
            'hours': 1
        }
    ]

    SCHEDULER_API_ENABLED = True



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

#@click.command('update-probs')
#@with_appcontext
#@cron.interval_schedule(hours=1)
def update_probs():
    add_to_db()
    return



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
    return
#    click.echo('Updated probabilities')




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



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'candidates.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    scheduler = APScheduler()
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()

    from . import db
    db.init_app(app)

    from . import table
    app.register_blueprint(table.bp)

    from . import update_probs
    app.register_blueprint(update_probs.bp)

    app.cli.add_command(update_probs.add_to_db)
    return app
