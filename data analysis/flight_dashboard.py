import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Set page config
st.set_page_config(page_title="International Flight Routes Dashboard", layout="wide")

# Title
st.title("✈️ International Flight Routes Dashboard - USA")
st.markdown("### Visualizing flight routes with color-coded traffic intensity")

# Load and process data
@st.cache_data
def load_data():
    # Load flight data
    file_paths = [
        '../data1/flightlist_20200101_20200131.csv.gz',
        '../data1/flightlist_20200201_20200229.csv.gz',
        '../data1/flightlist_20200301_20200331.csv.gz',
        '../data1/flightlist_20200401_20200430.csv.gz'
    ]
    
    all_dfs = [pd.read_csv(fp, compression='gzip') for fp in file_paths]
    df = pd.concat(all_dfs, ignore_index=True)
    
    # Load airports data
    columns = ['Airport ID', 'Name', 'City', 'Country', 'IATA', 'ICAO', 
               'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST', 
               'Tz database time zone', 'Type', 'Source']
    airports_df = pd.read_csv('../data1/airports.dat', names=columns, header=None, na_values='\\N')
    
    # Filter for flights with different origin and destination
    df = df[df['origin'] != df['destination']]
    
    # Merge with airport info
    flights_with_origin = df.merge(
        airports_df[['ICAO', 'Name', 'City', 'Country', 'IATA', 'Latitude', 'Longitude']],
        left_on='origin',
        right_on='ICAO',
        how='left',
        suffixes=('', '_origin')
    )
    
    flights_with_airport_info = flights_with_origin.merge(
        airports_df[['ICAO', 'Name', 'City', 'Country', 'IATA', 'Latitude', 'Longitude']],
        left_on='destination',
        right_on='ICAO',
        how='left',
        suffixes=('', '_destination')
    )
    
    # Filter for USA international flights
    flights_with_airport_info_in_USA = flights_with_airport_info[
        (flights_with_airport_info['Country'] == 'United States') |
        (flights_with_airport_info['Country_destination'] == 'United States')
    ]
    
    internation_flights_usa = flights_with_airport_info_in_USA[
        flights_with_airport_info_in_USA['Country'] != flights_with_airport_info_in_USA['Country_destination']
    ]
    
    # Create clean graph data
    graph_data = internation_flights_usa[
        internation_flights_usa['City'].notna() & 
        internation_flights_usa['Country'].notna() & 
        internation_flights_usa['City_destination'].notna() & 
        internation_flights_usa['Country_destination'].notna() &
        internation_flights_usa['Latitude'].notna() &
        internation_flights_usa['Longitude'].notna() &
        internation_flights_usa['Latitude_destination'].notna() &
        internation_flights_usa['Longitude_destination'].notna()
    ].copy()
    
    return graph_data

# Load data
with st.spinner("Loading flight data..."):
    graph_data = load_data()

# Aggregate routes by city pairs with coordinates
route_data = graph_data.groupby([
    'City', 'Country', 'Latitude', 'Longitude',
    'City_destination', 'Country_destination', 'Latitude_destination', 'Longitude_destination'
]).size().reset_index(name='flight_count')

# Sidebar controls
st.sidebar.header("⚙️ Dashboard Controls")

# Flight count filter
min_flights = int(route_data['flight_count'].min())
max_flights = int(route_data['flight_count'].max())

st.sidebar.subheader("Filter by Flight Count")
flight_threshold = st.sidebar.slider(
    "Minimum flights per route:",
    min_value=min_flights,
    max_value=min(1000, max_flights),
    value=min(50, max_flights),
    step=10
)

# Filter data
filtered_routes = route_data[route_data['flight_count'] >= flight_threshold].copy()

# Display statistics
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Statistics")
st.sidebar.metric("Total Routes (filtered)", len(filtered_routes))
st.sidebar.metric("Total Flights", f"{filtered_routes['flight_count'].sum():,}")
st.sidebar.metric("Avg Flights/Route", f"{filtered_routes['flight_count'].mean():.0f}")

# Color scale selection
color_scale_options = ['Viridis', 'Plasma', 'Inferno', 'Turbo', 'Jet', 'Rainbow']
selected_color_scale = st.sidebar.selectbox(
    "Color Scale:",
    color_scale_options,
    index=0
)

# Map projection
projection_options = ['natural earth', 'orthographic', 'mercator', 'equirectangular']
selected_projection = st.sidebar.selectbox(
    "Map Projection:",
    projection_options,
    index=0
)

