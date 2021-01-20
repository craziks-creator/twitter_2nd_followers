class AppSettings(object):

    # APP TOKENS
    CONSUMER_KEY = 'mr0UPm5hlKqbgJrbmFDQbycbs'
    CONSUMER_SECRET = ' dQFkWrwWDrdWRIuH9z9x9DqBOaKNphHDZzoXOXEXqLrqBQgHK5'

    # SESSION
    SECRET_KEY = '3faE64iwqJDNBGC5nQ60' # session encryption key

    # CALLBACK_URL
    LOCAL_CALLBACK_URL = 'http://127.0.0.1:5000/verify'
    CALLBACK_URL = 'https://fathomless-taiga-56567.herokuapp.com/verify'

settings = AppSettings()
