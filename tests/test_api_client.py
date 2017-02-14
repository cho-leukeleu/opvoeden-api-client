from __future__ import unicode_literals

import unittest

import mock
import requests
import requests_mock

from opvoeden_api import client, models

from . import utils

API_KEY = 'this-is-not-a-real-api-key'


def mock_session():
    session = mock.Mock(spec=requests.Session)
    session.headers = {}
    return session


class TestAPIAuthorizationHeader(unittest.TestCase):
    def test_client_sets_header(self):
        session = mock_session()
        client.Client(API_KEY, session=session)
        self.assertEqual(API_KEY, session.headers['Authorization'])


class TestAPIClientEndpoints(unittest.TestCase):
    def setUp(self):
        self.session = mock_session()
        self.session.get = mock.Mock()
        self.client = client.Client(API_KEY, base_url='https://example.com/', session=self.session)

    def test_contentset(self):
        self.client.contentset()
        self.session.get.assert_called_once_with('https://example.com/contentset')

    def test_contentset_with_id(self):
        self.client.contentset(1)
        self.session.get.assert_called_once_with('https://example.com/contentset/1')

    def test_article(self):
        self.client.article(1)
        self.session.get.assert_called_once_with('https://example.com/article/1')

    def test_image(self):
        self.client.image(1)
        self.session.get.assert_called_once_with('https://example.com/image/1')


class TestAPIClientResponses(unittest.TestCase):
    def setUp(self):
        self.client = client.Client(API_KEY, base_url='https://example.com/')

    def test_contentset(self):
        with requests_mock.Mocker() as m:
            m.get('https://example.com/contentset', text=utils.data('contentset_list.json'))
            response = self.client.contentset()
        self.assertTrue(
            all(isinstance(obj, models.ContentSet) for obj in response),
            'Expected response objects to be ContentSet instances')

    def test_contentset_with_id(self):
        with requests_mock.Mocker() as m:
            m.get('https://example.com/contentset/1', text=utils.data('contentset_detail.json'))
            response = self.client.contentset(1)
        self.assertTrue(
            all(isinstance(obj, models.Article) for obj in response),
            'Expected response objects to be Article instances')

    def test_article(self):
        with requests_mock.Mocker() as m:
            m.get('https://example.com/article/1', text=utils.data('article.json'))
            response = self.client.article(1)
        self.assertIsInstance(response, models.Article)

    def test_image(self):
        with requests_mock.Mocker() as m:
            m.get('https://example.com/image/1', text=utils.data('image.json'))
            response = self.client.image(1)
        self.assertIsInstance(response, models.Image)
