from utils.twitter.TwitterActionerMixin import TwitterActionerMixin
from utils.twitter.TwitterBase import TwitterBase
from utils.twitter.TwitterLoaderMixin import TwitterLoaderMixin


class Twitter(TwitterBase, TwitterLoaderMixin, TwitterActionerMixin):
    pass
