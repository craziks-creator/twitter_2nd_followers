#!env/bin/python
import sys
import tweepy
from app_conf import settings
from time import sleep
from flask import Flask, request, session, render_template,\
                  redirect, jsonify, abort

# CONFIG
CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
if len(sys.argv) == 2 and sys.argv[1] == 'local':
    CALLBACK_URL = settings.LOCAL_CALLBACK_URL
else:
    CALLBACK_URL = settings.CALLBACK_URL
db = dict() # user tokens could be stored in a database

# UTILS
def limit_handled(cursor):
    """Handle API rate limit by waiting 15 minutes and continue process"""
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print ('Rate Limit reached. Waiting 15 min.') 
            sleep(15 * 60)

def get_followers(user_id):
    """Get a list of followers from API and handle tweepy errors"""
    while True:
        try:
            api = db['api']
            return api.followers_ids(user_id)
        except tweepy.TweepError:
            print ('Error! Failed to get list of sub_followers.') 
            return []
        except tweepy.RateLimitError:
            print ('Rate Limit reached. Waiting 15 min.') 
            sleep(15 * 60)
        except KeyError:
            print ('Error! No API object found.') 
            abort(403)

def get_screen_name(user_id):
    """Get the screen name of user given their user_id"""
    while True:
        try:
            api = db['api']
            user =  api.get_user(user_id)
            return user.screen_name
        except tweepy.TweepError:
            print ('Error! Failed to get screen_name of follower.') 
            return ''
        except tweepy.RateLimitError:
            print ('Rate Limit reached. Waiting 15 min.') 
            sleep(15 * 60)
        except KeyError:
            print ('Error! No API object found.') 
            abort(403)

# FLASK APP
app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

@app.route("/")
def index():
    """Main page of app"""
    return render_template('index.html')

@app.route("/authorize")
def authorize():
    """Send request token to Twitter's API for app authorization"""
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET,
                               CALLBACK_URL)

    try:
        # twitter's authentication url
    	redirect_url = auth.get_authorization_url()
        # set the request token
    	session['request_token'] = auth.request_token
    except tweepy.TweepError:
    	print ('Error! Failed to get request token') 

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
    	print ('Error! Failed to get access token.') 

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
        print ('Error! No API object found.') 
        abort(403)

    # build tree of followers and sub_followers
    db['followers'] = {}
    followers = limit_handled(tweepy.Cursor(api.followers_ids).items())
    for follower in followers:
        sub_followers = get_followers(follower)
        db['followers'][follower] = sub_followers

    # count sub_followers subscriptions
    db['sub_followers'] = {}
    for follower, sub_followers in db['followers'].items():
        for sub_follower in sub_followers:
            # sub_follower cannot be user's own follower
            if not sub_follower in db['followers']:
                # update counter
                db['sub_followers'][sub_follower] = db['sub_followers'].\
                                                    get(sub_follower, 0) + 1

    # obtain screen names for user ids
    # comment out because it would take too long to run given the rate limit
    # for sub_follower, count in db['sub_followers'].copy().items():
    #     screen_name = get_screen_name(sub_follower)
    #     del db['sub_followers'][sub_follower]
    #     db['sub_followers'][screen_name] = count

    # convert dict of sub_followers to list for html template
    sub_followers = []
    for sub_follower, count in db['sub_followers'].items():
        sub_followers.append((sub_follower, count))

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
    app.run(debug=True)
