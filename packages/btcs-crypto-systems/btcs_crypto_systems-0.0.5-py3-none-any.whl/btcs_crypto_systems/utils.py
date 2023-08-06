import csv
from datetime import datetime

def get_csv_writer(file_name, headers):
    now = datetime.utcnow()
    datetime_string = now.strftime("%Y%m%d_%H%M")
    data_file = open('{}_{}.csv'.format(datetime_string, file_name), 'w', newline='')
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(headers)
    return csv_writer