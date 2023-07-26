

import pandas as pd
import os
import pytz
from datetime import datetime , timedelta
from django.conf import settings
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intern_project.settings")
django.setup()
from intern_project.models import menu_hours,time_zone


def string_to_timestamp(timestamp):
    format_string = "%Y-%m-%d %H:%M:%S.%f %Z"
    date_obj = datetime.strptime(timestamp, format_string)
    return date_obj

def local_to_utc(store_id,timestamp,current_date):
    source_timezone = time_zone.objects.filter(store_id=store_id)
    source_timezone =list(source_timezone.values_list('timezone_str'))
    print(source_timezone[0])
    if len(source_timezone)==0:
        source_timezone = pytz.timezone('America/Chicago')
    else:
        source_timezone = pytz.timezone(str(source_timezone[0][0]))
    
    timestamp= datetime.combine(current_date,timestamp)
    local_time= source_timezone.localize(timestamp)
    
    target_timezone='UTC'

    utc_datetime = timestamp.astimezone(pytz.utc)

    return utc_datetime
    



def get_uptime_hour(store_id,csv):
    store_data=csv.loc[csv['store_id'] ==store_id]
    # print(store_data)
    store_data=store_data.sort_values(by='timestamp_utc', ascending=False)
    store_data['timestamp_utc']= pd.to_datetime(store_data['timestamp_utc'])
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
                print(uptime_minutes)
            elif filtered_data['status'].iloc[0]=='inactive' and  filtered_data['status'].iloc[1]=='active':
                uptime_minutes += (current_timestamp -filtered_data['timestamp_utc'].iloc[1]).total_seconds/60

    return uptime_minutes
        
            

def get_uptime_lastday(store_id,csv):
    store_data= csv.loc[csv['store_id']==store_id]
    # print(store_data.iloc[1])




def generate_report():
    file_path='store status.csv'
    csv = pd.read_csv(file_path)
    unique_store_id=csv['store_id'].unique()

    for store_id in unique_store_id:
        # get_uptime_hour(store_id,csv)
        get_uptime_lastday(store_id,csv)


if __name__=='__main__':
    generate_report()