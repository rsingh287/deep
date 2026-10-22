import re
import subprocess
import urllib.parse
import webbrowser

AIRPORT_IATA = {
    "BUF": "Buffalo Niagara International Airport (BUF)",
    "DEL": "Indira Gandhi International Airport, New Delhi (DEL)",
    "YYZ": "Toronto Pearson International Airport (YYZ)",
    "JFK": "John F. Kennedy International Airport, New York (JFK)",
    "LHR": "London Heathrow Airport (LHR)",
    "LAX": "Los Angeles International Airport (LAX)",
    "ORD": "Chicago O'Hare International Airport (ORD)",
    "SFO": "San Francisco International Airport (SFO)",
    "BOM": "Chhatrapati Shivaji Maharaj Airport, Mumbai (BOM)",
    "ATQ": "Sri Guru Ram Dass Jee Airport, Amritsar (ATQ)",
    "CDG": "Paris Charles de Gaulle Airport (CDG)",
    "DXB": "Dubai International Airport (DXB)",
    "SIN": "Singapore Changi Airport (SIN)",
    "SYD": "Sydney Kingsford Smith Airport (SYD)",
    "YVR": "Vancouver International Airport (YVR)",
    "YUL": "Montréal-Trudeau International Airport (YUL)",
}


def handle_travel_booking_intent(prompt: str):
    """
    Unified Autonomous Router for Air Flights, Flight Tickets, Hotels, and Car Rentals.
    """
    p_low = prompt.lower().strip()

    # -------------------------------------------------------------------------
    # 1. AIR FLIGHTS & FLIGHT TICKETS
    # -------------------------------------------------------------------------
    if any(
        k in p_low
        for k in [
            "flight",
            "flights",
            "flight ticket",
            "flight tickets",
            "airfare",
            "fly from",
            "flying to",
            "plane ticket",
            "airline ticket",
        ]
    ):
        # Extract Origin & Destination
        route_match = re.search(
            r"from\s+([a-zA-Z0-9\s]+?)\s+to\s+([a-zA-Z0-9\s]+?)(?:\s+from|\s+on|\s+between|\s+for|\s+date|$)",
            prompt,
            re.IGNORECASE,
        )
        origin = route_match.group(1).strip().upper() if route_match else "BUF"
        destination = route_match.group(2).strip().upper() if route_match else "DEL"

        # Clean destination if date clause slipped into it
        destination = re.sub(r"\s+from.*", "", destination, flags=re.IGNORECASE).strip()

        # Extract dates: from <date1> to <date2>
        dates_match = re.search(
            r"(?:from|between|\s|^)\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}\w*)\s+(?:to|and|-)\s+((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}\w*)",
            prompt,
            re.IGNORECASE,
        )

        if dates_match:
            d1 = dates_match.group(1).strip()
            d2 = dates_match.group(2).strip()
            date_str = f"from {d1} to {d2}"
        else:
            date_str = "flexible dates"

        query_str = f"flights from {origin} to {destination} {date_str}".strip()
        google_flights_url = (
            f"https://www.google.com/travel/flights?q={urllib.parse.quote(query_str)}"
        )
        kayak_url = f"https://www.kayak.com/flights/{urllib.parse.quote(origin)}-{urllib.parse.quote(destination)}"
        skyscanner_url = f"https://www.skyscanner.com/transport/flights/{urllib.parse.quote(origin)}/{urllib.parse.quote(destination)}"

        # Open in browser silently
        try:
            subprocess.Popen(
                [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    google_flights_url,
                ]
            )
        except Exception:
            webbrowser.open(google_flights_url)

        orig_desc = AIRPORT_IATA.get(origin, origin)
        dest_desc = AIRPORT_IATA.get(destination, destination)

        return (
            f"I have opened Google Flights from {orig_desc} to {dest_desc} ({date_str}) in your browser.",
            "autonomous_flight_booking_engine",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{google_flights_url}'",
                    "output": f"Opened Google Flights for {origin} -> {destination} ({date_str})",
                }
            ],
        )

    # -------------------------------------------------------------------------
    # 2. HOTEL TICKETS & ACCOMMODATIONS
    # -------------------------------------------------------------------------
    if any(
        k in p_low
        for k in [
            "hotel",
            "hotels",
            "hotel ticket",
            "hotel booking",
            "resort",
            "motel",
            "stay in",
            "room booking",
        ]
    ):
        # Extract City
        city_match = re.search(
            r"(?:hotel|hotels|in|at|for)\s+([a-zA-Z\s,]+?)(?:\s+from|\s+on|\s+between|\s+for|\s+date|$)",
            prompt,
            re.IGNORECASE,
        )
        city = city_match.group(1).strip() if city_match else "New York"
        city = re.sub(
            r"\b(hotel|hotels|tickets|ticket|booking|in|for)\b",
            "",
            city,
            flags=re.IGNORECASE,
        ).strip()
        if not city:
            city = "New York"

        dates_match = re.search(
            r"(?:from|between|\s|^)\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}\w*)\s+(?:to|and|-)\s+((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}\w*)",
            prompt,
            re.IGNORECASE,
        )
        date_str = (
            f"from {dates_match.group(1)} to {dates_match.group(2)}"
            if dates_match
            else "flexible dates"
        )

        query_str = f"hotels in {city} {date_str}".strip()
        google_hotels_url = (
            f"https://www.google.com/travel/hotels?q={urllib.parse.quote(query_str)}"
        )
        booking_url = (
            f"https://www.booking.com/searchresults.html?ss={urllib.parse.quote(city)}"
        )
        airbnb_url = f"https://www.airbnb.com/s/{urllib.parse.quote(city)}/homes"

        try:
            subprocess.Popen(
                [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    google_hotels_url,
                ]
            )
        except Exception:
            webbrowser.open(google_hotels_url)

        return (
            f"I have opened Google Hotels for '{city}' ({date_str}) in your browser.",
            "autonomous_hotel_booking_engine",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{google_hotels_url}'",
                    "output": f"Opened Google Hotels for '{city}' ({date_str})",
                }
            ],
        )

    # -------------------------------------------------------------------------
    # 3. CAR RENTALS & VEHICLE RENTALS
    # -------------------------------------------------------------------------
    if any(
        k in p_low
        for k in [
            "car rental",
            "rent a car",
            "rental car",
            "car rentals",
            "vehicle rental",
            "auto rental",
            "hertz",
            "enterprise car",
        ]
    ):
        city_match = re.search(
            r"(?:in|at|for|from)\s+([a-zA-Z\s,]+?)(?:\s+from|\s+on|\s+between|\s+for|\s+date|$)",
            prompt,
            re.IGNORECASE,
        )
        city = city_match.group(1).strip() if city_match else "Toronto"
        city = re.sub(
            r"\b(car|rental|rentals|rent)\b", "", city, flags=re.IGNORECASE
        ).strip()
        if not city:
            city = "Toronto"

        dates_match = re.search(
            r"(?:from|between|\s|^)\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}\w*)\s+(?:to|and|-)\s+((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}\w*)",
            prompt,
            re.IGNORECASE,
        )
        date_str = (
            f"from {dates_match.group(1)} to {dates_match.group(2)}"
            if dates_match
            else "flexible dates"
        )

        query_str = f"car rental in {city} {date_str}".strip()
        google_cars_url = (
            f"https://www.google.com/travel/cars?q={urllib.parse.quote(query_str)}"
        )
        kayak_cars_url = f"https://www.kayak.com/cars/{urllib.parse.quote(city)}"

        try:
            subprocess.Popen(
                [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    google_cars_url,
                ]
            )
        except Exception:
            webbrowser.open(google_cars_url)

        return (
            f"I have opened Car Rental searches for '{city}' in your browser.",
            "autonomous_car_rental_engine",
            [
                {
                    "language": "powershell",
                    "code": f"start chrome '{google_cars_url}'",
                    "output": f"Opened Car Rental Search for '{city}' ({date_str})",
                }
            ],
        )

    return None
