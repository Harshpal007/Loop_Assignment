import os
from django.conf import settings
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intern_project.settings")
django.setup()
# settings.configure()




from intern_project.models import menu_hours,time_zone
from django.utils import timezone

import csv




def get_menuhours():
    print("doing menu")
    with open('Menu hours.csv','r') as data:
        table = csv.DictReader(data)

        for row in table:
            menu_hours.objects.create(
                store_id = int(row['store_id']),
                weekday =int(row['day']),
                start_time_local=row['start_time_local'],
                end_time_local=row['end_time_local']
            )
    print("menu done")

def get_timezeon():
    print("doing timezone")
    with open('bq-results-20230125-202210-1674678181880.csv','r') as data:
        table = csv.DictReader(data)

        for row in table:
            time_zone.objects.create(
                store_id = int(row['store_id']),
            timezone_str = row['timezone_str']
        )
    print("timezone done")

if __name__ == '__main__':
    # get_menuhours()
    get_timezeon()