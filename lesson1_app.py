import streamlit as st
import folium
from streamlit_folium import st_folium
import geonamescache

st.title("World Explorer: Fly Anywhere with 2 Numbers!")
st.write("Your mission: land near a big city on **all 6 continents** and collect a passport stamp from each.")

# Step 1: load real cities (offline)
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = [c for c in gc.get_cities().values() if c["population"] >= 1_000_000]
continents = {"AS": "Asia", "AF": "Africa", "EU": "Europe",
              "NA": "North America", "SA": "South America", "OC": "Oceania"}

if "stamps" not in st.session_state:
    st.session_state.stamps = {}          # continent -> where you landed

# Step 2: the two secret numbers
lat = st.slider("Latitude (moves you North / South)", -90.0, 90.0, 0.0)
lon = st.slider("Longitude (moves you East / West)", -180.0, 180.0, 0.0)

# Step 3: which city is closest to where you landed?
def gap(city):
    return (city["latitude"] - lat) ** 2 + (city["longitude"] - lon) ** 2

near = min(cities, key=gap)
country = countries[near["countrycode"]]
on_land = gap(near) ** 0.5 < 8            # farther than 8 degrees = nothing nearby

if on_land:
    st.success(f"You landed near {near['name']}, {country['name']}!")
    if st.button("Stamp my passport"):
        st.session_state.stamps[continents[country["continentcode"]]] = f"{near['name']}, {country['name']}"
else:
    st.warning("Splash! Open ocean or empty wilderness. Try different numbers!")

# Step 4: the map shows where you are, plus your stamps
m = folium.Map(location=[20, 0], zoom_start=2, tiles="Esri.WorldImagery")
folium.PolyLine([[0, -180], [0, 180]], color="yellow", tooltip="Equator").add_to(m)
folium.PolyLine([[-90, 0], [90, 0]], color="cyan", tooltip="Prime Meridian").add_to(m)
folium.Marker([lat, lon], icon=folium.Icon(color="red", icon="plane", prefix="fa")).add_to(m)
st_folium(m, height=420, returned_objects=[])

# Step 5: passport and progress
st.progress(len(st.session_state.stamps) / 6, text=f"{len(st.session_state.stamps)} of 6 continents")
st.dataframe([{"Continent": k, "Landed near": v} for k, v in st.session_state.stamps.items()])
if len(st.session_state.stamps) == 6:
    st.balloons()
    st.success("You travelled the whole world using only numbers! Every dot on a map is just "
               "latitude + longitude. Next lesson: make those dots show how BIG each city is.")
