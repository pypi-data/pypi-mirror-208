import tweepy

from utils.Log import Log

log = Log('Twitter')


class TwitterBase:
    twtr_api_key: str
    twtr_api_secret_key: str
    twtr_access_token: str
    twtr_access_token_secret: str

    def __init__(
        self,
        twtr_api_key,
        twtr_api_secret_key,
        twtr_access_token,
        twtr_access_token_secret,
    ):
        self.twtr_api_key = twtr_api_key
        self.twtr_api_secret_key = twtr_api_secret_key
        self.twtr_access_token = twtr_access_token
        self.twtr_access_token_secret = twtr_access_token_secret

        self.api = self.init_api()

    def init_api(self):
        try:
            auth = tweepy.OAuthHandler(
                self.twtr_api_key, self.twtr_api_secret_key
            )
            log.debug('Created Twitter API auth.')
            auth.set_access_token(
                self.twtr_access_token, self.twtr_access_token_secret
            )
            log.debug('Set Twitter Access Token.')
            return tweepy.API(auth)
        except Exception as e:
            log.error(f'Twitter API Setup failed: {e}')
            return None
