# Twitter 2nd degree followers

A simple web app that uses the Twitter API and is Heroku-deployable. You can authorize the app access to your Twitter account through OAuth and it will display a list of your 2nd degree followers (i.e. the followers of your followers).

## Heroku

The app is deployed to Heroku and can be found [here](https://fathomless-taiga-56567.herokuapp.com/).

## Setup

To run the app locally, you'll need to setup your environment.

* Install Python 2.7, virtualenv and git
* Run the commands below,
```sh
$ chmod u+x setup.sh
$ ./setup.sh
```

## Running locally

To run locally you'll need to activate the virtualenv.
```sh
$ source env/bin/activate
$ ./manage.py local
```
Open [http://localhost:5000/](http://127.0.0.1:5000/) on your web browser to run the client.
NOTE: This won't work without the app tokens which are not released publicly.

## Dealing with Twitter's API rate limit

The Twitter API limits GET requests of followers per user to 15 requests every 15 minutes. But, we need to make N+1 separate calls to the API, where N is the numbers of followers the user has, in order to compute the list of 2nd degree followers. We can expect Twitter to limit our calls to their API N/15 times, making the user wait 15 minutes every time.

At the moment the code does not overcome the rate limit intelligently. What it does is the following: If the app experiences a rate limit, it will pause the requests for periods of 15 min and then try a new request to the API.

Further, the code section to convert users_ids to screen_names has be commented out since it would require even further calls to the API and thus experience even further limits and wait time.
