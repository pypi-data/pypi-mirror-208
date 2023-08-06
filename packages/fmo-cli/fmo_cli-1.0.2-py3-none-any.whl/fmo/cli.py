

import os
import click
from dotenv import load_dotenv

from .nmea import parse_nmea_file
from .fmo import FMO, login_to_get_token, FMO_API_URL

load_dotenv()


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
    try:
        token = login_to_get_token(url, farm, user, password)
    except Exception as ex:
        click.echo(f"Authentication failed: {ex}")
        return

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