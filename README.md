# 2020 Candidates Conditional Probabilities of Winning

Running here:

http://34.222.49.203:3000/

### Todo

* Set up SQL table (look at music app)
* Make api calls feed into SQL table and page load pull from it
* Split api calls into own module and then cron job to run every 10min (?)
* Work out best way to graph historical data - R script to HTML?? or just ggplot
python? or what
* Follow up on electionbettingodds.com api/methodology and call/scrape
* Add more on why this is important:
    * Why prediction markets are strong
    * Why conditional probability is important - we want to beat Trump!


### Commands run on AWS

'''bash
sudo yum install git
sudo yum install python3
sudo yum install python-virtualenv
git clone ...
cd ...
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
FLASK_APP=app.py FLASK_DEBUG=0 python3 -m flask run --host=0.0.0.0 --port=3000
'''
