

import os
from datetime import datetime
import click
import pandas
from dotenv import load_dotenv

from .fmo import FMO, GPSPath, login_to_get_token, FMO_API_URL

load_dotenv()

# Convert DMS coordinates to decimal degrees
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


@click.group()
def cli():
    pass

@cli.command()
@click.argument('file')
def nmea(file):
    click.echo(file)
    if not file.endswith(".csv"):
        click.echo("Expecting a CSV file")
        return

    df = parse_nmea_file(file)
    print(df)

@cli.command()
@click.option("--url", prompt=True, default=FMO_API_URL)
@click.option("--farm", prompt=True, default="demo")
@click.option("--user", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def authenticate(url, farm, user, password):
    token = login_to_get_token(farm, user, password)

    # Write the token to the .env file
    with open(".env", "w") as f:
        f.write(f"FMO_TOKEN={token}\n")
        f.write(f"FMO_API_URL={url}\n")

    click.echo("Authentication successful. Token written to .env file.")
    click.echo("The token is a secret. Do not share it or commit it to git.")

@cli.command()
@click.option('--format', default="CSV", help="What format is the file? NMEA, CSV, GEOJSON")
@click.argument('file')
def upload_path(file, format):

    fmo_token = os.getenv("FMO_TOKEN")
    fmo_url = os.getenv("FMO_API_URL", FMO_API_URL)

    fmo = FMO(fmo_token, fmo_url)

    if format.lower() == "nmea":
        path = parse_nmea_file(file)
        df = path.dataframe()
        print(df)
        fmo.upload_path(path)
        return

    click.echo(f"Unexpected format: {format}")
    

if __name__ == '__main__':
    cli()