from utils import Log

log = Log('Tweet')


class Tweet:
    def __init__(
        self, text, image_file_path_list=None, in_reply_to_status_id=None
    ):
        self.text = text
        self.image_file_path_list = image_file_path_list or []
        self.in_reply_to_status_id = in_reply_to_status_id
