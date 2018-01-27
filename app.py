# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for
import sys
import util
import json
import pickle
import random
import logging
import server
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
    stances = [ [s*100 for s in a['stance'] ] for a in res['articles']]
    veracity = [v*100 for v in res['veracity']]
    rep   = [100*a['reputation'] for a  in res['articles']]
    urls   = [u for u  in res['urls']]
    n = len(sources)

    # return render_template("results.html", headlines=headlines, sources=sources, n=n,\
    #     veracity=veracity, stances=stances, claim=claim, rep=rep, \
    #     clf_vera_coef=res["clf_vera_coef"], clf_vera_intc=res["clf_vera_intc"].tolist(), urls = urls)
    return render_template("InterfaceAPrime.html", headlines=headlines, sources=sources, n=n,\
        veracity=veracity, stances=stances, claim=claim, rep=rep, \
        clf_vera_coef=res["clf_vera_coef"], clf_vera_intc=res["clf_vera_intc"].tolist(), urls = urls)


@app.route('/source_page/')
def source_page():
    s = request.args['source']

    data_all = pd.read_csv('edata_all.csv')
    rel_data = data_all[data_all.source==s]

    n = rel_data.shape[0] #This is how many articles we have for this source

    claims = []
    articles = []
    article_urls = []
    pred_stances = []
    pred_claim_veracities = []

    for i in range(n):
        claims = rel_data.claimHeadline.tolist()
        articles = rel_data.articleHeadline.tolist()
        article_urls = rel_data.url.tolist()
        pred_stances.append("Predicted Stance "+str(i)+" here")
        pred_claim_veracities.append("Predicted Claim Veracity "+str(i)+" here")

    return render_template("source_page.html", num_rows = n, source = s, claims = claims, \
            articles = articles, article_urls = article_urls, pred_stances = pred_stances, 
            pred_claim_veracities = pred_claim_veracities)

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
