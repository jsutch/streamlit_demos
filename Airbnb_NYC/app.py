"""
Taken from and somewhat expanded upon:
https://towardsdatascience.com/streamlit-101-an-in-depth-introduction-fc8aad9492f2

The examples in the article don't jibe with the actual output in a number of cases.
I've added some of my own workarounds, but the original code is here
https://github.com/shaildeliwala/experiments/blob/master/streamlit.py
"""
import pandas as pd
import streamlit as st
import plotly.express as px
import pydeck as pdk

# drop error from pyplot global warning
st.set_option('deprecation.showPyplotGlobalUse', False)

@st.cache
def get_data():
    url = "http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv"
    return pd.read_csv(url)
    

df = get_data()

st.title("Streamlit 101 - st.title example")
st.markdown("updated with code where the examples had none. Some updates and workarounds also")
st.markdown("thx to https://towardsdatascience.com/streamlit-101-an-in-depth-introduction-fc8aad9492f2")
st.header("This is a header")
st.markdown("## this is an h2")
st.markdown("> Markdown testing *italic* **bold test**")


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


df['price'] = df['price'].astype(int)


st.markdown("show only prices above $800")
st.map(data=df[df['price'] > 800])

st.header('show 3d map with stacking')
# The deck_gl_chart widget is deprecated and will be removed on 2020-05-01. To render a map, you should use st.pydeck_chart widget.
# st.pydeck_chart uses a different format

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
st.dataframe(df[st_ms].head(10))

st.subheader('average price by room type')
st.table(df.groupby("room_type").price.mean().reset_index()\
.round(2).sort_values("price", ascending=False)\
.assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))


st.subheader('which hosts have most properties listed - displaying json')
st.json([{"id":3647,"name":"THE VILLAGE OF HARLEM....NEW YORK !","host_id":4632,"host_name":"Elisabeth","neighbourhood_group":"Manhattan","neighbourhood":"Harlem","latitude":40.80902,"longitude":-73.9419,"room_type":"Private room","price":150,"minimum_nights":3,"number_of_reviews":0,"last_review":1,"reviews_per_month":1,"calculated_host_listings_count":1,"availability_365":365},{"id":3831,"name":"Cozy Entire Floor of Brownstone","host_id":4869,"host_name":"LisaRoxanne","neighbourhood_group":"Brooklyn","neighbourhood":"Clinton Hill","latitude":40.68514,"longitude":-73.95976,"room_type":"Entire home\\/apt","price":89,"minimum_nights":1,"number_of_reviews":279,"last_review":"2019-08-29","reviews_per_month":4.62,"calculated_host_listings_count":1,"availability_365":192}])


st.header("side bar and price range slider")
values = st.sidebar.slider(label="Price Range", min_value=float(df.price.min()), max_value=1000., value=(50., 300.))
f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Price distribution")
f.update_xaxes(title="Price")
f.update_yaxes(title="No. of listings")
st.plotly_chart(f)

st.header('using radio buttons and checkboxes')
# this does not produce a df output showing the changes, as in the example
st.write("Using a radio button restricts selection to only one option at a time.")
neighborhood = st.radio("Neighborhood", df.neighbourhood_group.unique())
show_exp = st.checkbox("Include expensive listings")
show_exp = " and price<200" if not show_exp else ""

@st.cache
def get_availability(show_exp, neighborhood):
    return df.query(f"""neighbourhood_group==@neighborhood{show_exp}\
        and availability_365>0""").availability_365.describe(\
            percentiles=[.1, .25, .5, .75, .9, .99]).to_frame().T

st.table(get_availability(show_exp, neighborhood))


st.header('pyplot - average availability')
# this has a warning - 
# PyplotGlobalUseWarning: You are calling st.pyplot() without any arguments. After December 1st, 2020, we will remove the ability to do this as it requires the use of Matplotlib's global figure object, which is not thread-safe.

# To future-proof this code, you should pass in a figure as shown below:


# >>> fig, ax = plt.subplots()
# >>> ax.scatter([1, 2, 3], [1, 2, 3])
# >>>    ... other plotting actions ...
# >>> st.pyplot(fig)

df.query("availability_365>0")\
.groupby("neighbourhood_group")\
.availability_365.mean()\
.plot.bar(rot=0)\
.set(title="Average availability by neighborhood group",\
xlabel="Neighborhood group", ylabel="Avg. availability (in no. of days)")
st.pyplot()


st.header('show number of reviews - sidebar number input')
# this is borked over value variables.
# Magics
# Notice how in the Number of Reviews section above, we wrote df.query("@minimum<=number_of_reviews<=@maximum")on its own line without wrapping it in a call to st.dataframe. This still rendered a dataframe because Streamlit detects a variable or literal on its own line and uses st.write to render it.

minimum = st.sidebar.number_input("Minimum", min_value=0, value=0)
maximum = st.sidebar.number_input("Maximum", min_value=0, value=5)
st.write('min and max are:', minimum, maximum)
if minimum > maximum:
    st.error("Please enter a valid range")
else:
    # df.query("@minimum<=number_of_reviews<=@maximum")
    df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False)\
        .head(50)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]
st.markdown('completed min and max section')



st.header('images and dropdowns')
pics = {
    "Cat": "https://cdn.pixabay.com/photo/2016/09/24/22/20/cat-1692702_960_720.jpg",
    "Puppy": "https://cdn.pixabay.com/photo/2019/03/15/19/19/puppy-4057786_960_720.jpg",
    "Sci-fi city": "https://storage.needpix.com/rsynced_images/science-fiction-2971848_1280.jpg"
}
pic = st.selectbox("Picture choices", list(pics.keys()), 0)
st.image(pics[pic], use_column_width=True, caption=pics[pic])


st.markdown("## Party time!")
st.write("Yay! You're done with this tutorial of Streamlit. Click below to celebrate.")
btn = st.button("Celebrate!")
if btn:
    st.balloons()