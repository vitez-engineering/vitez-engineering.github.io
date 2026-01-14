import os
import json
import time
import calendar
from PIL import Image, ImageOps, ExifTags
from geopy.geocoders import Nominatim
import requests
    
# --- SETTINGS ---
SOURCE_DIR = "/home/cvitez/Downloads/art-webp/artistic-1-001 (1)/artistic"
OUTPUT_DIR = os.path.join(SOURCE_DIR, "web_assets") # Best to put renamed files in a subfolder
QUALITY = 85
MAX_SIZE = (2500, 2500) 


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_decimal_from_dms(dms, ref):
    if not dms or len(dms) < 3: return None
    try:
        degrees = float(dms[0])
        minutes = float(dms[1]) / 60.0
        seconds = float(dms[2]) / 3600.0
        val = degrees + minutes + seconds
        return -val if ref in ['S', 'W'] else val
    except:
        return None



# Use a very specific user agent to avoid being lumped in with generic traffic
YOUR_EMAIL = "corythedog007@gmail.com" 

geolocator = Nominatim(
    user_agent="Vitez_Photography_Archive_Script_v26",
    timeout=10
)


import requests


import requests

def get_location_details(lat, long, debug=True):
    """
    Get detailed location information from coordinates.
    Returns format: "PLACE, STATE/PROVINCE, COUNTRY"
    
    Args:
        lat: Latitude
        long: Longitude
        debug: If True, print debug information
    """
    
    # Try Overpass API to find protected areas, parks, etc.
    overpass_urls = ["https://lz4.overpass-api.de/api/interpreter", "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"]
    
    # Query for protected areas within 10km (broader search)
    overpass_query = f"""
    [out:json][timeout:30];
    is_in({lat},{long})->.a;
    (

      way(pivot.a)["boundary"~"protected_area|national_park"];
      rel(pivot.a)["boundary"~"protected_area|national_park"];
      
      way(pivot.a)["leisure"~"nature_reserve|park"]["name"];
      rel(pivot.a)["leisure"~"nature_reserve|park"]["name"];
      
      way(pivot.a)["boundary"="administrative"]["admin_level"~"8"];
      rel(pivot.a)["boundary"="administrative"]["admin_level"~"8"];
    );
    out tags;
    """
    #      way["boundary"="protected_area"](around:100,{lat},{long});
    #     way["boundary"="national_park"](around:100,{lat},{long});
    #           way["leisure"="nature_reserve"](around:100,{lat},{long});
    #      way["leisure"="park"]["name"](around:100,{lat},{long});
    
    protected_area_name = None
    time.sleep(2)
    try:
        for i in range(3):
            response = requests.post(overpass_urls[i], data={'data': overpass_query}, timeout=30)
            if response.status_code == 200:
                break
            else:
                time.sleep(2)
                print(response.status_code)
                
        print(response)
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            
            if debug:
                print(f"Overpass returned {len(elements)} total elements")
            
            # Prioritize by feature importance
            priority_keywords = [
                ['national lakeshore', 'national seashore'],
                ['national park', 'national monument'],
                ['national forest', 'wilderness'],
                ['state park'],
                ['state forest', 'state recreation']
            ]
            
            candidates = []
            for element in elements:
                tags = element.get('tags', {})
                name = tags.get('name', '')
                
                if name:
                    # Clean up the name - remove unit designations and extra info
                    clean_name = name
                    # Remove parenthetical suffixes like (Federal Unit), (North Unit), etc.
                    if '(' in clean_name:
                        clean_name = clean_name.split('(')[0].strip()
                    # Remove dash suffixes like "- Shingleton Unit"
                    if ' - ' in clean_name:
                        clean_name = clean_name.split(' - ')[0].strip()
                    
                    # Skip generic names
                    if clean_name.lower() in ['park', 'forest', 'recreation area']:
                        continue
                    
                    # Determine priority level
                    priority = 99
                    name_lower = clean_name.lower()
                    for idx, keyword_group in enumerate(priority_keywords):
                        if any(kw in name_lower for kw in keyword_group):
                            priority = idx
                            break
                    
                    candidates.append((priority, clean_name))
            
            #dist = geodesic(photo_coords, (el['lat'], el['lon'])).miles
            
            # Sort by priority and take the best one
            if candidates:
                candidates.sort(key=lambda x: x[0])
                protected_area_name = candidates[0][1]
                if debug:
                    print(f"Overpass found {len(candidates)} candidates: {candidates[:5]}")
                    print(f"Selected: {protected_area_name}")
            elif debug:
                print(f"Overpass returned elements but no valid candidates")
        elif debug:
            print(f"Overpass API returned status code: {response.status_code}")
                
    except Exception as e:
        if debug:
            print(f"Overpass error: {e}")
        pass  # Fall through to Nominatim
    
    # Use Nominatim for state/country and fallback place info
    nominatim_url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': long,
        'format': 'json',
        'zoom': 16,  # Higher zoom for more specific locations
        'addressdetails': 1
    }
    headers = {
        'User-Agent': 'LocationDetailsApp/1.0'
    }
    
    try:
        response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        address = data.get('address', {})
        
        country = address.get('country', 'Unknown')
        state = (address.get('state') or 
                address.get('region') or 
                address.get('province') or 
                'Unknown')
        
        # If we found a protected area from Overpass, use that
        if protected_area_name:
            if debug:
                print(f"Using Overpass result: {protected_area_name}")
            return f"{protected_area_name}, {state}, {country}"
        
        if debug:
            print("No Overpass result, using Nominatim fallback")
            print(f"Address data: {address}")
        
        # Otherwise get place from Nominatim, avoiding townships and counties
        place_keys = [
            'tourism', 'leisure', 'amenity','city','town','hamlet', 'village',    # Points of interest
            'neighbourhood', 'suburb',  # Specific neighborhoods
            'municipality'  # Admin areas
        ]
        
        place = None
        for key in place_keys:
            if key in address and address[key]:
                candidate = address[key]
                # Skip if it's a township or county
                if 'township' not in candidate.lower() and 'county' not in candidate.lower():
                    place = candidate
                    break
        
        # If still no place, try to get the nearest city/town even if not in immediate address
        if not place:
            place = address.get('city') or address.get('town') or address.get('village')
        if not place:    
            for key in place_keys:
                if key in address and address[key]:
                    candidate = address[key]
                    # Skip if it's a township or county
                    if true:
                        place = candidate
                        break
        
        # Last resort: use first part of display_name, but NOT county
        if not place:
            display_name = data.get('display_name', 'Unknown Location')
            first_part = display_name.split(',')[0].strip()
            # Only use it if it doesn't contain "County" or "Township"
            if 'county' not in first_part.lower() and 'township' not in first_part.lower() and 'road' not in first_part.lower() and 'drive' not in first_part.lower() and 'street' not in first_part.lower():
                place = first_part
            else:
                # Try second part of display name instead
                parts = display_name.split(',')
                if len(parts) > 1:
                    place = parts[1].strip()
                else:
                    place = first_part.replace(' County', '').replace(' Township', '')
        
        return f"{place}, {state}, {country}"
        
    except Exception as e:
        return f"Error: {str(e)}"

















