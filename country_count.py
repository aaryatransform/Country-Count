import streamlit as st
import pycountry
import re

# Country name mapping for abbreviations
country_mapping = {
    "United States": "US",
    "United Kingdom": "UK",
    "United Arab Emirates": "UAE"
}

# Incomplete names mapping
incomplete_names = {
    "United": "United States",
    # Add more if needed
}

def process_data(data):
    lines = data.strip().split('\n')
    country_dict = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            count = int(parts[0])
        except ValueError:
            continue
        # Find index where part ends with "toggle"
        for i in range(1, len(parts)):
            if parts[i].endswith("toggle"):
                break
        else:
            continue  # No "toggle" found
        # Extract location parts
        if i > 1:
            location_parts = parts[1:i] + [parts[i][:-len("toggle")].rstrip(',')]
        else:
            location_parts = [parts[i][:-len("toggle")].rstrip(',')]
        location = ' '.join(location_parts).strip()
        if not location:
            continue
        # Check for incomplete names
        if location in incomplete_names:
            location = incomplete_names[location]
        # Try to look up the country
        try:
            country = pycountry.countries.lookup(location)
            country_name = country.name
            if country_name in country_mapping:
                country_abbr = country_mapping[country_name]
            else:
                country_abbr = country_name
            # Add to dictionary
            if country_abbr in country_dict:
                country_dict[country_abbr] += count
            else:
                country_dict[country_abbr] = count
        except LookupError:
            continue  # Not a country
    # Generate output
    output = '; '.join([f"{country}: {count}" for country, count in country_dict.items() if count > 0])
    return output if output else "No valid country data found."

# Streamlit UI
st.title("Country Count Extractor")
st.write("Paste your data below in the format 'count location toggle off' (e.g., '316 United States toggle off').")
input_data = st.text_area("Input Data:", height=300)
if st.button("Process"):
    if input_data:
        result = process_data(input_data)
        st.write("**Result:**")
        st.code(result, language=None)  # Streamlit's code block includes a copy button
    else:
        st.write("Please provide input data.")