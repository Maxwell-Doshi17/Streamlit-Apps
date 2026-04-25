import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st
#Full dataset with storm events from 2015-2025
counties = pd.read_csv("data/illinois_counties.csv")
year2025 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2025_c20250818.csv")
year2024 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2024_c20250818.csv")
year2023 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2023_c20250731.csv")
year2022 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2022_c20250721.csv")
year2021 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2021_c20250520.csv")
year2020 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2020_c20250702.csv")
year2019 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2019_c20250520.csv")
year2018 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2018_c20250520.csv")
year2017 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2017_c20250520.csv")
year2016 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2016_c20250818.csv")
year2015 = pd.read_csv("data/StormEvents_details-ftp_v1.0_d2015_c20250818.csv")
storm_full = pd.concat([year2015, year2016, year2017, year2018, year2019, year2020, year2021, year2022, year2023, year2024, year2025], ignore_index=True)
#Clean data so county names match 
counties['county'] = (
    counties['county']
    .str.replace('-', ' ', regex=False)                      
    .str.replace("dekalb", "DE KALB", case=False, regex=False)
    .str.replace("dupage", "DU PAGE", case=False, regex=False)
    .str.replace("lasalle", "LA SALLE", case=False, regex=False)
    .str.upper()
    .str.replace('st clair', 'ST. CLAIR', case=False, regex=False)                              
)

