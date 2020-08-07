import pandas as pd
from aita_updater.db import session_context, db_create_engine
from aita_models import User, Submission
from aita_updater.exceptions import NoUserError
import datetime
import logging


class RedditProcessor:

    def __init__(self, post_data):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f'{__name__} entered')
        self.unprocessed_data = post_data

    def get_user(self, db_session, user_name):
        """
        get a result from a single post
        :return:
        """
        query = db_session.query(User). \
            filter(User.username == user_name)
        query_results = query.first()
        return query_results

    def create_user(self, db_session, user_name):
        """

        :param db_session:
        :param user_name:
        :return:
        """
        user_info = {
            'username': user_name,
            'dt_updated': datetime.datetime.now()
        }
        return User(**user_info)

    def create_or_find_user(self, db_session, user_name):
        """
        create user object
        :param user_name:
        :return:
        """
        found_user: object = self.get_user(db_session, user_name)
        if not found_user:
            new_user = self.create_user(db_session, user_name)
            db_session.add(new_user)
            self.logger.debug(f'new user {new_user.username} added')
            db_session.flush()
            return new_user
        else:
            self.logger.debug(f'user {found_user} already exists in Database '
                              'not adding')
            return found_user

    def create_submission(self, post, user_id) -> Submission:
        """
        create submission object
        :param post:
        :return:
        """
        submission = {
            'created': datetime.datetime.utcfromtimestamp(post.created),
            'title': post.title,
            'user_id': user_id,
            'dt_updated': datetime.datetime.now()
        }
        return Submission(**submission)

    def find_or_add_post(self, db_session, title) -> bool:
        """
        check if post exists in database,
        if it does return the result, else,
        :return:
        """
        query = db_session.query(Submission). \
            filter(Submission.title == title)
        found_title = bool(query.first())
        return found_title

    def run(self):
        """
        run processor
        :return:
        """
        with session_context(db_create_engine()) as db_session:
            submissions = []
            for post in self.unprocessed_data:
                post_exists = self.find_or_add_post(db_session, post.title)
                if not post_exists:
                    try:
                        user = self.create_or_find_user(db_session, post.author.name)
                        submission = self.create_submission(post, user.id)
                        submissions.append(submission)
                    except AttributeError:
                        self.logger.info('No username found for post.. skipping')
            db_session.add_all(submissions)
            self.logger.debug('New submissions added to DB')
        return

