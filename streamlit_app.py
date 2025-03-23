################################################################################
# US POPULATION DASHBOARD
# This application visualizes US population data from 2010-2019 using Streamlit
# Author: Unknown
# Modified: [Current Date]
################################################################################

################################################################################
# SECTION 1: SETUP AND CONFIGURATION
# Importing necessary libraries and configuring the page layout
################################################################################
import streamlit as st  # Main framework for creating web applications
import pandas as pd     # Data manipulation library
import altair as alt    # Declarative statistical visualization library
import plotly.express as px  # Interactive plotting library

# Page configuration to set overall dashboard properties
# - Title appears in browser tab
# - Icon appears next to title
# - Wide layout maximizes available screen space
# - Expanded sidebar ensures filters are immediately visible
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

# Enable dark theme for Altair visualizations to match dashboard aesthetics
alt.themes.enable("dark")

################################################################################
# SECTION 2: STYLING
# Custom CSS to enhance the visual appearance of dashboard components
# This overrides Streamlit's default styles for various elements
################################################################################
st.markdown("""
<style>
/* Main container padding adjustments for better spacing */
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

/* Vertical block adjustment to maximize screen real estate */
[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Metric styling - these are the number displays with deltas */
[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

/* Center alignment for metric labels */
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Position adjustments for up/down delta icons */
[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
</style>
""", unsafe_allow_html=True)

################################################################################
# SECTION 3: DATA LOADING
# Loading the preprocessed dataset for population analysis
################################################################################
# The reshaped dataset contains yearly population data for all US states
# CSV is expected to have columns: states, year, population, and state codes
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')

################################################################################
# SECTION 4: SIDEBAR FILTERS
# Creating interactive controls for user filtering and visualization preferences
################################################################################
with st.sidebar:
    st.title('🏂 US Population Dashboard')
    
    # Create a reversed year list to show most recent years first
    # This improves UX by making recent data more accessible
    year_list = list(df_reshaped.year.unique())[::-1]
    
    # Year selector dropdown with filtered dataset based on selection
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    
    # Sort states by population for ordered display in visualizations
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    # Color theme selector for customizing visualizations
    # Different color scales evoke different emotional responses and highlight different patterns
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

################################################################################
# SECTION 5: VISUALIZATION FUNCTIONS
# Reusable functions to create various chart types
################################################################################

# Heatmap function: Creates a rectangular heatmap showing population by state and year
# Parameters:
# - input_df: DataFrame containing the data
# - input_y: Column name for y-axis (typically 'year')
# - input_x: Column name for x-axis (typically 'states')
# - input_color: Column name for color encoding (typically 'population')
# - input_color_theme: Color scheme to use
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',  # Using max() aggregation for color scale
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),  # Adding borders between cells for better separation
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300 (commented out to allow dynamic height)
    return heatmap

# Choropleth map function: Creates a US map with states colored by population
# Parameters:
# - input_df: DataFrame containing the data
# - input_id: Column name with state codes for mapping
# - input_column: Column name for color encoding (typically 'population')
# - input_color_theme: Color scheme to use
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, 
                               locations=input_id,  # State codes column
                               color=input_column,  # Values used for color encoding
                               locationmode="USA-states",  # Set to US states mapping
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),  # Consistent color scale
                               scope="usa",  # Focus map on USA only
                               labels={'population':'Population'}
                              )
    # Customize layout for seamless dashboard integration
    choropleth.update_layout(
        template='plotly_dark',  # Match dashboard theme
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
        margin=dict(l=0, r=0, t=0, b=0),  # Remove margins
        height=350
    )
    return choropleth

# Donut chart function: Creates a donut chart for migration percentages
# Parameters:
# - input_response: Percentage value to display (e.g., 35 for 35%)
# - input_text: Label for the chart
# - input_color: Color theme ('blue', 'green', 'orange', or 'red')
def make_donut(input_response, input_text, input_color):
    # Color mapping for different chart types
    # Using dark/light pairs for contrast and visual appeal
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    
    # Create data frames for main chart and background
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]  # Split into filled and empty portions
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]  # Background is 100% filled with lighter color
    })
    
    # Create main donut chart with rounded corners
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",  # Arc angle based on percentage
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),  # Map colors to segments
                        legend=None),  # Hide legend for cleaner display
    ).properties(width=130, height=130)
    
    # Add text in the center of the donut showing the percentage
    text = plot.mark_text(
        align='center', 
        color="#29b5e8", 
        font="Lato", 
        fontSize=32, 
        fontWeight=700, 
        fontStyle="italic"
    ).encode(text=alt.value(f'{input_response} %'))
    
    # Create background donut for visual effect
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    # Combine all layers for final chart
    return plot_bg + plot + text

