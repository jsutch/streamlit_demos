import pandas as pd
import streamlit as st
import plotly.express as px
import pydeck as pdk

@st.cache
def get_data():
    url = "http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv"
    return pd.read_csv(url)
    

df = get_data()

st.title("Streamlit 101: An in-depth introduction")
st.markdown("Welcome to this in-depth introduction to [...].")
st.header("Customary quote")
st.markdown("> I just love to go home, no matter where I am **test**")


st.subheader("Exploratory Data Analysis")
st.dataframe(df.head())


st.subheader("Specifying Code Blocks")
st.code("""
@st.cache
def get_data():
    url = ""http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv""
    return pd.read_csv(url)
""", language="python")

# st.map displays locations on a map without having to write a single line of boilerplate code to prepare a map object. The only requirement is that the dataframe must contain columns named lat/latitude or lon/longitude.

st.subheader("mapping")
st.markdown("showing the entire map with just 'data=df'")
st.map(data=df)

# showing map where 'price' > $800
df['price'] = df['price'].astype(int)

st.dataframe(df.info())

st.markdown("show only prices above $800")
# st.map(data=df[['price'] > 800])
st.deck_gl_chart(
     viewport={
         'latitude': 40.7477,
         'longitude': -73.9750,
         'zoom': 11,
         'pitch': 50,
     },
     layers=[{
         'type': 'HexagonLayer',
         'data': df,
         'radius': 200,
         'elevationScale': 4,
         'elevationRange': [0, 1000],
         'pickable': True,
         'extruded': True,
     }, {
         'type': 'ScatterplotLayer',
         'data': df,
     }])
# the new way to do that
# st.pydeck_chart()


st.header('subselecting columns')
cols = ["name", "host_name", "neighbourhood", "room_type", "price"]
st_ms = st.multiselect("Columns", df.columns.tolist(), default=cols)

