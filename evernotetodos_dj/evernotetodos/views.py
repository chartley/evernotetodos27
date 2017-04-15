from django.shortcuts import HttpResponse

from main import get_todos

def oauth(request):
    return HttpResponse("Oauth stuff goes here")

def oauth_done(request):
    account = request.user.socialaccount_set.all()[0]
    socialtoken = account.socialtoken_set.all()[0]

    print 'token: %s' % socialtoken.token

    todos = get_todos(socialtoken.token)
    response = 'Done:\n<ul>\n'
    for todo in todos:
        response += '<li>' + todo + '</li>\n'
    response += '</ul>\n'
    return HttpResponse(response)
