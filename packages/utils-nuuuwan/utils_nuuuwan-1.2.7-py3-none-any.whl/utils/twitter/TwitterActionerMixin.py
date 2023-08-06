"""Implements twitter."""


from utils.Log import Log
from utils.twitter.Tweet import Tweet
from utils.twitter.TwitterActionerMixinHelpers import (
    _update_profile_description, _update_status, _upload_media)

log = Log('Twitter')


class TwitterActionerMixin:
    def send(self, tweet: Tweet):
        media_ids = _upload_media(
            self.api,
            tweet.image_file_path_list,
        )
        return _update_status(
            self.api, tweet.text, media_ids, tweet.in_reply_to_status_id
        )

    def update_profile_description(self):
        _update_profile_description(self.api)

    def update_profile_image(self, profile_image_file):
        log.debug(f'update_profile_image: {profile_image_file}')
        self.api.update_profile_image(profile_image_file)

    def update_banner_image(self, banner_image_file):
        log.debug(f'update_banner_image: {banner_image_file}')
        self.api.update_profile_banner(banner_image_file)
