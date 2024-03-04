# from django.core.management.base import BaseCommand, CommandError, CommandParser

# # from campaign.backends import brevo_api

# # class Command(BaseCommand):
# #     help = "Close the specified poll for voting"
    
# #     def add_arguments(self, parser):
# #         parser.add_argument("poll_ids",nargs="+", type=int)

# #     def handle(self, *args, **options):
# #         for poll_id in options["poll_ids"]:
# #             try:
# #                 poll = brevo_api.objects.get(pk=poll_id)
# #             except brevo_api.DoesNotExist:
# #                 raise CommandError('Poll "%s" does not exits' % poll_id)
            
# #             poll.opened = False
# #             poll.save()

# #             self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
