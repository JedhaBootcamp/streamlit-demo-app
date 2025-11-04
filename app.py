import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

### ----------------------------------------------------
### 🧠 CONFIGURATION SECTION
### ----------------------------------------------------

# st.set_page_config() defines metadata and layout of your Streamlit app.
# You can set the page title, the emoji/icon, and whether the layout is "wide" or "centered".
st.set_page_config(
    page_title="E-commerce",
    page_icon="💸 ",
    layout="wide"
)

# Public CSV file containing fake e-commerce sales data
DATA_URL = ('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/e-commerce_data.csv')

### ----------------------------------------------------
### 🎨 APP HEADER
### ----------------------------------------------------

# st.title() displays a large page title at the top of your app.
st.title("Build dashboards with Streamlit 🎨")

# st.markdown() allows you to write rich text using Markdown syntax.
# It can display paragraphs, links, emojis, code, etc.
st.markdown("""
    Welcome to this awesome `streamlit` dashboard. This library is great to build very fast and
    intuitive charts and applications running on the web. Here is a showcase of what you can do with
    it. Our data comes from an e-commerce website that simply displays samples of customer sales. Let's check it out.

    Also, if you want to have a real quick overview of what Streamlit is all about, feel free to watch the below video 👇
""")

# st.expander() creates a collapsible section the user can open/close.
with st.expander("⏯️ Watch this 15min tutorial"):
    # st.video() embeds a YouTube video or local video file in your app.
    st.video("https://youtu.be/B2iAodr0fOo")

# Horizontal separator line
st.markdown("---")


### ----------------------------------------------------
### 📦 LOAD DATA
### ----------------------------------------------------

# @st.cache_data is a Streamlit decorator that caches function results.
# When you reload the app, data is read from the cache instead of reloading from the source.
@st.cache_data
def load_data(nrows):
    # Load CSV file with pandas
    data = pd.read_csv(DATA_URL, nrows=nrows)
    # Format columns properly (convert strings to datetime/numeric)
    data["Date"] = data["Date"].apply(lambda x: pd.to_datetime(",".join(x.split(",")[-2:])))
    data["currency"] = data["currency"].apply(lambda x: pd.to_numeric(x[1:]))
    return data

# st.subheader() creates a smaller section title.
st.subheader("Load and showcase data")

st.markdown("""
    You can use the usual Data Science libraries like `pandas` or `numpy` to load data. 
    Then simply use [`st.write()`](https://docs.streamlit.io/library/api-reference/write-magic/st.write) to showcase it on your web app. 
""")

# st.text() displays plain text — useful for showing loading states or messages.
data_load_state = st.text('Loading data...')

# Load the data
data = load_data(1000)

# Once loaded, we clear the loading message
data_load_state.text("") 

# st.checkbox() creates a checkable box. When checked, its value is True.
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    # st.write() is Streamlit’s universal “display anything” function:
    # It can show dataframes, text, charts, and more.
    st.write(data)    


### ----------------------------------------------------
### 📊 SIMPLE CHARTS WITH STREAMLIT
### ----------------------------------------------------

st.subheader("Simple bar chart built directly with Streamlit")

st.markdown("""
    You can build simple charts directly with Streamlit using:
    * [`st.bar_chart`](https://docs.streamlit.io/library/api-reference/charts/st.bar_chart)
    * [`st.line_chart`](https://docs.streamlit.io/library/api-reference/charts/st.line_chart)
    * [`st.area_chart`](https://docs.streamlit.io/library/api-reference/charts/st.area_chart)

    These are great for quick visualizations — they automatically detect the data structure
    from a pandas DataFrame or Numpy array.
""")

# Build a basic bar chart directly using Streamlit
currency_per_country = data.set_index("country")["currency"]
st.bar_chart(currency_per_country)  # Automatically renders a bar chart


### ----------------------------------------------------
### 📈 CHARTS BUILT WITH PLOTLY
### ----------------------------------------------------

st.subheader("Simple bar chart built with Plotly")