# Create color scale based on flight counts
def get_color_from_count(count, min_count, max_count, colorscale):
    """Get color based on flight count using the selected colorscale"""
    if max_count == min_count:
        normalized = 0.5
    else:
        normalized = (count - min_count) / (max_count - min_count)
    
    # Plotly colorscales
    colorscale_dict = {
        'Viridis': 'Viridis',
        'Plasma': 'Plasma',
        'Inferno': 'Inferno',
        'Turbo': 'Turbo',
        'Jet': 'Jet',
        'Rainbow': 'Rainbow'
    }
    
    import plotly.colors as pc
    colorscale_name = colorscale_dict[colorscale]
    colors = pc.sample_colorscale(colorscale_name, [normalized])[0]
    return colors

# Prepare data for visualization
min_count = filtered_routes['flight_count'].min()
max_count = filtered_routes['flight_count'].max()

# Create figure
fig = go.Figure()

# Add routes as lines
for idx, row in filtered_routes.iterrows():
    color = get_color_from_count(row['flight_count'], min_count, max_count, selected_color_scale)
    
    # Create great circle path (approximate with straight line for simplicity)
    fig.add_trace(go.Scattergeo(
        lon=[row['Longitude'], row['Longitude_destination']],
        lat=[row['Latitude'], row['Latitude_destination']],
        mode='lines',
        line=dict(width=1 + (row['flight_count'] - min_count) / (max_count - min_count) * 3, color=color),
        opacity=0.5,
        hovertemplate=(
            f"<b>Route:</b> {row['City']}, {row['Country']} → {row['City_destination']}, {row['Country_destination']}<br>"
            f"<b>Flights:</b> {row['flight_count']:,}<br>"
            "<extra></extra>"
        ),
        showlegend=False
    ))

# Add airport markers
unique_origins = filtered_routes[['City', 'Country', 'Latitude', 'Longitude']].drop_duplicates()
unique_destinations = filtered_routes[['City_destination', 'Country_destination', 'Latitude_destination', 'Longitude_destination']].drop_duplicates()
unique_destinations.columns = ['City', 'Country', 'Latitude', 'Longitude']
unique_airports = pd.concat([unique_origins, unique_destinations]).drop_duplicates()

fig.add_trace(go.Scattergeo(
    lon=unique_airports['Longitude'],
    lat=unique_airports['Latitude'],
    mode='markers',
    marker=dict(size=4, color='red', line=dict(width=0.5, color='white')),
    text=unique_airports['City'] + ', ' + unique_airports['Country'],
    hovertemplate='<b>%{text}</b><extra></extra>',
    name='Airports',
    showlegend=True
))

# Update layout
fig.update_layout(
    title=f"International Flight Routes (≥ {flight_threshold} flights per route)",
    geo=dict(
        projection_type=selected_projection,
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showocean=True,
        oceancolor='rgb(230, 245, 255)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)',
    ),
    height=700,
    showlegend=True
)

# Display the map
st.plotly_chart(fig, use_container_width=True)

# Create legend for color scale
st.markdown("### 🎨 Flight Count Legend")

# Create a horizontal color bar
legend_values = np.linspace(min_count, max_count, 10)
legend_colors = [get_color_from_count(val, min_count, max_count, selected_color_scale) for val in legend_values]

legend_fig = go.Figure()

for i, (val, color) in enumerate(zip(legend_values, legend_colors)):
    legend_fig.add_trace(go.Bar(
        x=[1],
        y=[val],
        orientation='v',
        marker=dict(color=color),
        name=f"{int(val):,}",
        hovertemplate=f"<b>Flight Count:</b> {int(val):,}<extra></extra>",
        showlegend=False
    ))

legend_fig.update_layout(
    barmode='stack',
    height=100,
    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    yaxis=dict(title="Number of Flights", showgrid=True),
    margin=dict(l=50, r=20, t=20, b=30)
)

st.plotly_chart(legend_fig, use_container_width=True)

# Display top routes table
st.markdown("### 📈 Top 20 Busiest Routes")
top_routes = filtered_routes.nlargest(20, 'flight_count')[
    ['City', 'Country', 'City_destination', 'Country_destination', 'flight_count']
].copy()
top_routes.columns = ['Origin City', 'Origin Country', 'Destination City', 'Destination Country', 'Flight Count']
top_routes['Flight Count'] = top_routes['Flight Count'].apply(lambda x: f"{x:,}")
st.dataframe(top_routes, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("*Data: OpenFlights Database | Period: January - April 2020*")

