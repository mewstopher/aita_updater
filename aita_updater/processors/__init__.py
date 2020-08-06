import pandas as pd
from aita_updater.session import Session
from aita_updater.db import session_context, db_create_engine
from aita_models import User
import datetime


class RedditProcessor:

    def __init__(self, post_data):
        self.unprocessed_data = post_data

    def create_results(self) -> dict:
        """
        create results dictionary
        :return: results_dict
        """
        results_dict = {
            'title': [],
            'upvotes': [],
            'vote': [],
            'created': [],
            'top_comment': [],
        }
        return results_dict

    def create_bundle(self):
        """
        get a result from a single post
        :return:
        """

        pass

    def add_user(self):
        user_info = {
            'username': 'mu',
            'dt_updated': datetime.datetime.now()
        }
        return User(**user_info)

    def get_users(self, db_session):
        query = db_session.query(User). \
            filter(User.username == 'mu')
        query_result = query.all()
        return query_result

    def run(self):
        """
        run processor
        :return:
        """
        with session_context(db_create_engine()) as db_session:
            user = self.add_user()
            users = self.get_users(db_session)
            db_session.add(user)
        return

