import streamlit as st
import requests

st.title("AI Assistant streamlit App")

tab1, tab2 = st.tabs(["OpenWeather API", "Dad Jokes Generator"])

import dotenv
import os
dotenv.load_dotenv()
api_key = os.getenv("APIkey")

with tab1:
    st.header("Get Weather Data")
    city = st.text_input("City Name", key="city")
    
    if st.button("Get Weather"):
        if city and api_key:
            print(api_key)
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                st.json(data)
                # Optionally parse and display key info
                st.write(f"Location: {data.get('name', 'Unknown')}")
                st.write(f"Temperature: {data['main']['temp']} K")
                st.write(f"Weather: {data['weather'][0]['description']}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        else:
            st.error("Please fill all fields")

with tab2:
    st.header("Search Dad Jokes")
    term = st.text_input("Search Term (put one word to search)", key="term")
    
    if st.button("Search Jokes"):
        params = {}
        if term:
            params["term"] = term
        headers = {"Accept": "application/json"}
        url = "https://icanhazdadjoke.com/search"
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            jokes = data.get("results", [])
            if jokes:
                for joke in jokes:
                    st.write(joke["joke"])
                    st.divider()
            else:
                st.write("No jokes found.")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")