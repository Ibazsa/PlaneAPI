import requests
from rich.console import Console
from rich.table import Table
from rich.text import Text


console = Console()
SEARCH_TYPES = {
    "1" : "area_search",
    "2" : "callsign",
    "3" : "registration"

}
#for area search:
def determine_location_type(location):
    parts = [part.strip() for part in location.split(",")]
    if len(parts) != 2:
        parts = location.split()

    if len(parts) == 2:
        try:
            float(parts[0])
            float(parts[1])
            return "coord"
        except ValueError:
            pass

    if len(location) == 3 and location.isalpha():
        return "airport_code"

    return "city"

def input_area_search():
    loc = input("input coordinates, airport code, or city\n")
    locType=determine_location_type(loc)

    if locType == "coord":
        coordLoc = loc.split()
        lat =coordLoc[0]
        lon = coordLoc[1]
        rad = input("search radius: ")

        return lat, lon, rad
    elif locType == "airport_code":
        response = requests.get(
            f"https://airportsapi.com/api/airports/{loc.upper()}",
            timeout=10,
        )
        response.raise_for_status()
        airport_data = response.json()["data"]["attributes"]
        lat = airport_data["latitude"]
        lon = airport_data["longitude"]
        rad = input("search radius: ")
        return lat, lon, rad
    else:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{loc}", "format": "json", "limit": 1},
            headers={"User-Agent": "PlaneAPI-project"},
            timeout=10,
        )
        results = response.json()
        lat, lon = results[0]["lat"], results[0]["lon"]
        rad = input("search radius: ")
        return lat, lon, rad



def build_url(search_type, lat=None, lon=None, rad=None, callsign=None, registration=None):
    if search_type == "area_search":
        return f"https://opendata.adsb.fi/api/v3/lat/{lat}/lon/{lon}/dist/{rad}"
    elif search_type == "callsign":
        return f"https://opendata.adsb.fi/api/v2/callsign/{callsign}"
    elif search_type == "registration":
        return f"https://opendata.adsb.fi/api/v2/registration/{registration}"
    else:
        raise ValueError("Invalid search type")


def request_flight_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("ac", [])
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


def list_aircrafts(aircraft_list):
    table = Table(title="Aircraft")         #create rows for the table
    table.add_column("Flight")
    table.add_column("Registration")
    table.add_column("Type")
    table.add_column("Altitude (ft)")
    table.add_column("Speed (kn)")
    table.add_column("Heading")
    table.add_column("Squawk")

    for aircraft in aircraft_list:      #loop through the aircraft list
        flight_num = aircraft.get("flight") or "N/A"
        if isinstance(flight_num, str):
            flight_num = flight_num.strip()

        squawk = str(aircraft.get("squawk") or "N/A").strip()

        if squawk == "7500" or squawk == "7600" or squawk == "7700":
            squawk.stylize("bold red")


        table.add_row(                  #add the rows to the table
            str(flight_num),
            str(aircraft.get("r", "N/A")),
            str(aircraft.get("t", "N/A")),
            str(aircraft.get("alt_baro", "N/A")),
            str(aircraft.get("gs", "N/A")),
            str(aircraft.get("true_heading", "N/A")),
            squawk

        )

    console.print(table)


if __name__ == "__main__":

    while True:
        search_type_inp= input(
            "0. quit\n1. list aircrafts by area \n2. search by callsign\n3. search aircraft by registration number\n"
        ).strip()
        search_type = SEARCH_TYPES.get(search_type_inp)
        if search_type == "area_search":
            lat, lon, rad = input_area_search()
            url = build_url(search_type, lat=lat, lon=lon, rad=rad)
        elif search_type == "callsign":
            callsign = input("enter callsign:\n")
            url = build_url(search_type, callsign=callsign)
        elif search_type=="registration":
            reg_num = input("enter aircraft registration number:\n")
            url = build_url(search_type, registration=reg_num)

        elif search_type_inp == "0":
            break
        else:
            print("Invalid search type.")
            continue

        print(url)
        aircraft_list = request_flight_data(url)
        list_aircrafts(aircraft_list)
