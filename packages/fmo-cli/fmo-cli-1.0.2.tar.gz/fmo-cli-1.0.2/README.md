# FindMyOyster Command Line Interface

This CLI tool allows you to interact with the [FindMyOyster](https://findmyoyster.com) backend to upload or access data. You can also use it as a library in your own scripts.

## Installation

```
pip install fmo-cli
```

## Authenticate 

Before making any requests to the API you must authenticate. Requests are authenticated using a token.

To get a token to must use the `authenticate` command.

```
fmo authenticate
```
The command will ask for 4 values
- URL: Where is the FMO server? The default value is most likely OK
- Farm: FMO isolates all data per farm. Before doing anything you need to know what farm you are working with. For experiments you can probably use the "demo" farm, which is basically open to anyone.
- Username: The username you would use in the app
- Password: The password you would use in the app

If authentication is successful, then a token will be saved in a `.env` file. FMO will look for the token there for all subsequent request. 

If you already have a token, you are welcome to create the file by hand and skip the authentication step. The file should look like this:
```
FMO_TOKEN=<my-token>
FMO_API_URL=https://api.findmyoyster.com/v1
```

## Upload a GPS path

GPS path are one of the primary types of data we deal with. Here how you might upload a path from a CSV file

```
fmo upload-path --format nmea ./my-data.csv
```

You would like support for GPS data in a particular format, please let me know.

The example above is based on the NMEA format https://www.gpsworld.com/what-exactly-is-gps-nmea-data/