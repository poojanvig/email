import streamlit as st
import requests
import pandas as pd

import base64

# Function to create a download link for CSV
def create_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Encode to base64
    href = f'<a href="data:file/csv;base64,{b64}" download="leads.csv">Download Leads as CSV</a>'
    return href

def get_leads(data):
    url = "https://api.apollo.io/v1/mixed_people/search"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, json=data)
    response_json = response.json()
    people_details = response_json['people']
    extracted_data = []

    for person in people_details:
        individual_data = {
            'Full Name': person['name'],
            'Email': person['email'],
            'LinkedIn URL': person['linkedin_url'],
            'Title': person['title'],
            'Organization Name': person['organization']['name'],
            'Website URL': person['organization']['website_url'],
            'Phone': person['organization'].get('account', {}).get('primary_phone', {}).get('number', None),
            'City': person['city'],
            'State': person['state'],
            'Country': person['country'],
            'Departments': ', '.join(person['departments']),
        }
        extracted_data.append(individual_data)

    return pd.DataFrame(extracted_data)

st.title('Lead Generation Tool')

api_key = st.text_input('Enter API Key')
page = st.number_input('Enter Page Number', min_value=1, value=1)
person_titles = st.text_area('Enter Person Titles (comma-separated)')
# country = st.text_input('Enter Country')
# state = st.text_input('Enter State')

if st.button('Generate Leads'):
    data = {
        "api_key": api_key,
        "page": page,
        "person_titles": person_titles.split(','),
        # "country": cou÷÷ntry,
        # "state": state,
    }
    leads_df = get_leads(data)
    st.dataframe(leads_df)
     # Create and display the download link
    st.markdown(create_download_link(leads_df), unsafe_allow_html=True)
'jAkdjgnA1MEl6Ra9YvlpIw'