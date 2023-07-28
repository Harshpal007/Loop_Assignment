from django.db import models

class menu_hours(models.Model):
    store_id=models.BigIntegerField(unique=False)
    weekday=models.PositiveIntegerField()
    start_time_local=models.TimeField()
    end_time_local=models.TimeField()


class time_zone(models.Model):
    store_id=models.BigIntegerField(primary_key=True)
    timezone_str=models.CharField(max_length=100)

class Report(models.Model):
    report_id = models.PositiveIntegerField(unique=True)
    status = models.CharField(max_length=20, choices=(("Running", "Running"), ("Complete", "Complete")))
    csv_file = models.FileField(upload_to="completed_reports/", null=False, blank=True)