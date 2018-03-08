# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for, session, escape
import sys
import util
import json
import pickle
import random
import logging
import server
import  string
import numpy as np
import pandas as pd

import logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

#fileHandler = logging.FileHandler("app.log")
#fileHandler.setFormatter(logFormatter)
#logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)


# Initialize the Flask application
app = Flask(__name__)

app.secret_key =  '\xb1\xecM|pz\x0f\xa5\x82\x90\x1a\xb9\xca2@V\x03WGS\xf2\xc3w\x88'

# Define a route for the default URL, which loads the form
@app.route('/') # First page
def form():
    return render_template('form_submit.html')

@app.route('/userClaimsInput/', methods=['POST'])
def userClaimsInput():
    QS=request.form['claim']
    print ("Query string is")
    print QS
    print request.form["button"]

    if request.form["button"] == "Try a Random Claim":
        list_claims = pickle.load(open('list_claim.pkl'))
        QS = random.choice(list_claims)
    return render_template('form_action.html', QueryString=QS)

# Second Page code down below
#Error needs to be fixed using OOP


@app.route('/results/', methods=['GET', 'POST'])
def results():
    #claim = request.args['claim']
    claim=request.form['claim']
    print ("Query string is")
    print claim
    print request.form["button"]

    if request.form["button"] == "Try a Random Claim":
        list_claims = pickle.load(open('list_claim.pkl'))
        claim = random.choice(list_claims)

    res = server.api_call(claim)
    #res_str = json.dumps(res, indent=4, sort_keys=True)
    headlines = [a['headlines'] for a in res['articles']]
    sources = [a['sources'] for a in res['articles']]
    stances = [ [s for s in a['stance'] ] for a in res['articles']]
    stances = [ np.argmax(s) - 1  for s in stances] # stance = -1, 0, 1
    #stances = [ s[2] - s[0] for s in stances]
    #print stances
    veracity = [v*100 for v in res['veracity']]
    rep   = [a['reputation'] for a  in res['articles']]
    urls   = [u for u  in res['urls']]
    n = len(sources)

    return render_template("results.html", headlines=headlines, sources=sources, n=n,\
        veracity=veracity, stances=stances, claim=claim, rep=rep, urls=urls)


@app.route('/task/', methods=['GET', 'POST'])
def task():
    task_claims = pickle.load(open('task_claims.pkl'))
    claim_idx = 0
    point_change = 0
    try:
        point_change=int(request.form['point_change'])
        claim_idx=int(request.form['claim_idx'])
    except:
        pass


    claim, gold_vera = task_claims[claim_idx]
    gold_vera = gold_vera.capitalize()
    #print claim, gold_vera


    res = server.api_call(claim, True)
    #res_str = json.dumps(res, indent=4, sort_keys=True)
    headlines = [a['headlines'] for a in res['articles']]
    sources = [a['sources'] for a in res['articles']]
    stances = [ [s for s in a['stance'] ] for a in res['articles']]
    stances = [ np.argmax(s) - 1  for s in stances] # stance = -1, 0, 1
    #stances = [ s[2] - s[0] for s in stances]
    #print stances
    veracity = [v*100 for v in res['veracity']]
    rep   = [a['reputation'] for a  in res['articles']]
    urls   = [u for u  in res['urls']]
    n = len(sources)

    if 'username' in session:
        username = session['username']
    else:
        N = 10
        session['username'] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        username = session['username']

    users = pickle.load(open('users.pkl'))
    if username not in users:
        users[username] = 0
    users[username] += point_change
    pickle.dump(users, open('users.pkl', 'w'))
    points = users[username]

    return render_template("task.html", headlines=headlines, sources=sources, n=n,\
        veracity=veracity, stances=stances, claim=claim, rep=rep, \
        urls = urls,\
        next_claim_idx=str(claim_idx+1), gold_vera=gold_vera, current_point=points)


@app.route('/ab/', methods=['GET', 'POST'])
def ab():
    task_claims = pickle.load(open('task_claims.pkl'))
    claim_idx = 0
    point_change = 0
    try:
        claim_idx=int(request.args.get('c', ''))
    except:
        pass


    claim, gold_vera = task_claims[claim_idx]
    gold_vera = gold_vera.capitalize()

    res = server.api_call(claim, True)
    #res_str = json.dumps(res, indent=4, sort_keys=True)
    headlines = [a['headlines'] for a in res['articles']]
    sources = [a['sources'] for a in res['articles']]
    stances = [ [s for s in a['stance'] ] for a in res['articles']]
    stances = [ np.argmax(s) - 1  for s in stances] # stance = -1, 0, 1
    #stances = [ s[2] - s[0] for s in stances]
    #print stances
    veracity = [v*100 for v in res['veracity']]
    rep   = [a['reputation'] for a  in res['articles']]
    urls   = [u for u  in res['urls']]
    n = len(sources)

    return render_template("ab.html", headlines=headlines, sources=sources, n=n,\
        veracity=veracity, stances=stances, claim=claim, rep=rep, \
        urls = urls,\
        gold_vera=gold_vera)


@app.route('/source_page/')
def source_page():
    source = request.args['source']

    data_all = pd.read_csv('edata_all.csv')
    rel_data = data_all[data_all.source==source]

    n = rel_data.shape[0] #This is how many articles we have for this source

    claims = []
    articles = []
    article_urls = []
    stances = []
    claim_veracities = []

    for i in range(n):
        claims = rel_data.claimHeadline.tolist()
        articles = rel_data.articleHeadline.tolist()
        article_urls = rel_data.url.tolist()
        stances = rel_data.articleHeadlineStance.tolist()
        claim_veracities = rel_data.claimTruth.tolist()

    return render_template("source_page.html", num_rows = n, source = source, claims = claims, \
            articles = articles, article_urls = article_urls, stances = stances, 
claim_veracities = claim_veracities)


@app.route('/survey/')
def survey():
    return render_template("survey.html")

@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/finish/')
def finish():
    useful = request.args.get('useful')
    easy = request.args.get('easy')
    comment = request.args.get('comment')

    log = "[SURVEY] useful=" + useful + ";easy=" + easy + ";comment=" + comment

    print log
    logger.info(log)

    return render_template("finish.html")


@app.route('/userClaimsOpinion/', methods=['POST'])
def userClaimsOpinion():
    EM = "The numbers should add up to 100!"
    truePercentage=request.form['trueInput']
    falsePercentage=request.form['falseInput']
    uncertainPercentage=request.form['unsureInput']
    total = int(truePercentage) + int(falsePercentage) + int(uncertainPercentage)
    if total != 100:
     return render_template('form_action.html', ErrorMessage=EM)
    else:
        return render_template('form_action.html')



    # sum =int(QS) + int(QS2)

    # if sum >100 or sum<100:
    #     return render_template (userClaimsInput page , errormessage="The numbers should add up to 100")

    #In string QS, replace every string with a + and then pass it as a parameter to the API (An)
    # QSNEW= "http://www.cs.utexas.edu/~atn/cgi-bin/api.cgi?claim="+ourstring


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)
