import requests
from rich.console import Console
from rich.table import Table


console = Console()


def input_validation_float(input_str):
    try:
        return float(input_str)
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None


def input_area_search():
    lat = input_validation_float(input("lat: ").strip())
    if lat is None:
        exit()
    lon = input_validation_float(input("lon: ").strip())
    if lon is None:
        exit()
    rad = input_validation_float(input("rad: ").strip())
    if rad is None:
        exit()
    return lat, lon, rad


def input_callsign_search():
    callsign = input("callsign: ").strip()
    if not callsign:
        print("Invalid input. Please enter a valid callsign.")
        exit()
    return callsign


def build_url(search_type, lat=None, lon=None, rad=None, callsign=None):
    if search_type == "1":
        return f"https://opendata.adsb.fi/api/v3/lat/{lat}/lon/{lon}/dist/{rad}"
    elif search_type == "2":
        return f"https://opendata.adsb.fi/api/v2/callsign/{callsign}"
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
    table = Table(title="Aircraft")
    table.add_column("Flight")
    table.add_column("Registration")
    table.add_column("Type")
    table.add_column("Altitude (ft)")
    table.add_column("Speed (kn)")
    table.add_column("Heading")

    for aircraft in aircraft_list:
        flight_num = aircraft.get("flight") or "N/A"
        if isinstance(flight_num, str):
            flight_num = flight_num.strip()

        table.add_row(
            str(flight_num),
            str(aircraft.get("r", "N/A")),
            str(aircraft.get("t", "N/A")),
            str(aircraft.get("alt_baro", "N/A")),
            str(aircraft.get("gs", "N/A")),
            str(aircraft.get("true_heading", "N/A")),
        )

    console.print(table)


if __name__ == "__main__":
    while True:
        search_type = input(
            "0. quit\n1. list aircrafts by area \n2. search flight\n"
        ).strip()

        if search_type == "1":
            lat, lon, rad = input_area_search()
            url = build_url(search_type, lat=lat, lon=lon, rad=rad)
        elif search_type == "2":
            callsign = input_callsign_search()
            url = build_url(search_type, callsign=callsign)
        elif search_type == "0":
            break
        else:
            print("Invalid search type.")
            continue

        print(url)
        aircraft_list = request_flight_data(url)
        list_aircrafts(aircraft_list)
