from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail

from ...main import get_todos
from ...utils import get_user_evernote_note

class Command(BaseCommand):
    help = 'Sends email summaries for user_pks given'

    def add_arguments(self, parser):
        parser.add_argument('user_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        for user_id in options['user_ids']:
            # get user
            user = User.objects.get(pk=user_id)

            email_body = '#todo summary for user %s\n' % user_id
            try:
                # get user token and todos
                auth_token = get_user_evernote_note(user)
                todos = get_todos(auth_token)

                # render to email string
                for todo in todos:
                    email_body += todo + '\n'
            except Exception as e:
                email_body += 'Exception: %s' % e

            # send email
            send_mail(
                'Summary of #todo for user %s' % user.pk,
                email_body,
                'django@chrtly.com',
                [user.email],
                fail_silently=False,
            )
