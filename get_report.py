

import pandas as pd
import os
import pytz
import csv
import random
from io import StringIO
from datetime import datetime , timedelta
from dateutil.parser import parse
from django.conf import settings
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intern_project.settings")
django.setup()
from intern_project.models import menu_hours,time_zone,Report



def generate_random_string(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))



def string_to_timestamp(timestamp):
    format_string = "%Y-%m-%d %H:%M:%S.%f %Z"

    date_obj = parse(timestamp)
    return date_obj

def local_to_utc(store_id,timestamp,current_date):
    source_timezone = time_zone.objects.filter(store_id=store_id)
    source_timezone =list(source_timezone.values_list('timezone_str'))
    # print(source_timezone[0])
    if len(source_timezone)==0:
        source_timezone = pytz.timezone('America/Chicago')
    else:
        source_timezone = pytz.timezone(str(source_timezone[0][0]))
    
    timestamp= datetime.combine(current_date,timestamp)
    local_time= source_timezone.localize(timestamp)
    
    target_timezone='UTC'

    utc_datetime = timestamp.astimezone(pytz.utc)

    return utc_datetime
    



def get_uptime_hour(store_id,csv_file):
    store_data=csv_file.loc[csv_file['store_id'] ==store_id]
    # print(store_data)
    store_data['timestamp_utc']= pd.to_datetime(store_data['timestamp_utc'])
    store_data=store_data.sort_values(by='timestamp_utc', ascending=False)
    
    current_timestamp= store_data['timestamp_utc'].iloc[0]
    # format_string = "%Y-%m-%d %H:%M:%S.%f %Z"
    # current_timestamp = string_to_timestamp(current_time_str)
    
    current_day=current_timestamp.date().weekday()

    #fotr handling edge case of multiple menu hours
    menu_hours_range=menu_hours.objects.filter(store_id=store_id,weekday=current_day)
    menu_hours_range= list(menu_hours_range.values_list('start_time_local','end_time_local'))
    uptime_minutes=0
    for range in menu_hours_range:
        start_time=local_to_utc(store_id,range[0],current_timestamp)
        end_time = local_to_utc(store_id,range[1],current_timestamp)
        if end_time.time()>=current_timestamp.time() and start_time.time()<=current_timestamp.time():
            two_hours_ago = current_timestamp -timedelta(hours=2)
            filtered_data = store_data[(store_data['timestamp_utc'] >= two_hours_ago) & (store_data['timestamp_utc'] <= current_timestamp)]
            
            filtered_data = filtered_data.sort_values(by ='timestamp_utc', ascending =False)
            if filtered_data['status'].iloc[0]=='active' and  filtered_data['status'].iloc[1]=='active':
                uptime_minutes+=60
                # print(uptime_minutes)
            elif filtered_data['status'].iloc[0]=='inactive' and  filtered_data['status'].iloc[1]=='active':
                uptime_minutes += (current_timestamp -filtered_data['timestamp_utc'].iloc[1]).total_seconds()/60

    return uptime_minutes
        
            

def get_uptime_lastday(store_id,csv_file,current_weekday=0):
    store_data= csv_file.loc[csv_file['store_id']==store_id]
    # print(store_data.iloc[1])
    store_data['timestamp_utc']= pd.to_datetime(store_data['timestamp_utc'])
    store_data = store_data.sort_values(by='timestamp_utc',ascending=False)
    current_timestamp=store_data['timestamp_utc'].iloc[0]
    # print(current_timestamp)

    #getting current weekday
    current_weekday=current_timestamp.date().weekday()
    # print(current_weekday)
    menu_hours_range = menu_hours.objects.filter(store_id=store_id,weekday=current_weekday)
    menu_hours_range = list(menu_hours_range.values_list('start_time_local','end_time_local'))
    # print(type(menu_hours_range))
    uptime_minutes=0
    total_menu_hours=0
    # store_data = store_data.sort_values(by='timestamp_utc',ascending=True)
    for ranges in menu_hours_range:
        start_time=local_to_utc(store_id,ranges[0],current_timestamp)
        end_time = local_to_utc(store_id,ranges[1],current_timestamp)
        total_menu_hours+=(end_time-start_time).total_seconds()/3600
        print(total_menu_hours)
        if(current_timestamp<=end_time):
            filtered_data = store_data[(store_data['timestamp_utc'] >= start_time) & (store_data['timestamp_utc'] <= current_timestamp)]
        else:
            filtered_data = store_data[(store_data['timestamp_utc'] >= start_time) & (store_data['timestamp_utc'] <= current_timestamp)]
        size=len(filtered_data)
        filtered_data = filtered_data.sort_values(by='timestamp_utc',ascending=True)
        temp_count=0
        # print(start_time ,"   " ,end_time)
        for i in range(size):
            if i>0 and filtered_data['status'].iloc[i]=='inactive' and filtered_data['status'].iloc[i-1]=='active':
                temp_count+=(filtered_data['timestamp_utc'].iloc[i]-filtered_data['timestamp_utc'].iloc[i-1]).total_seconds()/3600
                uptime_minutes+=temp_count
                temp_count=0
            elif i>0 and filtered_data['status'].iloc[i]=='active' and filtered_data['status'].iloc[i-1]=='active':
                # print("inside shop")
                temp_count+=(filtered_data['timestamp_utc'].iloc[i]-filtered_data['timestamp_utc'].iloc[i-1]).total_seconds()/3600
            if i==0 and filtered_data['status'].iloc[i]=='active':
                temp_count+=(filtered_data['timestamp_utc'].iloc[i-1]-start_time).total_seconds()/3600
                # print("inside shop")
            if i==size-1:
                uptime_minutes+=temp_count


    return uptime_minutes ,total_menu_hours


