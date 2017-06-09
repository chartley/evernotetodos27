# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
# from evernote.api.client import EvernoteClient, NoteStore
from mock import MagicMock, Mock, patch

import main

# Create your tests here.
class EvernoteScannerTestCase(TestCase):
    def setUp(self):
        pass

    @patch('evernotetodos.main.EvernoteClient')
    def test_get_todos_unicode_content(self, MockEvernoteClient):
        """Test we can handle unicode note titles"""
        notes = [
            TestNote(1, 'Chunqi', ['Stuff']),
            TestNote(2, 'Ravi', [u'#todo thé thing']),
            TestNote(3, 'Ren', [u'#todo weird space']),
        ]
        self.config_mock_evernoteclient(MockEvernoteClient, notes)


        todos = main.get_todos('mock_auth_token')
        self.assertEqual(todos, [u'Ravi :: #todo thé thing', u'Ren :: #todo weird space'])

    @patch('evernotetodos.main.EvernoteClient')
    def test_get_todos_unicode_title(self, MockEvernoteClient):
        """Test we can handle unicode note titles"""
        notes = [
            TestNote(1, 'Chunqi', ['Stuff']),
            TestNote(2, u'André', ['#todo thing']),
        ]
        self.config_mock_evernoteclient(MockEvernoteClient, notes)


        todos = main.get_todos('mock_auth_token')
        self.assertEqual(todos, [u'Andr\xe9 :: #todo thing'])

    @patch('evernotetodos.main.EvernoteClient')
    def test_get_todos_case_insensitive(self, MockEvernoteClient):
        """Test we can handle upper / lower case"""
        notes = [
            TestNote(1, u'Someone', [u'#ToDo thing']),
        ]
        self.config_mock_evernoteclient(MockEvernoteClient, notes)


        todos = main.get_todos('mock_auth_token')
        self.assertEqual(todos, [u'Someone :: #ToDo thing'])

    @staticmethod
    def config_mock_evernoteclient(MockEvernoteClient, notes):
        note_list = Mock()
        note_list.notes = map(lambda n: n.as_mock_search_result(), notes)

        def stub_get_note(auth_token, guid, *args):
            for note in notes:
                if note.guid == guid:
                    return Mock(content=note.content)
            return None

        note_store = Mock()
        note_store.listNotebooks = Mock(return_value=['n1'])
        note_store.getNote = Mock(side_effect=stub_get_note)

        note_list.totalNotes = len(note_list.notes)
        note_store.findNotesMetadata = Mock(return_value=note_list)
        client = MockEvernoteClient()
        client.get_note_store = Mock(return_value=note_store)


class TestNote(object):
    def __init__(self, guid, title, items):
        self.guid = guid
        self.title = title
        content = map(lambda item: '<li>' + item + '</li>', items)
        self.content = '<xml>' + ','.join(content) + '</xml>'

    def as_mock_search_result(self):
        spec = {
            'guid': self.guid,
            'title': self.title,
        }
        return Mock(**spec)
