from flask import *
import pandas as pd
import requests as req

BASE_URL = "https://www.predictit.org/api/marketdata/markets/"
DEM_NOM_ID = 3633
REP_NOM_ID = 3653
PRES_ID = 3698
PARTY_ID = 2721

HEADERS = {'Content-Type':'application/json'}
PARAMETERS = {'id': str(id), 'responseType': 'JSON'}


def request_api(id):
    # Make request
    response = req.get(url=BASE_URL + str(id), json=PARAMETERS, headers=HEADERS)
    df = pd.DataFrame(response.json())
    df = pd.concat([df.drop(['contracts', 'shortName', 'name', 'image'], axis=1), df['contracts'].apply(pd.Series)], axis=1)
    return df

def get_current_cands():
    # Get presidential candidate list, add new columns with defaults
    pres_candidates = request_api(PRES_ID)[['name','image','lastTradePrice']].rename(columns={'lastTradePrice':'presidentPrice'})
    pres_candidates['dem'] = False
    pres_candidates['rep'] = False
    pres_candidates['nominationPrice'] = None

    # Get party candidates
    dem_candidates = request_api(DEM_NOM_ID)[['name','image','lastTradePrice']].rename(columns={'lastTradePrice':'nominationPrice'})
    rep_candidates = request_api(REP_NOM_ID)[['name','image','lastTradePrice']].rename(columns={'lastTradePrice':'nominationPrice'})

    # Loop through each, merge in nomination price and set party
    for name in pres_candidates['name']:
        if name in dem_candidates['name'].unique():
            pres_candidates.loc[pres_candidates['name'] == name,'dem'] = True
            pres_candidates.loc[pres_candidates['name'] == name,'nominationPrice'] = dem_candidates.loc[dem_candidates['name'] == name,'nominationPrice'].unique()

    for name in pres_candidates['name']:
        if name in rep_candidates['name'].unique():
            pres_candidates.loc[pres_candidates['name'] == name,'rep'] = True
            pres_candidates.loc[pres_candidates['name'] == name,'nominationPrice'] = rep_candidates.loc[rep_candidates['name'] == name,'nominationPrice'].unique()

    # Calculate conditional probability
    pres_candidates['conditionalProbability'] = pres_candidates['presidentPrice']/pres_candidates['nominationPrice']

    # Drop low candidates, give dumb numbers
    pres_candidates = pres_candidates[pres_candidates['presidentPrice'] > 0.02]

    # Sort by Party, Conditional Probability
    pres_candidates = pres_candidates.sort_values(by=['rep', 'conditionalProbability'], ascending=False)

    return pres_candidates


def html_cand_table():
    df = get_current_cands()
    df['image'] = '<img src="' + df['image'].astype(str) + '>'
    df['conditionalProbability'] = df['conditionalProbability']*100
    df['conditional chance to win'] = df['conditionalProbability'].map('{:,.2f}%'.format)
    df['party'] = 'Democrat'
    df.loc[df['rep'] == True,'party'] = 'Republican'
    df = df[['name', 'image', 'party', 'conditional chance to win']]
    return df.to_html()



app = Flask(__name__)

@app.route("/table")
def show_table():
    return render_template('view.html',tables=[html_cand_table()],
    titles = ['Chances candidates win given they are nominated, based on PredictIt prices'])

if __name__ == "__main__":
    app.run(host='0.0.0.0')
