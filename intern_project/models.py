from django.db import models

class menu_hours(models.Model):
    store_id=models.BigIntegerField()
    weekday=models.PositiveIntegerField()
    start_time_local=models.TimeField()
    end_time_local=models.TimeField()


class time_zone(models.Model):
    store_id=models.BigIntegerField(primary_key=True)
    timezone_str=models.CharField(max_length=100)