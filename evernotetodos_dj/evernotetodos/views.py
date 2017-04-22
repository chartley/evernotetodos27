from django.shortcuts import HttpResponse

from main import get_todos
from utils import get_user_evernote_note

def oauth(request):
    return HttpResponse("Oauth stuff goes here")

def profile(request):
    auth_token = get_user_evernote_note(request.user)

    todos = get_todos(auth_token)

    response = 'Done:\n<ul>\n'
    for todo in todos:
        response += '<li>' + todo + '</li>\n'
    response += '</ul>\n'
    return HttpResponse(response)
