# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
# from evernote.api.client import EvernoteClient, NoteStore
from mock import MagicMock, Mock, patch

import main

# Create your tests here.
class EvernoteScannerTestCase(TestCase):
    note_unixtime = 1535130165000
    note_timestamp = datetime.datetime.fromtimestamp(note_unixtime/1000)

    def setUp(self):
        pass

    @patch('evernotetodos.main.EvernoteClient')
    def test_get_todos_unicode_content(self, MockEvernoteClient):
        """Test we can handle unicode note content"""
        notes = [
            TestNote(1, 'Chunqi', ['Stuff']),
            TestNote(2, 'Ravi', [u'#todo thé thing']),
            TestNote(3, 'Ren', [u'#todo weird space']),
        ]
        self.config_mock_evernoteclient(MockEvernoteClient, notes)

        todos = main.get_todos('mock_auth_token')
        expected_todos = [ \
            main.ToDo(EvernoteScannerTestCase.note_timestamp, u'Ravi :: #todo thé thing'),\
            main.ToDo(EvernoteScannerTestCase.note_timestamp, u'Ren :: #todo weird space')]
        self.assertEqual(todos, expected_todos)


    @patch('evernotetodos.main.EvernoteClient')
    def test_get_todos_unicode_title(self, MockEvernoteClient):
        """Test we can handle unicode note titles"""
        notes = [
            TestNote(1, 'Chunqi', ['Stuff']),
            TestNote(2, u'André', ['#todo thing']),
        ]
        self.config_mock_evernoteclient(MockEvernoteClient, notes)

        todos = main.get_todos('mock_auth_token')
        expected_todo = main.ToDo(EvernoteScannerTestCase.note_timestamp, u'Andr\xe9 :: #todo thing')
        self.assertEqual(todos, [expected_todo])


    @patch('evernotetodos.main.EvernoteClient')
    def test_get_todos_case_insensitive(self, MockEvernoteClient):
        """Test we can handle upper / lower case"""
        notes = [
            TestNote(1, u'Someone', [u'#ToDo thing']),
        ]
        self.config_mock_evernoteclient(MockEvernoteClient, notes)

        todos = main.get_todos('mock_auth_token')
        expected_todo = main.ToDo(EvernoteScannerTestCase.note_timestamp, u'Someone :: #ToDo thing')
        self.assertEqual(todos, [expected_todo])


    @patch('evernotetodos.main.EvernoteClient')
    def test_get_todos_internal_divs(self, MockEvernoteClient):
        """Test we can handle the <li>s conatining <divs> instead of text"""
        notes = [
            TestNote(1, u'Someone', [u'<div>#todo thing</div>']),
        ]
        self.config_mock_evernoteclient(MockEvernoteClient, notes)

        todos = main.get_todos('mock_auth_token')
        expected_todo = main.ToDo(EvernoteScannerTestCase.note_timestamp, u'Someone :: #todo thing')
        self.assertEqual(todos, [expected_todo])

    @staticmethod
    def config_mock_evernoteclient(MockEvernoteClient, notes):
        note_list = Mock()
        note_list.notes = map(lambda n: n.as_mock_search_result(), notes)

        def stub_get_note(auth_token, guid, *args):
            for note in notes:
                if note.guid == guid:
                    return Mock(content=note.content, \
                                updated=EvernoteScannerTestCase.note_unixtime)
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


# some sample output showing different formats

# older note, with XML header and no internal divs
# <?xml version="1.0" encoding="UTF-8" standalone="no"?>
# <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
# <en-note><div><div><div>Links</div><div><ul><li>1:1 Notes - <a style="color: rgb(0, 0, 238); text-decoration: underline;" href="https://fb.quip.com/D9ilAVYCYtZK">https://fb.quip.com/D9ilAVYCYtZK</a></li></ul></div><div><ul><li>Great tech-talk on BC Downranking experiment #psc</li></ul>

# one here, without XML header and with <div>s inside <li>s
# <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note><div>1:1 8/10/2018</div><ul><li><div>Has done growth and monetization</div></li><li><div>Intro to Dave, Jesse #todo</div></li></ul></en-note>
