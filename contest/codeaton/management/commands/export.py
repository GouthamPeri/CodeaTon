from codeaton.models import *
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Sends college statistics to the mail'

    def handle(self, *args, **options):
        file = open("data.csv", "w")
        reg_objects = Registration.objects.all()
        file.write("Team Name,Member 1 Name, Member 1 Phone Number, Member 1 Email ID,Member 2 Name, Member 2 Phone Number, Member 2 Email ID\n")
        for r in reg_objects:
            file.write(str(r.team_name) + "," + str(r.member_1_name) + "," + str(r.member_1_phone_no) + "," + str(r.member_1_email)
                       + "," + str(r.member_2_name) + "," + str(r.member_2_phone_no) + "," + str(r.member_2_email) + "\n")

        print "successfully dumped"