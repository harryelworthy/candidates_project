# 2020 Candidates Conditional Probabilities of Winning

Running here:

http://34.222.49.203:3000/

### Todo

* Check that cron job is running - don't think it is
* Revamp timestamping - get timestamp of just the year/day/hour min 0 or whatever, subtract everything else, then on first runthrough check that none of that timestamp exist. So can easily ping.
* Work out best way to graph historical data - probably R script that creates
interactive ggplot html, cron every hour with the new data and then saves to html,
then view.html bring it in. Maybe try ask stat prof.
* Follow up on electionbettingodds.com methodology tweet
* Think more about methodology: integrate profit fee/tax in?
    * Probably not super hard. 1/E[payout]. Tough because final profits get 10% off
    plus any profits made selling along the way? So each one has expected value of 10%
    less profit? but selling value higher? Need to scribble out
* Add funds to Betfair account and request API access
    * This would be good to integrate, probably better than PredictIt(?), shouldn't
    be too hard now that I have structure in place
* Add more on why this is important:
    * Why prediction markets are strong
    * Why conditional probability is important - we want to beat Trump!
* Try to work out hotter way to do front end - anyone good with this stuff? Or any
good frameworks? May be easier to make whole view.html come from R script, nicer
tables etc?
* Buy www.whobeatstrump.com? Better name?
* Check if PredictIt/Betfair has 'chances Bernie runs as independent' or something
or try to think if there's any other possible way to check for tail risk
* Document code better

### Installation from scratch on AWS

```bash
sudo yum install git
sudo yum install python3
sudo yum install python-virtualenv
git clone ...
cd candidates_project
python3 -m venv venv
source venv/bin/activate
export FLASK_APP=candidates
export FLASK_DEBUG=0
pip3 install -r requirements.txt
nohup flask run --host=0.0.0.0 --port=3000
```

Cron job:
```bash
SHELL=/bin/bash
0 1 * * * root source venv/bin/activate && export FLASK_APP=candidates && flask update-probs
```
