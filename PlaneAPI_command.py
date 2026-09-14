import argparse
import sys
from urllib.parse import quote_plus

import requests


def validate_float(name, value):
    try:
        return float(value)
    except (TypeError, ValueError):
        print(f"Invalid {name}: {value!r}. Must be a number.")
        return None


def build_area_url(lat, lon, radius):
    lat_f = validate_float("lat", lat)
    lon_f = validate_float("lon", lon)
    rad_f = validate_float("radius", radius)

    if lat_f is None or lon_f is None or rad_f is None:
        raise ValueError("Latitude, longitude, and radius must be numeric values.")

    return f"https://opendata.adsb.fi/api/v3/lat/{lat_f}/lon/{lon_f}/dist/{rad_f}"


def build_callsign_url(callsign):
    callsign = (callsign or "").strip()
    if not callsign:
        raise ValueError("Callsign cannot be empty.")
    return "https://opendata.adsb.fi/api/v2/callsign/" + quote_plus(callsign.upper())


def fetch_aircraft(url):
    try:
        response = requests.get(url, timeout=10)
    except requests.Timeout:
        print("Request timed out.")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    if response is None:
        print("No response received from API.")
        sys.exit(1)

    if not response.ok:
        print(f"API request failed with status code: {response.status_code}")
        try:
            print("Response body:", response.text)
        except Exception:
            pass
        sys.exit(1)

    try:
        data = response.json()
    except ValueError:
        print("Failed to decode JSON from the API response.")
        sys.exit(1)

    if not isinstance(data, dict):
        print("Unexpected response format from API.")
        sys.exit(1)

    return data.get("ac", [])


def print_aircraft(aircraft_list):
    if not aircraft_list:
        print("No aircraft found.")
        return

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
            f"{flight_num} | aircraft: {ac_reg} {ac_type} | altitude: {ac_alt} ft "
            f"| speed: {ac_speed} kn | heading: {ac_heading}"
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Simple ADS-B API client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    area_parser = subparsers.add_parser("area", help="List aircraft in a geographic area")
    area_parser.add_argument("--lat", required=True, type=float, help="Latitude")
    area_parser.add_argument("--lon", required=True, type=float, help="Longitude")
    area_parser.add_argument("--rad", required=True, type=float, help="Radius in nautical miles")

    callsign_parser = subparsers.add_parser("callsign", help="Search aircraft by callsign")
    callsign_parser.add_argument("callsign", help="Aircraft callsign to search")

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        if args.command == "area":
            url = build_area_url(args.lat, args.lon, args.rad)
        elif args.command == "callsign":
            url = build_callsign_url(args.callsign)
        else:
            print("Invalid command")
            sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)

    print(url)
    aircraft_list = fetch_aircraft(url)
    print_aircraft(aircraft_list)


if __name__ == "__main__":
    main()
