"""Location string parsing and Indian city/state normalisation."""

from typing import Dict, Optional, Tuple

INDIAN_STATES: Dict[str, list] = {
    "Karnataka": ["bangalore", "bengaluru", "mysore", "mangalore", "hubli"],
    "Maharashtra": ["mumbai", "pune", "nagpur", "thane", "nashik"],
    "Delhi": ["delhi", "new delhi"],
    "Tamil Nadu": ["chennai", "coimbatore", "salem", "madurai", "trichy"],
    "Telangana": ["hyderabad", "secunderabad"],
    "West Bengal": ["kolkata", "calcutta", "siliguri"],
    "Gujarat": ["ahmedabad", "surat", "vadodara", "rajkot"],
    "Rajasthan": ["jaipur", "jodhpur", "udaipur", "kota"],
    "Uttar Pradesh": ["lucknow", "kanpur", "agra", "varanasi", "noida", "ghaziabad"],
    "Punjab": ["chandigarh", "ludhiana", "amritsar", "jalandhar"],
    "Haryana": ["gurugram", "gurgaon", "faridabad"],
    "Madhya Pradesh": ["bhopal", "indore", "jabalpur"],
    "Kerala": ["kochi", "thiruvananthapuram", "kozhikode"],
    "Andhra Pradesh": ["visakhapatnam", "vijayawada", "guntur"],
}

# Build reverse map: city_lower → state
_CITY_TO_STATE: Dict[str, str] = {
    city: state for state, cities in INDIAN_STATES.items() for city in cities
}


class LocationCleaner:
    """Parse location strings into (city, state) tuples."""

    @staticmethod
    def clean_location(
        location_raw: Optional[str],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse location string.

        Returns:
            (city, state) — either may be None.
        """
        if not location_raw:
            return None, None

        # Strip remote/hybrid qualifiers
        text = location_raw.strip()
        for kw in ("remote", "hybrid", "work from home", "wfh"):
            text = text.replace(kw, "").replace(kw.title(), "")
        text = text.strip(" ,")

        parts = [p.strip() for p in text.split(",") if p.strip()]
        if not parts:
            return None, None

        city = parts[0]
        # Try to find state from parts or reverse map
        state = None
        if len(parts) >= 2:
            candidate = parts[1]
            # Check if it's a known state
            for known_state in INDIAN_STATES:
                if known_state.lower() == candidate.lower():
                    state = known_state
                    break
            if not state:
                state = _CITY_TO_STATE.get(candidate.lower())

        if not state:
            state = _CITY_TO_STATE.get(city.lower())

        return city, state
