#!env/bin/python
import sys
import tweepy
from time import sleep
from flask import Flask, request, session, render_template,\
                  redirect, jsonify, abort

# CONFIG
CONSUMER_KEY = 'pZae9lin4TMTp2FExsCgRAbsi'
CONSUMER_SECRET = '9pJFXTsOx9SpQm2Ecb5uWBT8sucka56B3BFUn7NPnS80ux5RoD'
db = dict() # user tokens could be stored in a database

# UTILS
def limit_handled(cursor):
    """Handle API rate limit by waiting 15 minutes and continue process"""
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            sleep(15 * 60)

# FLASK APP
app = Flask(__name__)

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
def get_sub_followers():
    """Construct 2nd line followers for user"""
    try:
        api = db['api']
    except KeyError:
        print 'Error! No API object found.'
        abort(403)

    db['followers'] = {}
    # followers = api.followers_ids()
    # build tree of followers and sub_followers
    for follower in limit_handled(tweepy.Cursor(api.followers_ids)):
        sub_followers = []
        # for sub_follower in limit_handled(tweepy.Cursor(api.followers_ids, id=follower)):
        #     sub_followers.append(sub_follower)
        db['followers'][follower] = sub_followers

    db['sub_followers'] = {}
    # count sub_followers subscriptions
    for follower, sub_followers in db['followers'].items():
        for sub_follower in sub_followers:
            # sub_follower cannot be user's own follower
            if not sub_follower in db['followers']:
                # update counter
                db['sub_followers'][sub_follower] = db['sub_followers'].\
                                                    get(sub_follower, 0) + 1

    # convert dict of sub_followers to list for html
    sub_followers = []
    for sub_follower, count in db['sub_followers'].items():
        sub_followers.append((sub_follower, count))

    ##########

    # db['followers'] = {}
    # # build tree of followers and sub_followers
    # for follower in limit_handled(tweepy.Cursor(api.followers).items()):
    #     follower_name = follower.screen_name
    #     sub_followers = []
    #     # for sub_follower in limit_handled(tweepy.Cursor(api.followers, screen_name=follower_name).items()):
    #     #     sub_follower_name = sub_follower.screen_name
    #     #     sub_followers.append(sub_follower_name)
    #     db['followers'][follower_name] = sub_followers
    #
    # db['sub_followers'] = {}
    # # count sub_followers subscriptions
    # for follower, sub_followers in db['followers'].items():
    #     for sub_follower in sub_followers:
    #         # sub_follower cannot be user's own follower
    #         if not sub_follower in db['followers']:
    #             # update counter
    #             db['sub_followers'][sub_follower] = db['sub_followers'].\
    #                                                 get(sub_follower, 0) + 1
    #
    # # convert dict of sub_followers to list for html
    # followers = []
    # for sub_follower, count in db['sub_followers'].items():
    #     followers.append((sub_follower, count))

    #########

    # followers_id = api.followers_ids()
    # followers_obj = [api.get_user(follower) for follower in followers_id]
    # followers_screen = [follower.screen_name for follower in followers_obj]
    # followers = []
    # for follower in followers_screen:
    #     followers.append((follower, 1))

    return render_template('followers.html', followers=sub_followers)

@app.route("/followers/followers/json", methods=['GET'])
def json_sub_followers():
    """Return a jsonified version of the list of sub_followers"""
    sub_followers = db.get('sub_followers', {})
    return jsonify({'sub_followers': sub_followers})

@app.errorhandler(403)
def not_found(error):
    return "Failed to authorize app. Please try again."

if __name__ == '__main__':
    # encryption key for session
    app.secret_key = '3faE64iwqJDNBGC5nQ60'
    app.run(debug=True)
