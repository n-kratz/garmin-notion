import garminconnect
from getpass import getpass
from datetime import date, timedelta
import os
from notion_client import Client

def write_text(client, PAGE_ID, text, type):
    client.blocks.children.append(
        block_id=PAGE_ID,
        children=[
            {
                "object": "block",
                "type": type,
                type: {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": text,
                        }
                    }]
                }
            }
        ]
    )

def write_row(client, database_id, date, miles, vo2max, duration, effect):
    client.pages.create(
        **{
            "parent":{
                "database_id": database_id
            },
            "properties":{
                'date': {'date': {'start': date}},
                "miles": {'number': miles},
                "vo2max": {'number': vo2max},
                "duration": {'number': duration},
                "effect": {'title': [{'text': {'content': effect}}]}
            }
        }
    )

def main():
    PG_ID = ''
    DB_ID = ''
    NOTION_TOKEN = ''

    email = getpass("Enter email address: ")
    password = getpass("Enter password: ")

    garmin = garminconnect.Garmin(email, password)
    garmin.login()

    GARTH_HOME = os.getenv("GARTH_HOME", "~/.garth")
    garmin.garth.dump(GARTH_HOME)

    today = date.today()
    today = today.isoformat()

    lastrun = garmin.get_last_activity()['splitSummaries'][0]
    stats = garmin.get_max_metrics(today)

    vo2max = stats[0]['generic']['vo2MaxPreciseValue']
    miles = round(lastrun['distance']/1609.34, 2)
    effect = garmin.get_last_activity()['trainingEffectLabel']
    duration = round(garmin.get_last_activity()['duration'], 2)

    records = garmin.get_personal_record()

    for record in records:
            if record['activityType'] == None:
                records.remove(record)

    myrecords = []
    for record in records:
            if int(record['value']//60) <= 60:
                minutes = int(record['value']//60)
                seconds = round((record['value']/60 - minutes)*60, 2)
                time_string = "{}:{}".format(minutes, seconds)
                myrecords.append(time_string)
            else:
                hours = int(record['value']//3600)
                minutes = int((record['value']/3600 - (hours % 60))*60)
                seconds = round(((record['value']/3600 - (hours % 60))*60 - minutes)*60, 2)
                time_string = "{}:{}:{}".format(hours, minutes, seconds)
                myrecords.append(time_string)

    pr1k = myrecords[0]
    pr1m = myrecords[1]
    pr5k = myrecords[2]
    pr10k = myrecords[3]
    prhalf = myrecords[4]

    text = "My 1k record: " + pr1k + "\n" + "My mile record: " + pr1m + "\n" + "My 5k record: " + pr5k + "\n" + "My 10k record: " + pr10k + "\n" + "My half marathon record: " + prhalf

    client = Client(auth=NOTION_TOKEN)
    write_row(client, DB_ID, today, miles, vo2max, duration, effect)

if __name__ == '__main__':
     main()