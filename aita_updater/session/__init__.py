from decouple import config
import pandas as pd
import praw


class Session:
    def __init__(self, subreddit):
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
        return reddit

    def get_top_posts(self, n_posts):
        """
        get n submissions from a subreddit

        """
        top_n = self.subreddit.hot(limit=n_posts)
        return top_n

    def parse_results(self, n_posts):
        """
        get wanted data from posts
        """
        rd = {'title': [],
              'upvotes': [],
              'vote': [],
              'created': [],
              'top_comment': [],
              }
        top_posts = self.get_top_posts(n_posts)
        parsed_rd = self.expand_results(rd, top_posts)
        return parsed_rd

    def expand_results(self, rd, top_posts):
        """
        expand results and grab needed
        attributes
        :return: rd
        """
        for post in top_posts:
            if not post.stickied:
                rd['title'].append(post.title)
                rd['upvotes'].append(post.ups)
                rd['created'].append(post.created)
                rd['vote'].append('NTA')
                for comment in post.comments:
                    body = comment.body
                    rd['top_comment'].append(body)
                    break
        return rd

    def convert_results(self, n_posts):
        """
        convert results to a pandas dataframe
        :param rd: dict
        :return:
        """
        results: dict = self.parse_results(n_posts)
        results_df = pd.DataFrame(results)
        return results_df
