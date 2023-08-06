
from datetime import datetime
import pandas
# Convert DMS coordinates to decimal degrees
from fmo.fmo import GPSPath


def nmea_latitude(dms, direction):
    decimal = float(dms[:2]) + float(dms[2:])/60
    if direction == 'S':
        decimal = -decimal
    return decimal

def nmea_longitude(dms, direction):
    decimal = float(dms[:3]) + float(dms[3:])/60
    if direction == 'W':
        decimal = -decimal
    return decimal

def parse_nmea_file(file) -> GPSPath:
    # https://www.gpsworld.com/what-exactly-is-gps-nmea-data/

    if not file.endswith(".csv"):
        raise Exception("Not a CSV file")
    
    # Read the CSV file into a list of dictionaries
    df = pandas.read_csv(file, dtype = str)

    # Parse the latitude and longitude fields and convert them to decimal degrees
    values = []
    for _, row in df.iterrows():
        lat = nmea_latitude(row[2], row[3])
        lng = nmea_longitude(row[4], row[5])
        timestamp = datetime.combine(datetime.today(), datetime.strptime(row[1], '%H%M%S.%f').time())
        values.append((timestamp, lat, lng))

    return GPSPath(values)