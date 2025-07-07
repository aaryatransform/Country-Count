import streamlit as st
import pycountry
import re


from country_mapping import country_mapping

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
            count = int(parts[0].replace(',', ''))
        except ValueError:
            continue
        for i in range(1, len(parts)):
            if parts[i].endswith("toggle"):
                break
        else:
            continue
        if i > 1:
            location_parts = parts[1:i] + [parts[i][:-len("toggle")].rstrip(',')]
        else:
            location_parts = [parts[i][:-len("toggle")].rstrip(',')]
        location = ' '.join(location_parts).strip()
        cleaned_location = re.sub(r'toggle$', '', location, flags=re.IGNORECASE).strip()
        # Special handling for Türkiye
        if cleaned_location.lower() == "türkiye":
            country_abbr = "Türkiye"
            if country_abbr in country_dict:
                country_dict[country_abbr] += count
            else:
                country_dict[country_abbr] = count
            continue
        try:
            country = pycountry.countries.lookup(cleaned_location)
            country_name = country.name
            country_abbr = country_mapping.get(country_name, country_mapping.get(country_name.lower(), country_name))
            if country_abbr in country_dict:
                country_dict[country_abbr] += count
            else:
                country_dict[country_abbr] = count
        except LookupError:
            # If user input is Türkiye, treat as Turkey for lookup
            if cleaned_location.lower() == "türkiye":
                country_abbr = "Türkiye"
                if country_abbr in country_dict:
                    country_dict[country_abbr] += count
                else:
                    country_dict[country_abbr] = count
                continue
            try:
                fuzzy_matches = pycountry.countries.search_fuzzy(cleaned_location)
                if fuzzy_matches:
                    country_name = fuzzy_matches[0].name
                    country_abbr = country_mapping.get(country_name, country_mapping.get(country_name.lower(), country_name))
                    if country_abbr in country_dict:
                        country_dict[country_abbr] += count
                    else:
                        country_dict[country_abbr] = count
                else:
                    continue
            except LookupError:
                continue
    # Generate output, sorted alphabetically
    output = '; '.join([f"{country}: {count}" for country, count in sorted(country_dict.items()) if count > 0])
    return output if output else "No valid country data found."


st.title("Country Count Extractor")
st.write("Paste your data below in the format 'count location toggle off' (e.g., '2,666 United States toggle off').")
input_data = st.text_area("Input Data:", height=300)
if st.button("Process"):
    if input_data:
        result = process_data(input_data)
        st.write("**Result:**")
        st.code(result, language=None)
    else:
        st.write("Please provide input data.")