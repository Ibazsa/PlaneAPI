import requests


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
        response.raise_for_status()  # Raise an error for bad responses
        return response.json().get("ac", [])
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def list_aircrafts(aircraft_list):
    for aircraft in aircraft_list:
        flight_num = aircraft.get("flight") or "N/A"
        if isinstance(flight_num, str):
            flight_num = flight_num.strip()
        ac_reg = aircraft.get("r", "N/A")
        ac_type = aircraft.get("t", "N/A")
        ac_alt = aircraft.get("alt_baro", "N/A")
        ac_speed = aircraft.get("gs", "N/A")
        ac_heading = aircraft.get("true_heading", "N/A")
        print(
            f"{flight_num} | aircraft: {ac_reg} {ac_type} | altitude: {ac_alt} ft  speed: {ac_speed} kn  heading: {ac_heading}")


search_type = input("1. list aircrafts by area \n2. search flight\n").strip()
url=""  #to shut up the warning

if search_type == "1":
    lat, lon, rad = input_area_search()
    url = build_url(search_type, lat=lat, lon=lon, rad=rad)
elif search_type == "2":
    callsign = input_callsign_search()
    url = build_url(search_type, callsign=callsign)
else:
    print("Invalid search type.")
    exit()

aircraft_list = request_flight_data(url)
list_aircrafts(aircraft_list)
print(url)