st.markdown("""
    Streamlit is compatible with many visualization libraries like:
    * [`plotly`](https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart) 
    * [`matplotlib`](https://docs.streamlit.io/library/api-reference/charts/st.pyplot)
    * [`bokeh`](https://docs.streamlit.io/library/api-reference/charts/st.bokeh_chart)
    
    This gives you much more control over design, colors, and interactivity. 🥰
""")

# Create a Plotly figure
fig = px.histogram(data.sort_values("country"), x="country", y="currency", barmode="group")

# st.plotly_chart() embeds a Plotly chart inside your Streamlit app.
st.plotly_chart(fig, use_container_width=True)


### ----------------------------------------------------
### 🎛️ INPUT WIDGETS & FORMS
### ----------------------------------------------------

st.subheader("Input data")

st.markdown("""
    You can also let users interact with your app through input widgets:
    * Dropdowns, sliders, text inputs, date pickers, etc.
    * Or use a `form` to group several widgets and submit them together.
""")

# st.columns() allows to split the page into columns for better layout control.
col1, col2 = st.columns(2)

with col1:
    st.markdown("**1️⃣ Example of input widget**")

    # st.selectbox() creates a dropdown list from which the user can select one option.
    country = st.selectbox("Select a country you want to see all time sales", data["country"].sort_values().unique())
    
    # Filter dataset according to the selected value
    country_sales = data[data["country"] == country]

    # Build a chart from filtered data
    fig = px.histogram(country_sales, x="Date", y="currency")
    fig.update_layout(bargap=0.2)

    # Display chart
    st.plotly_chart(fig, use_container_width=True)


with col2:
    st.markdown("**2️⃣ Example of input form**")

    # st.form() lets you create a group of input widgets that only run after clicking "Submit".
    with st.form("average_sales_per_country"):
        country = st.selectbox("Select a country you want to see sales", data["country"].sort_values().unique())
        start_period = st.date_input("Select a start date you want to see your metric")
        end_period = st.date_input("Select an end date you want to see your metric")

        # st.form_submit_button() adds a button that triggers the form submission.
        submit = st.form_submit_button("submit")

        if submit:
            # When the form is submitted, process user input and display results dynamically
            avg_period_country_sales = data[(data["country"] == country)]
            start_period, end_period = pd.to_datetime(start_period), pd.to_datetime(end_period)
            mask = (avg_period_country_sales["Date"] > start_period) & (avg_period_country_sales["Date"] < end_period)
            avg_period_country_sales = avg_period_country_sales[mask].mean()

            # st.metric() displays a KPI-style number with optional delta or color formatting.
            st.metric("Average sales during selected period (in $)", np.round(avg_period_country_sales, 2))


### ----------------------------------------------------
### 🧭 SIDEBAR MENU
### ----------------------------------------------------

# st.sidebar gives you access to a dedicated sidebar panel.
# Useful for navigation menus, filters, or extra info.
st.sidebar.header("Build dashboards with Streamlit")
st.sidebar.markdown("""
    * [Load and showcase data](#load-and-showcase-data)
    * [Charts directly built with Streamlit](#simple-bar-chart-built-directly-with-streamlit)
    * [Charts built with Plotly](#simple-bar-chart-built-with-plotly)
    * [Input Data](#input-data)
""")

# st.sidebar.empty() creates an empty container you can fill dynamically later.
e = st.sidebar.empty()
e.write("")

# st.sidebar.write() works exactly like st.write(), but in the sidebar area.
st.sidebar.write("Made with 💖 by [Jedha](https://jedha.co)")


### ----------------------------------------------------
### 🍇 FOOTER SECTION
### ----------------------------------------------------

# st.columns() is used again to align footer content horizontally.
empty_space, footer = st.columns([1, 2])

with empty_space:
    st.write("")  # Just a visual spacer

with footer:
    st.markdown("""
        🍇  
        If you want to learn more, check out [streamlit's documentation](https://docs.streamlit.io/) 📖
    """)