def clean_county(series):
    return (
        series
        .str.replace('-', ' ', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace("LASALLE", "LA SALLE", regex=False)
        .str.replace("DEKALB", "DE KALB", regex=False)
        .str.replace("DEWITT", "DE WITT", regex=False)
        .str.replace("DUPAGE", "DU PAGE", regex=False)
        .str.strip()
        .str.upper()
    )
counties['county'] = clean_county(counties['county'])

#Select incident range
illinois = storm_full[storm_full["STATE"] == "ILLINOIS"]
illinois2 = illinois[(illinois["BEGIN_YEARMONTH"] >= 201510) &
                     (illinois["BEGIN_YEARMONTH"] <= 202510)]
#convert property and crop damage to floats
def convert_damage(value):
    if isinstance(value, str):
        value = value.upper().replace(',', '').strip()
        if value.endswith('K'):
            return int(float(value[:-1]) * 1000)
        elif value.endswith('M'):
            return int(float(value[:-1]) * 1_000_000)
        elif value.endswith('B'):
            return int(float(value[:-1]) * 1_000_000_000)
        else:
            return int(float(value))
    return value  
illinois_map = gpd.read_file("data/IL_BNDY_County_Py[1].shp")
illinois_map['county'] = clean_county(illinois_map['COUNTY_NAM'])
illinois2['DAMAGE_PROPERTY'] = illinois2['DAMAGE_PROPERTY'].apply(convert_damage)
illinois2['DAMAGE_CROPS'] = illinois2['DAMAGE_CROPS'].apply(convert_damage)
#Combine incidents with corresponding county data
illinois2['CZ_NAME'] = clean_county(illinois2['CZ_NAME'])
merged = pd.merge(
    illinois2,
    counties,
    left_on='CZ_NAME',
    right_on='county',
    how='inner'  # or 'left' if you want to keep all storm events
)
#clean
merged_filled = merged.fillna(0)
merged_filled['county'] = clean_county(merged_filled['county'])
damaging_incidents = merged_filled[merged_filled['DAMAGE_PROPERTY'] > 0]
incident_counts = damaging_incidents['county'].value_counts().sort_values(ascending=False)
plt.style.use('dark_background')

st.title("Illinois County Insights: Housing, Income & Storm Impact")
st.markdown("""This dashboard visualizes county-level patterns across Illinois, 
            including housing, income, and storm-related impacts. It allows 
            users to explore geographic disparities and identify trends across regions. 
            The storm data is from the years 2015 to 2025.""")


propdamage_incident_counts = (
    merged_filled[merged_filled['DAMAGE_PROPERTY'] > 0]
    .groupby('county')
    .size()
    .reset_index(name='propdamage_incident_counts')
)
propdamage_incident_counts['county'] = (
    propdamage_incident_counts['county']
    .str.replace('-', ' ', regex=False)
    .str.replace('.', '', regex=False)
    .str.strip()
    .str.upper()
)
cropdamage_incident_counts = (
    merged_filled[merged_filled['DAMAGE_CROPS'] > 0]
    .groupby('county')
    .size()
    .reset_index(name='cropdamage_incident_counts')
)
cropdamage_incident_counts['county'] = (
    cropdamage_incident_counts['county']
    .str.replace('-', ' ', regex=False)
    .str.replace('.', '', regex=False)
    .str.strip()
    .str.upper()
)
incident_counts = (
    merged_filled
    .groupby('county')
    .size()
    .reset_index(name='incident_counts')
)
incident_counts['county'] = (
    incident_counts['county']
    .str.replace('-', ' ', regex=False)
    .str.replace('.', '', regex=False)
    .str.strip()
    .str.upper()
)
propdamage_flood_incident_counts = (
    merged_filled[
        (merged_filled['DAMAGE_PROPERTY'] > 0) &
        (
            (merged_filled["EVENT_TYPE"] == "Flood") |
            (merged_filled["EVENT_TYPE"] == "Flash Flood") |
            (merged_filled["EVENT_TYPE"] == "Lakeshore Flood")
        )
    ]
    .groupby('county')
    .size()
    .reset_index(name="propdamage_flood_incident_counts")
)
propdamage_flood_incident_counts['county'] = (
    propdamage_flood_incident_counts['county']
    .str.replace('-', ' ', regex=False)
    .str.replace('.', '', regex=False)
    .str.strip()
    .str.upper()
)
flood_incident_counts = (
    merged_filled[
        (
            (merged_filled["EVENT_TYPE"] == "Flood") |
            (merged_filled["EVENT_TYPE"] == "Flash Flood") |
            (merged_filled["EVENT_TYPE"] == "Lakeshore Flood")
        )
    ]
    .groupby('county')
    .size()
    .reset_index(name="flood_incident_counts")
)
flood_incident_counts['county'] = (
    flood_incident_counts['county']
    .str.replace('-', ' ', regex=False)
    .str.replace('.', '', regex=False)
    .str.strip()
    .str.upper()
)
def mapgraph(df, column, title, color):
    map_data = illinois_map.merge(
        df[["county", column]],
        on="county",
        how='left'
    )
    map_data[column] = map_data[column].fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=(10,10))
    map_data.plot(
        column=column,
        cmap=color,
        linewidth=0.8,
        ax=ax, 
        edgecolor="0.8",
        legend=True
    )
    ax.set_title(title)
    ax.axis("off")
    st.pyplot(fig)

mapgraph(counties, "per_capita_income", "Per Capita Income by County in Illinois", "Greens")
mapgraph(counties, "percent_below_poverty_line", "Percent Below Poverty Line by County in Illinois", "Greens")
mapgraph(counties, "median_housing_value", "Median Housing Value by County in Illinois", "Greens")
mapgraph(counties, "median_household_income", "Median Household Income by County in Illinois", "Greens")
mapgraph(counties, "sqr_miles", "Square Miles by County in Illinois", "Greens")
mapgraph(incident_counts, "incident_counts", "Storm Incidents by County in Illinois", "Reds")
mapgraph(propdamage_incident_counts, "propdamage_incident_counts", "Storm Incidents with Property Damage by County in Illinois", "Reds")
mapgraph(cropdamage_incident_counts, "cropdamage_incident_counts", "Storm Incidents with Crop Damage by County in Illinois", "Reds")
mapgraph(flood_incident_counts, "flood_incident_counts", "Flood Incidents by County in Illinois", "Reds")
mapgraph(propdamage_flood_incident_counts, "propdamage_flood_incident_counts", "Flooding Incidents with Property Damage by County in Illinois", "Reds")






