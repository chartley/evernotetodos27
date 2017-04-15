#!/usr/bin/env python

from xml.etree import ElementTree as ET

from evernote.api.client import EvernoteClient, NoteStore

def get_todos(auth_token):
    client = EvernoteClient(token=auth_token)
    note_store = client.get_note_store()

    # check token has basic auth by listing notes (allowed without full auth)
    try:
        notebooks = note_store.listNotebooks()
        n_notebooks = len(notebooks)
        print '[OK] Evernote API working, %s notebooks' % n_notebooks
    except Exception as e:
        print '[FAIL] Evernote API failure: %s' % e

    # search for notes which have #todo content
    # see http://dev.evernote.com/doc/articles/search.php
    notefilter = NoteStore.NoteFilter()
    notefilter.words = '#todo'
    spec = NoteStore.NotesMetadataResultSpec()
    spec.includeTitle = True
    note_list = note_store.findNotesMetadata(auth_token, notefilter, 0, 100, spec)
    print 'Search for #todo found %d notes' % note_list.totalNotes

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

        # find <li>'s with #todo text and print
        tree = ET.fromstring(note.content)
        elems = tree.findall('.//li')
        todo_elems = filter(lambda e: '#todo' in e.text, elems)
        for elem in todo_elems:
            s = '%s :: %s' % (note_search_result.title, elem.text)
            print s
            todos.append(s)

    return todos

# import sys
# dev_token = sys.argv[1]
# try:
#     get_todos(dev_token)
# except Exception as e:
#     print 'Exception: %s'