# Format population numbers for display (e.g., "12.3 M" instead of "12345678")
# This improves readability of large numbers in dashboard metrics
def format_number(num):
    if num > 1000000:
        if not num % 1000000:  # Check if it's an exact number of millions
            return f'{num // 1000000} M'  # Use integer division for clean numbers
        return f'{round(num / 1000000, 1)} M'  # Round to 1 decimal for clarity
    return f'{num // 1000} K'  # Format thousands with K suffix

# Calculate year-over-year population changes to identify migration patterns
# Parameters:
# - input_df: DataFrame with multi-year data
# - input_year: Selected year to compare with previous year
def calculate_population_difference(input_df, input_year):
    # Get data for selected year and previous year
    selected_year_data = input_df[input_df['year'] == input_year].reset_index()
    previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
    
    # Calculate the difference in population between selected and previous year
    # fill_value=0 handles cases where a state might not have data for previous year
    selected_year_data['population_difference'] = selected_year_data.population.sub(
        previous_year_data.population, fill_value=0)
    
    # Return a dataframe with only the necessary columns, sorted by population difference
    return pd.concat(
        [selected_year_data.states, selected_year_data.id, 
         selected_year_data.population, selected_year_data.population_difference], 
        axis=1
    ).sort_values(by="population_difference", ascending=False)

################################################################################
# SECTION 6: DASHBOARD LAYOUT AND VISUALIZATION RENDERING
# Creating the main dashboard panels and populating with visualizations
################################################################################
# Create three columns with specified width ratios:
# - Left column (1.5): Migration statistics
# - Middle column (4.5): Main visualizations (map and heatmap)
# - Right column (2): State rankings table
col = st.columns((1.5, 4.5, 2), gap='medium')

# Left Column: Population Gains/Losses and Migration Statistics
with col[0]:
    st.markdown('#### Gains/Losses')

    # Calculate population differences for selected year
    df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)

    # Display metrics for state with the largest population gain
    # Special handling for 2010 (first year) where no YoY comparison is possible
    if selected_year > 2010:
        first_state_name = df_population_difference_sorted.states.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    # Display metrics for state with the largest population loss
    if selected_year > 2010:
        last_state_name = df_population_difference_sorted.states.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.population.iloc[-1])   
        last_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])   
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    # States Migration Section - Donut charts showing migration patterns
    st.markdown('#### States Migration')

    if selected_year > 2010:
        # Identify states with significant migration (>50,000 people)
        df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference > 50000]
        df_less_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference < -50000]
        
        # Calculate percentage of states with significant inbound/outbound migration
        states_migration_greater = round((len(df_greater_50000)/df_population_difference_sorted.states.nunique())*100)
        states_migration_less = round((len(df_less_50000)/df_population_difference_sorted.states.nunique())*100)
        
        # Create donut charts for inbound and outbound migration percentages
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')
    else:
        # Set default values for 2010 (first year with no comparison)
        states_migration_greater = 0
        states_migration_less = 0
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')

    # Create sub-columns for donut charts with spacing for visual balance
    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)

# Middle Column: Map and Heatmap Visualizations
with col[1]:
    st.markdown('#### Total Population')
    
    # Create and display choropleth map of US states colored by population
    choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
    
    # Create and display heatmap showing population trends across years and states
    heatmap = make_heatmap(df_reshaped, 'year', 'states', 'population', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)
    
# Right Column: Top States Table and Information
with col[2]:
    st.markdown('#### Top States')

    # Create a searchable, sortable table of states with population data
    # ProgressColumn visualizes the relative population with bars for easier comparison
    st.dataframe(df_selected_year_sorted,
                 column_order=("states", "population"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "states": st.column_config.TextColumn(
                        "States",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.population),  # Scale based on largest state
                     )}
                 )
    
    # Information about the dashboard with data sources and key metrics explanation
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - 🔍 **Gains/Losses**: states with high inbound/ outbound migration for selected year
            - 📊 **States Migration**: percentage of states with annual inbound/ outbound migration > 50,000
            ''')