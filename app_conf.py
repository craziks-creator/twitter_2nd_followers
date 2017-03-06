class AppSettings(object):

    # APP TOKENS
    CONSUMER_KEY = 'pZae9lin4TMTp2FExsCgRAbsi'
    CONSUMER_SECRET = '9pJFXTsOx9SpQm2Ecb5uWBT8sucka56B3BFUn7NPnS80ux5RoD'

    # SESSION
    SECRET_KEY = '3faE64iwqJDNBGC5nQ60' # session encryption key

    # CALLBACK_URL
    LOCAL_CALLBACK_URL = 'http://127.0.0.1:5000/verify'
    CALLBACK_URL = 'https://fathomless-taiga-56567.herokuapp.com/verify'

settings = AppSettings()
