"""Tests for utils."""

import unittest

from utils import Log, Tweet, Twitter

log = Log('test_twitter')

TEST_QUOTE = '\n'.join(
    [
        'Data is a precious thing',
        'and will last longer',
        'than the systems themselves.',
        '- Tim Berners-Lee',
    ]
)


SKIP_API_CREDENTIALS = 'Needs Twitter API credentials'


class TestActionerMixin(unittest.TestCase):
    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_send_tweet(self):
        twitter = Twitter.from_environ_vars()
        tweet = Tweet(
            TEST_QUOTE,
        )
        response = twitter.send(tweet)
        self.assertIsNotNone(response)

    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_send_tweet_with_media(self):
        twitter = Twitter.from_environ_vars()
        tweet = Tweet(
            TEST_QUOTE,
            ['tests/types_of_data.png'],
        )
        response = twitter.send(tweet)
        self.assertIsNotNone(response)

    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_send_tweets_in_thread(self):
        twitter = Twitter.from_environ_vars()
        previous_tweet_id = None
        for i in range(0, 4):
            tweet = Tweet(
                f'{i}/ ' + TEST_QUOTE,
                ['tests/types_of_data.png'],
                previous_tweet_id,
            )
            response = twitter.send(tweet)
            self.assertIsNotNone(response)
            previous_tweet_id = response.id
            log.debug(previous_tweet_id)

    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_update_profile_description(self):
        twitter = Twitter.from_environ_vars()
        twitter.update_profile_description()

    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_update_profile_image(self):
        twitter = Twitter.from_environ_vars()
        twitter.update_profile_image('tests/lanka_data_logo.png')

    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_update_banner_image(self):
        twitter = Twitter.from_environ_vars()
        twitter.update_banner_image('tests/banner.png')


if __name__ == '__main__':
    unittest.main()
