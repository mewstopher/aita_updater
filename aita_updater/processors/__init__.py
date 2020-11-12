import pandas as pd
from aita_updater.db import session_context, db_create_engine
from aita_models import User,\
    Submission,\
    SubmissionContent,\
    Vote,\
    Comments
from aita_updater.exceptions import NoUserError
import datetime
import logging
from enum import Enum


class Constants(Enum):
    YTA = 'You\'re the asshole'
    NTA = 'Not the asshole'
    ESH = 'Everyone sucks here'


class RedditProcessor:

    def __init__(self, post_data):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f'{__name__} entered')
        self.unprocessed_data = post_data

    @staticmethod
    def create_vote(code: str, description: str) -> Vote:
        """
        create vote info
        :return:
        """
        info = {
            'code': code,
            'description': description,
            'dt_updated': datetime.datetime.now()
            }
        return Vote(**info)

    def get_votes(self) -> list:
        """
        get all three types of vote
        :return:
        """
        votes = []
        for i in ['NTA', 'YTA', 'ESH']:
            vote = self.create_vote(i, getattr(Constants, i).value)
            votes.append(vote)
        return votes

    @staticmethod
    def get_user(db_session, user_name) -> User:
        """
        get a result from a single post
        :return:
        """
        query = db_session.query(User). \
            filter(User.username == user_name)
        query_results = query.first()
        return query_results

    @staticmethod
    def create_user(user_name):
        """

        :param user_name:
        :return:
        """
        user_info = {
            'username': user_name,
            'dt_updated': datetime.datetime.now()
        }
        return User(**user_info)

    def create_or_find_user(self, db_session, user_name: str):
        """
        create user object
        :param user_name: reddit username
        :param db_session: database session
        :return:
        """
        found_user: User = self.get_user(db_session, user_name)
        if not found_user:
            new_user = self.create_user(user_name)
            db_session.add(new_user)
            self.logger.debug(f'new user {new_user.username} added')
            db_session.flush()
            return new_user
        else:
            self.logger.debug(f'user {found_user.username} already exists in Database '
                              'not adding')
            return found_user

    @staticmethod
    def create_submission(post, user_id) -> Submission:
        """
        create submission object
        :param post: a single reddit submission/post
        :param user_id: id of a user from user table
        :return: Submission: Submission object
        """
        submission = {
            'created': datetime.datetime.utcfromtimestamp(post.created),
            'title': post.title,
            'user_id': user_id,
            'dt_updated': datetime.datetime.now()
        }
        return Submission(**submission)

    @staticmethod
    def find_or_add_post(db_session, title) -> bool:
        """
        check if post exists in database,
        if it does return the result, else,
        :return: found_title
                bool
        """
        query = db_session.query(Submission). \
            filter(Submission.title == title)
        found_title = bool(query.first())
        return found_title

    @staticmethod
    def create_submission_content(post, submission_id):
        """
        :param submission_id:
        :param post:
        :return:
        """
        info = {
            'submission_id': submission_id,
            'body': post.selftext,
            'vote_id': 1,
            'upvotes': post.ups,
            'dt_updated': datetime.datetime.now()
        }
        return SubmissionContent(**info)

    def create_comment(self, comment, user_id: int, submission_id: int) -> Comments:
        """

        :param comment:
        :param user_id:
        :return:
        """
        info = {
            'time_submitted': datetime.datetime.utcfromtimestamp(comment.created),
            'comment_upvotes': comment.ups,
            'user_id': user_id,
            'submission_id': submission_id,
            'dt_updated': datetime.datetime.now()
        }
        return Comments(**info)

    def select_comment(self, submission_id, post):
        """
        Select a top comment with one of
        the votes selected

        :return:
        """
        for comment in post.comments:
            for i in ['NTA', 'YTA', 'ESH']:
                if i in comment.body:
                    return comment
        else:
            return None

    def get_comments(self, db_session, submission_id, post):
        selected_comment = self.select_comment(submission_id, post)
        comment_user = self.create_or_find_user(db_session,
                                                selected_comment.author.name)
        new_comment = self.create_comment(selected_comment,
                                          comment_user.id,
                                          submission_id)
        return new_comment

    def run(self):
        """
        run processor. Adds entries to DB
        :return:
        """
        with session_context(db_create_engine()) as db_session:
            submission_contents = []
            votes = self.get_votes()
            db_session.add_all(votes)
            db_session.flush()
            for post in self.unprocessed_data:
                post_exists = self.find_or_add_post(db_session, post.title)
                if not post_exists:
                    try:
                        user = self.create_or_find_user(db_session, post.author.name)
                        submission = self.create_submission(post, user.id)
                        self.logger.debug(f'Adding post: {post.title}')
                        db_session.add(submission)
                        db_session.flush()
                        submission_content = self.create_submission_content(post, submission.id)
                        submission_contents.append(submission_content)
                        comment = self.get_comments(db_session, submission.id, post)
                        db_session.add(comment)
                        db_session.flush()

                    except AttributeError:
                        self.logger.info(f'No username found for post {post.title} '
                                         '.. skipping')
            db_session.add_all(submission_contents)

            self.logger.debug(f'{len(submission_contents)} New submissions added to DB')
        return
