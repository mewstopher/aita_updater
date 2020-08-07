from decouple import config
import pandas as pd
import logging
import praw


class Session:
    def __init__(self, subreddit):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f'{__name__} entered')
        self.reddit = self.authenticate()
        self.subreddit = self.reddit.subreddit(subreddit)

    def authenticate(self):
        """
        authenticate using env vars
        :return:
        """
        reddit = praw.Reddit(user_agent=config("USER_AGENT"),
                             client_id=config("CLIENT_ID"),
                             client_secret=config("CLIENT_SECRET"),
                             username=config("USERNAME"),
                             password=config("PASSWORD")
                             )
        self.logger.debug('Using .ENV to authenticate Reddit!')
        return reddit

    def get_posts(self, n_posts: int, sort_by: str):
        """
        pull posts from reddit
        :return:
        """
        post_retriever = getattr(self.subreddit, sort_by)
        top_posts = post_retriever(limit=n_posts)
        self.logger.debug(f'{n_posts} posts retrieved from the subreddit: '
                          f'{self.subreddit}')
        return top_posts
