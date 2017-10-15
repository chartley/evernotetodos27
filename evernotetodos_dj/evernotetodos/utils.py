

def get_user_evernote_note(user):
    """ Gets a user's evernote token via django-allauth, given a django user
    """
    evernote_accts = user.socialaccount_set.filter(provider='evernote')
    if not evernote_accts.exists():
        raise Exception('No Evernote SocialAccounts linked to %s' % user.pk)
    if evernote_accts.count() > 1:
        raise Exception('>1 Evernote account for %s ' % user.pk)
    account = evernote_accts[0]

    if account.socialtoken_set.count() != 1:
        raise Exception('SocialTokens %d when 1 expected for user %s' % (account.socialtoken_set.count(), user.pk))
    socialtoken = account.socialtoken_set.all()[0]

    print 'get_user_evernote_note(%s): token: %s' % (user.pk, socialtoken.token)

    return socialtoken.token