from geopy.distance import geodesic
def get_overpass_context(lat, lon):
    """
    Uses Overpass to find the State (admin_level 4) 
    and Country (admin_level 2) containing the coordinates.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # This query asks: "What administrative areas contain this point?"
    query = f"""
    [out:json][timeout:15];
    is_in({lat},{lon})->.a;
    rel(pivot.a)["boundary"="administrative"]["admin_level"~"2|4"];
    out tags;
    """
    
    context = {"state": "", "country": ""}
    
    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=15)
        if response.status_code == 200:
            elements = response.json().get('elements', [])
            for el in elements:
                tags = el.get('tags', {})
                name = tags.get('name:en') or tags.get('name')
                level = tags.get('admin_level')
                
                if level == "2":
                    context["country"] = name
                if level == "4":
                    context["state"] = name
    except Exception as e:
        print(f"Overpass Context Error: {e}")
        
    return context
def find_nearest_neighbor_overpass(lat, lon):
    overpass_url = "https://overpass-api.de/api/interpreter"
    photo_coords = (lat, lon)
    radius = 30000 # 30km (~18 miles)

    query = f"""
    [out:json][timeout:25];
    (
      # Only look for actual named Settlements
      node["place"~"city|town|village"](around:{radius},{lat},{lon});
      
      # Only look for designated National/State lands and Parks
      node["boundary"~"national_park|protected_area|national_lakeshore|seashore"](around:{radius},{lat},{lon});
      node["leisure"~"nature_reserve|park"](around:{radius},{lat},{lon});
      node["natural"~"wood|forest"](around:{radius},{lat},{lon});
    );
    out body;
    """
    
    try:
        headers = {'User-Agent': 'Vitez_Photo_Archive_Script'}
        response = requests.post(overpass_url, data={'data': query}, timeout=20, headers=headers)
        if response.status_code != 200: return None
            
        data = response.json()
        elements = data.get('elements', [])
        if not elements: return None

        nature_hits = []
        city_hits = []

        for el in elements:
            tags = el.get('tags', {})
            name = tags.get('name:en') or tags.get('name')
            if not name: continue
            
            # --- THE POND SHIELD ---
            # Skip minor water features that clutter the results
            blacklist = ["POND", "RETENTION", "CANAL", "DITCH", "DRAIN", "CREEK"]
            if any(word in name.upper() for word in blacklist):
                continue


            
            # Categorize
            # We only count it as 'Nature' if it's a Park, Forest, or Protected Area
            is_nature = any(t in tags for t in ['leisure', 'boundary', 'natural'])
            
            if is_nature:
                nature_hits.append((name, dist))
            else:
                city_hits.append((name, dist))

        print(nature_hits, city_hits)

        # Nature gets priority over cities
        if nature_hits:
            nature_hits.sort(key=lambda x: x[1])
            return nature_hits[0][0]
            
        if city_hits:
            city_hits.sort(key=lambda x: x[1])
            return city_hits[0][0]

    except:
        return None
    return None

def format_location_string(place, addr):
    """Formats everything to: PLACE, STATE, COUNTRY"""
    # Ensure addr is a dict
    if not addr: addr = {}
    
    state = addr.get('state', "")
    country = addr.get('country', "")
    
    # Standardize USA
    c_name = "USA" if "UNITED STATES" in country.upper() else country.upper()
    
    place_str = str(place).upper()
    parts = [place_str]
    
    # Add State if it's not already in the name
    if state and state.upper() not in place_str:
        parts.append(state.upper())
    
    if c_name:
        parts.append(c_name)
    
    return ", ".join(dict.fromkeys(p for p in parts if p))

# ... [Keep your get_decimal_from_dms, get_gps_data, and process() functions as they























def get_gps_data(exif):
    """
    Tries multiple methods to find GPS data in EXIF.
    Returns (lat, lon) or (None, None)
    """
    gps_info = {}
    
    # Method 1: Modern Pillow get_ifd (for GPS IFD)
    try:
        raw_gps = exif.get_ifd(0x8825)
        if raw_gps:
            for tag, value in raw_gps.items():
                decoded = ExifTags.GPSTAGS.get(tag, tag)
                gps_info[decoded] = value
    except: pass

    # Method 2: Fallback to old GPSInfo tag
    if not gps_info:
        try:
            # 34853 is the tag for GPSInfo
            raw_gps = exif.get(34853)
            if raw_gps:
                for tag, value in raw_gps.items():
                    decoded = ExifTags.GPSTAGS.get(tag, tag)
                    gps_info[decoded] = value
        except: pass

    if gps_info:
        lat = get_decimal_from_dms(gps_info.get('GPSLatitude'), gps_info.get('GPSLatitudeRef'))
        lon = get_decimal_from_dms(gps_info.get('GPSLongitude'), gps_info.get('GPSLongitudeRef'))
        return lat, lon
    
    return None, None

def process():
    dimensions_data = {}
    source_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    source_files.sort(key=lambda x: os.path.getmtime(os.path.join(SOURCE_DIR, x)), reverse=True)

    print(f"Deep-scanning {len(source_files)} images...")

    for index, filename in enumerate(source_files):
        archive_no = str(index + 1).zfill(3)
        webp_name = f"{archive_no}.webp"
        
        file_path = os.path.join(SOURCE_DIR, filename)
        try:
            with Image.open(file_path) as img:
                img = ImageOps.exif_transpose(img)
                img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                width, height = img.size
                ratio = round(height / width, 4)

                exif = img.getexif()
                date_taken, location_str = "---", "UNKNOWN LOCATION"

                # 1. Get Date (0x8769 is the ExifSubIFD)
                sub_exif = exif.get_ifd(0x8769)
                raw_date = sub_exif.get(36867) or exif.get(306)
                if raw_date:
                    try:
                        parts = str(raw_date).split(" ")[0].split(":")
                        month = calendar.month_name[int(parts[1])].upper()[:3]
                        date_taken = f"{month} {parts[0]}"
                    except: pass

                # 2. Get GPS using our new robust function
                lat, lon = get_gps_data(exif)
                
                if lat and lon:
                    # Success! We found coordinates. Now get the address.
                    time.sleep(2.0)
                    location_str = get_location_details(lat, lon)
                else:
                    # Diagnostic: Tell us if the file actually has no GPS
                    print(f" ! No GPS tags found in {filename}")

                # 3. Save
                img.save(os.path.join(OUTPUT_DIR, webp_name), "WEBP", quality=QUALITY)
                
                dimensions_data[webp_name] = {
                    "number": archive_no,
                    "ratio": ratio,
                    "date": date_taken,
                    "location": location_str
                }
                print(f"[{archive_no}] {location_str} | {date_taken}")

        except Exception as e:
            print(f"ERROR on {filename}: {e}")

    with open("dimensions.json", "w") as f:
        json.dump(dimensions_data, f, indent=4, sort_keys=True)



if __name__ == "__main__":
    process()
