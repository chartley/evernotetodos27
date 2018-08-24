from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail

from ...main import get_todos
from ...utils import get_user_evernote_note

class Command(BaseCommand):
    help = 'Sends email summaries for user_pks given'

    def add_arguments(self, parser):
        parser.add_argument('user_ids', nargs='+', type=int)

        # allow --debug to print out
        parser.add_argument(
            '--debug',
            action='store_true',
            dest='debug',
            help='Debug print output instead of emailing',
        )

    def handle(self, *args, **options):
        if options['debug']:
            print '### DEBUG MODE ###'

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
                    email_body += todo.item_string + '\n'
            except Exception as e:
                import traceback
                email_body += 'Exception: %s\n%s' % (e, traceback.format_exc())


            if options['debug']:
                print email_body + '\n'
            else:
                # send email
                send_mail(
                    'Summary of #todo for user %s' % user.pk,
                    email_body,
                    'django@chrtly.com',
                    [user.email],
                    fail_silently=False,
                )
