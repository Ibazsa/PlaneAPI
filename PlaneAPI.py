import requests



search_type = input("1. list aircrafts by area \n2. search flight\n").strip()

if search_type == "1":
    lat = input("lat: ").strip()
    lon = input("lon: ").strip()
    rad = input("radius: ").strip()

    url = f"https://opendata.adsb.fi/api/v3/lat/{lat}/lon/{lon}/dist/{rad}"

elif search_type == "2":
    callsign = input("callsign:").strip()

    url = "https://opendata.adsb.fi/api/v2/callsign/" + callsign


print(url)
response = requests.get(url, timeout=10)
aircraft_list = response.json().get("ac", [])
for aircraft in aircraft_list:
    flight_num = aircraft.get("flight") or "N/A"
    if isinstance(flight_num, str):
        flight_num = flight_num.strip()
    ac_reg = aircraft.get("r", "N/A")
    ac_type = aircraft.get("t", "N/A")
    ac_alt = aircraft.get("alt_baro", "N/A")
    ac_speed = aircraft.get("gs", "N/A")
    ac_heading = aircraft.get("true_heading", "N/A")
    print(f"{flight_num} | aircraft: {ac_reg} {ac_type} | altitude: {ac_alt} ft  speed: {ac_speed} kn  heading: {ac_heading}")
