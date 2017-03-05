#!env/bin/python
import flask
import tweepy
from flask import Flask, request, session, render_template, redirect, jsonify

app = Flask(__name__)

# config
CONSUMER_KEY = 'pZae9lin4TMTp2FExsCgRAbsi'
CONSUMER_SECRET = '9pJFXTsOx9SpQm2Ecb5uWBT8sucka56B3BFUn7NPnS80ux5RoD'
db = dict() # user tokens could be stored in a database

@app.route("/")
def index():
    """Main page of app"""
    return render_template('index.html')

@app.route("/authorize")
def authorize():
    """Send request token to Twitter's API for app authorization"""
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    try:
        # twitter's authentication url
    	redirect_url = auth.get_authorization_url()
        # set the request token
    	session['request_token'] = auth.request_token
    except tweepy.TweepError:
    	print 'Error! Failed to get request token'

    return redirect(redirect_url)

@app.route("/verify")
def verify():
    """Obtain the user's access token and connect to Twitter's API"""
    verifier = request.args.get('oauth_verifier')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    token = session.get('request_token')
    del session['request_token'] # the authorization request ended
    auth.request_token = token

    try:
    	auth.get_access_token(verifier)
    except tweepy.TweepError:
    	print 'Error! Failed to get access token.'

    # connect to API
    api = tweepy.API(auth)
    db['api'] = api

    # store user's tokens
    db['access_token_key'] = auth.access_token
    db['access_token_secret'] = auth.access_token_secret

    return redirect('./followers/followers')

@app.route("/followers/followers")
def get_2nd_followers():
    api = db['api']
    followers = api.followers()
    l = []
    for follower in followers:
        entry = (follower.screen_name, 1)
        l.append(entry)
    db['followers'] = l

    return render_template('followers.html', followers=l)

@app.route("/followers/followers/json", methods=['GET'])
def json_2nd_followers():
    followers = db['followers']
    return jsonify({'2nd_followers': {follower[0]: follower[1] for follower in followers}})

if __name__ == '__main__':
    # encryption key for session
    app.secret_key = '3faE64iwqJDNBGC5nQ60'
    app.run(debug=True)
