#!/usr/bin/env python

import datetime
from django.conf import settings
from xml.etree import ElementTree as ET

from evernote.api.client import EvernoteClient, NoteStore

class ToDo(object):
    def __init__(self, note_update_timestamp, item_string):
        self.note_update_timestamp = note_update_timestamp
        self.item_string = item_string

    def __eq__(self, other):
        return self.note_update_timestamp == other.note_update_timestamp \
               and self.item_string == other.item_string

def get_todos(auth_token):
    client = EvernoteClient(token=auth_token, sandbox=settings.EVERNOTE_IS_SANDBOX)
    note_store = client.get_note_store()

    # check token has basic auth by listing notes (allowed without full auth)
    try:
        notebooks = note_store.listNotebooks()
        # print '[OK] Evernote API working, %s notebooks' % len(notebooks)
    except Exception as e:
        print '[FAIL] Evernote API failure: %s' % e

    # search for notes which have #todo content
    # see http://dev.evernote.com/doc/articles/search.php
    notefilter = NoteStore.NoteFilter()
    notefilter.words = '#todo'
    spec = NoteStore.NotesMetadataResultSpec()
    spec.includeTitle = True
    note_list = note_store.findNotesMetadata(auth_token, notefilter, 0, 100, spec)
    # print 'Search for #todo found %d notes' % note_list.totalNotes

    # for each note, pull the #todo lines
    todos = []
    for note_search_result in note_list.notes:
        # pull note content
        note = note_store.getNote(
            auth_token,
            note_search_result.guid,
            True,
            False,
            False,
            False,
        )
        note_updated = datetime.datetime.fromtimestamp(note.updated/1000)

        # find <li>'s with #todo text and print
        tree = ET.fromstring(note.content)
        elems = tree.findall('.//li') or []

        # can be empty as #todo search omits the # . Use .lower() to icase
        todo_elems = filter(lambda e: e.text and '#todo' in e.text.lower(), elems) or []
        for elem in todo_elems:
            title = convert_to_unicode(note_search_result.title)
            element_text = convert_to_unicode(elem.text)
            s = u'%s :: %s' % (title, element_text)
            todos.append(ToDo(note_updated, s))

    # sort in reverse chrono of update time
    return sorted(todos, key=lambda t: t.note_update_timestamp, reverse=True)

def convert_to_unicode(s):
    return s.decode('utf-8') if isinstance(s, str) else s


# import sys
# dev_token = sys.argv[1]
# try:
#     get_todos(dev_token)
# except Exception as e:
#     print 'Exception: %s' % e
#     import traceback
#     traceback.print_exc()