def get_uptime_last_week(store_id,csv_file):
    uptime_last_week=0
    store_data= csv_file.loc[csv_file['store_id']==store_id]
    
    store_data['timestamp_utc']= pd.to_datetime(store_data['timestamp_utc'])
    store_data = store_data.sort_values(by='timestamp_utc',ascending=False)
    current_timestamp=store_data['timestamp_utc'].iloc[0]
    # print(current_timestamp)
    current_date=current_timestamp.date()
    total_menu_hours=0
    #getting current weekday
    j=6
    while j>=0:
        current_day=current_timestamp.date().weekday()
        menu_hours_range = menu_hours.objects.filter(store_id=store_id,weekday=current_day)
        menu_hours_range = list(menu_hours_range.values_list('start_time_local','end_time_local'))
        for ranges in menu_hours_range:
            start_time=local_to_utc(store_id,ranges[0],current_timestamp)
            end_time = local_to_utc(store_id,ranges[1],current_timestamp)
            total_menu_hours+=(end_time-start_time).total_seconds()/3600
            if(current_timestamp<=end_time):
                filtered_data = store_data[(store_data['timestamp_utc'] >= start_time) & (store_data['timestamp_utc'] <= current_timestamp)]
            else:
                filtered_data = store_data[(store_data['timestamp_utc'] >= start_time) & (store_data['timestamp_utc'] <= current_timestamp)]
            size=len(filtered_data)
            filtered_data = filtered_data.sort_values(by='timestamp_utc',ascending=True)
            temp_count=0
        # print(start_time ,"   " ,end_time)
            for i in range(size):
                if i>0 and filtered_data['status'].iloc[i]=='inactive' and filtered_data['status'].iloc[i-1]=='active':
                    temp_count+=(filtered_data['timestamp_utc'].iloc[i]-filtered_data['timestamp_utc'].iloc[i-1]).total_seconds()/3600
                    uptime_last_week+=temp_count
                    temp_count=0
                elif i>0 and filtered_data['status'].iloc[i]=='active' and filtered_data['status'].iloc[i-1]=='active':
                # print("inside shop")
                    temp_count+=(filtered_data['timestamp_utc'].iloc[i]-filtered_data['timestamp_utc'].iloc[i-1]).total_seconds()/3600
                if i==0 and filtered_data['status'].iloc[i]=='active':
                    temp_count+=(filtered_data['timestamp_utc'].iloc[i-1]-start_time).total_seconds()/3600
                # print("inside shop")
                if i==size-1:
                    uptime_last_week+=temp_count
        j-=1
        current_timestamp=current_timestamp-timedelta(days=1)
    print(uptime_last_week)
    return uptime_last_week,total_menu_hours



def generate_report():
    file_path='store status.csv'
    csv_file = pd.read_csv(file_path)
    unique_store_id=csv_file['store_id'].unique()
    print(len(unique_store_id))
    output = StringIO()
    writer = csv.writer(output)
    i=0
    for store_id in unique_store_id:
        if i>100:
            break
        uptime_last_hour = get_uptime_hour(store_id,csv_file)
        uptime_last_day,total_menu_hours_day = get_uptime_lastday(store_id,csv_file)
        uptime_last_week,total_menu_hours_week = get_uptime_last_week(store_id,csv_file)
        downtime_last_hour = 60-uptime_last_hour
        downtime_last_day=abs(total_menu_hours_day-uptime_last_day)
        downtime_last_week=abs(total_menu_hours_week-uptime_last_week)
        row=[store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week]
        writer.writerow(row)
        i+=1
    # print(output.getvalue())
    report_csv_content = output.getvalue()
    report_file_name = f"report_{generate_random_string(8)}.csv"
    report_id = generate_random_string()
    report_file_path = os.path.join('csv_reports/', report_file_name)

    with open(report_file_path, 'w') as report_file:
        report_file.write(report_csv_content)


    new_report = Report(csv_report_file=report_file_path)
    new_report.save()

    return report_id

    




if __name__=='__main__':
    generate_report()