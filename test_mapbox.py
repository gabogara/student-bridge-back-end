from dotenv import load_dotenv
load_dotenv()

from utils.mapbox_helpers import geocode_address

coords = geocode_address("3883 Turquoise Way", "Oakland, CA 94609")
print("RESULT:", coords)