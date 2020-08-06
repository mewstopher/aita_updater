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
        self.results_dict = self.create_results()

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
        logging.debug('Successfully authenticated Reddit!')
        return reddit

    def create_results(self):
        """
        get wanted data from posts
        """
        results_dict = {'title': [],
              'upvotes': [],
              'vote': [],
              'created': [],
              'top_comment': [],
              }
        return results_dict

    def get_posts(self, n_posts: int):
        """
        pull posts from reddit
        :return:
        """
        top_posts = self.subreddit.hot(limit=n_posts)
        self.logger.debug(f'{n_posts} retrieved from the subreddit: '
                          f'{self.subreddit}')
        return top_posts

    def update_results(self, top_posts):
        """
        expand results and grab needed
        attributes
        :return: results_dict
        """
        results_dict = self.results_dict
        for post in top_posts:
            if not post.stickied:
                results_dict['title'].append(post.title)
                results_dict['upvotes'].append(post.ups)
                results_dict['created'].append(post.created)

                top_comment = self.get_top_comment(post.comments)
                results_dict['top_comment'].append(top_comment['body'])
                results_dict['vote'].append(top_comment['vote'])
        return results_dict

    def get_top_comment(self, comments) -> dict:
        """
        get top comment from post comments
        attach vote to comment if fount
        :return:
        """
        i = 0
        while i < len(comments):
            comment_dict = {}
            comment = comments[i]
            if not comment.stickied:
                comment_vote = self.extract_vote(comment.body)
                if len(comment_vote) == 1:
                    comment_dict['body'] = comment.body
                    comment_dict['vote'] = comment_vote
                    return comment_dict
            i += 1
        return

    def extract_vote(self, comment) -> list:
        """
        extract NTA, ESH, YTA from
        top comment
        :return:
        #TODO: make this method more robust
        """
        vote = []
        if 'NTA' in comment:
            vote.append('NTA')
        if 'ESH' in comment:
            vote.append('ESH')
        if 'YTA' in comment:
            vote.append('YTA')

        return vote

    def convert_results(self):
        """
        convert results to a pandas dataframe
        :return:
        """
        results_df = pd.DataFrame(self.results_dict)
        return results_df
