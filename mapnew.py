import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from sqlalchemy import create_engine
from datetime import datetime
import sqlite3
# Connect to the SQLite database
from sqlalchemy import inspect

engine = create_engine('mysql+pymysql://root:Mahesh@localhost/phonepe_data')
inspector = inspect(engine)
tables = inspector.get_table_names()
print(tables)

# Set wide layout
st.set_page_config(layout="wide")

# Custom CSS styling
st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #1e0836;
        color: #f2d9ff;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background-color: #1e0836;
        color: #f2d9ff;
    }
    .stSelectbox label, .stSlider label, .stRadio label, .stTextInput label, .stMultiSelect label {
        color: #f2d9ff !important;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #f2d9ff !important;
    }
    .st-bb {
        background-color: #260946 !important;
        color: white !important;
    }
    .stButton>button {
        background-color: #a259ff;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["PhonePe", "Case Studies"])

if section == "PhonePe":
    # Load data
    agg_trans = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/aggregated_transaction.csv")
    agg_user = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/aggregated_user.csv")
    map_trans = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/map_transaction.csv")
    map_user = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/map_user.csv")
    top_trans = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/top_transaction.csv")
    top_user = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/top_user.csv")
    agg_insurance = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/aggregated_insurance.csv")
    map_insurance = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/map_insurance.csv")
    top_insurance = pd.read_csv("C:/Users/mahes/OneDrive/Desktop/PhonePe/.venv/top_insurance.csv")
    st.title("PhonePe Pulse - State-wise Analysis")

    # Create columns for map and category details (opposite to each other)
    col1, col2 = st.columns([1, 2])

    with col1:
        # Map and category logic
        category = st.selectbox("Category", ["Transactions", "Users"])

    with col2:
        years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        year_quarters = [f"{q} {y}" for y in years for q in quarters]
        selected_period = st.selectbox("Period", year_quarters, index=24)

    selected_quarter, selected_year = selected_period.split()
    selected_year = int(selected_year)
    selected_quarter = int(selected_quarter[1])

    # Mapping for states to match GeoJSON
    state_name_mapping = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island',
        'andhra-pradesh': 'Andhra Pradesh',
        'arunachal-pradesh': 'Arunachal Pradesh',
        'assam': 'Assam',
        'bihar': 'Bihar',
        'chandigarh': 'Chandigarh',
        'chhattisgarh': 'Chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra & Nagar Haveli',
        'delhi': 'Delhi',
        'goa': 'Goa',
        'gujarat': 'Gujarat',
        'haryana': 'Haryana',
        'himachal-pradesh': 'Himachal Pradesh',
        'jammu-&-kashmir': 'Jammu & Kashmir',
        'jharkhand': 'Jharkhand',
        'karnataka': 'Karnataka',
        'kerala': 'Kerala',
        'madhya-pradesh': 'Madhya Pradesh',
        'maharashtra': 'Maharashtra',
        'manipur': 'Manipur',
        'meghalaya': 'Meghalaya',
        'mizoram': 'Mizoram',
        'nagaland': 'Nagaland',
        'odisha': 'Odisha',
        'puducherry': 'Puducherry',
        'punjab': 'Punjab',
        'rajasthan': 'Rajasthan',
        'sikkim': 'Sikkim',
        'tamil-nadu': 'Tamil Nadu',
        'telangana': 'Telangana',
        'tripura': 'Tripura',
        'uttar-pradesh': 'Uttar Pradesh',
        'uttarakhand': 'Uttarakhand',
        'west-bengal': 'West Bengal'
    }

    # Load GeoJSON
    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    geojson_data = requests.get(geojson_url).json()

    # Map and display data for selected category
    if category == "Transactions":
        df_trans = agg_trans.groupby('State').agg({
            'transaction_count': 'sum',
            'transaction_amount': 'sum'
        }).reset_index()
        df_trans['State'] = df_trans['State'].str.lower().map(state_name_mapping)

        fig = px.choropleth(
            df_trans,
            geojson=geojson_data,
            locations='State',
            featureidkey='properties.ST_NM',
            color='transaction_amount',
            color_continuous_scale="Purples",
            hover_data=['transaction_count', 'transaction_amount']
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            title="Total Transaction Amount by State",
            margin={"r":0,"t":30,"l":0,"b":0},
            height=600  # Increased map height
        )

        col2.plotly_chart(fig, use_container_width=True)

        # Category details (on the left)
        df_filtered = agg_trans[(agg_trans["Year"] == selected_year) & (agg_trans["Quarter"] == selected_quarter)]
        total_txn = df_filtered["transaction_count"].sum()
        total_amt = df_filtered["transaction_amount"].sum()
        avg_txn_amt = round(total_amt / total_txn) if total_txn else 0

        col1.markdown(f"### {category}")
        col1.markdown(f"**Total transaction count:** `{total_txn:,}`")
        col1.markdown(f"**Total payment value:** `₹{total_amt:,.0f}`")
        col1.markdown(f"**Avg. transaction value:** `₹{avg_txn_amt:,}`")
        
        st.markdown("---")
        st.markdown("### Categories")

        cat_summary = df_filtered.groupby("Transaction_type").agg({
            "transaction_count": "sum",
            "transaction_amount": "sum"
        }).sort_values("transaction_count", ascending=False)

        for idx, row in cat_summary.iterrows():
            st.markdown(f"**{idx}**: `{int(row['transaction_count']):,}`")

    elif category == "Users":
        df_users = map_user.groupby('State').agg({
            'RegisteredUsers': 'sum',
            'AppOpens': 'sum'
        }).reset_index()
        df_users['State'] = df_users['State'].str.lower().map(state_name_mapping)

        fig = px.choropleth(
            df_users,
            geojson=geojson_data,
            locations='State',
            featureidkey='properties.ST_NM',
            color='RegisteredUsers',
            color_continuous_scale="Purples",
            hover_data=['RegisteredUsers', 'AppOpens']
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            title="Registered Users by State",
            margin={"r":0,"t":30,"l":0,"b":0},
            height=600  # Increased map height
        )

        col2.plotly_chart(fig, use_container_width=True)

        # Category details (on the left)
        total_users = df_users["RegisteredUsers"].sum()
        total_app_opens = df_users["AppOpens"].sum()

        col1.markdown(f"### {category}")
        col1.markdown(f"**Total registered users:** `{total_users:,}`")
        col1.markdown(f"**Total app opens:** `{total_app_opens:,}`")

        st.markdown("### View Level")
        view_level = st.radio("Select view", ["States", "Districts"], horizontal=True)

        if view_level == "States":
            state_list = df_users['State'].dropna().unique()
            st.markdown("### Top 10 States")
            top_states = df_users.groupby("State")["RegisteredUsers"].sum().sort_values(ascending=False).head(10)
            for idx, val in top_states.items():
                st.markdown(f"**{idx}**: `{val:,}`")

        elif view_level == "Districts":
            state_list = df_users['State'].dropna().unique()
            state = st.selectbox("Select State", sorted(state_list))
            st.markdown(f"### Top 10 Districts")
            top_districts = df_users[df_users['State'] == state].groupby("State")["RegisteredUsers"].sum().sort_values(ascending=False).head(10)
            for idx, val in top_districts.items():
                st.markdown(f"**{idx}**: `{val:,}`")

elif section == "Case Studies":
    st.title("Case Studies")
    #st.markdown("Explore case studies on PhonePe transaction and user data.")
    case_study = st.selectbox("Select a Case Study", [
        '1. Decoding Transaction Dynamics on PhonePe',
        '2. Device Dominance and User Engagement Analysis',
        '3. Insurance Penetration and Growth Potential Analysis',
        '4. Transaction Analysis for Market Expansion',
        '5. User Engagement and Growth Strategy',
        '6. Insurance Engagement Analysis',
        '7. Transaction Analysis Across States and Districts',
        '8. User Registration Analysis',
    ])
    query_map = {
        '1. Decoding Transaction Dynamics on PhonePe': [
            ("Total Transactions and Amount by State", 
             "SELECT state, SUM(transaction_count) AS total_transactions, SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY state ORDER BY total_amount DESC ;", ["bar", "pie"]),
            ("Transaction Trends by Year and Quarter", 
             "SELECT year, quarter, SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY year, quarter ORDER BY year, quarter;", ["line","area","heatmap","bar"]),
            ("Payment Category Analysis", 
             "SELECT Transaction_type, SUM(transaction_count) AS total_transactions, SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY Transaction_type ORDER BY total_amount DESC;", ["pie","bar","treemap"]),
            ("Top Pincodes by Transaction Amount",
              "SELECT Metric_type AS Pincode, SUM(Metric_amount) AS Total_Transaction_Amount FROM top_transaction WHERE Level = 'Pincode' GROUP BY Metric_type ORDER BY Total_Transaction_Amount DESC LIMIT 10;", ["pie","bar"]),
        ],
        '2. Device Dominance and User Engagement Analysis': [
            ("Total Registered Users and App Opens by District ,Year", 
             "SELECT District,Year,SUM(RegisteredUsers) AS total_registered_users,SUM(AppOpens) AS total_app_opens FROM  map_user GROUP BY District,Year ORDER BY total_registered_users DESC LIMIT 30;", ["pie", "bar"]),
            ("Top Users by Registered Users", 
             "SELECT State,Year,Quarter,SUM(RegisteredUsers) AS Total_Registered_Users FROM top_user GROUP BY State, Year, Quarter ORDER BY Total_Registered_Users DESC ;", ["bar","pie"]),
        ],
        '3. Insurance Penetration and Growth Potential Analysis': [
            ("Insurance Penetration and Growth Potential Analysis", 
             "SELECT ai.state,SUM(ai.transaction_amount) AS total_insurance_premium,COUNT(DISTINCT ai.transaction_type) AS total_transaction_types,SUM(at.transaction_amount) AS total_transaction_amount,COUNT(DISTINCT at.transaction_type) AS total_transactions FROM aggregated_insurance ai JOIN  aggregated_transaction at ON ai.state = at.state WHERE ai.transaction_amount > 0 GROUP BY ai.state ORDER BY total_insurance_premium DESC;", ["pie","scatter"])
        ],
        '4. Transaction Analysis for Market Expansion': [
            ("Transaction Volume and Value by State", 
             "SELECT state,SUM(transaction_amount) AS total_transaction_value,COUNT(*) AS total_transactions FROM  aggregated_transaction GROUP BY state ORDER BY total_transaction_value DESC;", ["scatter"]),
            ("User Growth in Each State", 
             "SELECT State, SUM(RegisteredUsers) AS total_users FROM map_user GROUP BY State ORDER BY total_users DESC;", ["bar","pie","scatter"]),
            ("Transaction Type Trends", 
             "SELECT state,transaction_type,COUNT(*) AS transaction_count, SUM(transaction_amount) AS total_transaction_value FROM aggregated_transaction GROUP BY state, transaction_type ORDER BY total_transaction_value DESC;", ["pie","scatter","heatmap"]),
        ],
        '5. User Engagement and Growth Strategy': [
            ("Total User Engagement per State ", 
             "SELECT State, Year, Quarter,SUM(Aggregated_count) AS total_engagement FROM aggregated_user GROUP BY State, Year, Quarter ORDER BY total_engagement DESC;", ["pie","heatmap","scatter"]),
            ("Insurance Adoption by State", 
             "SELECT State, SUM(transaction_count) AS total_insurance_adoption FROM aggregated_insurance WHERE Transaction_type = 'insurance' GROUP BY State ORDER BY total_insurance_adoption DESC;", ["pie","heatmap"]),
            ("Top Users by Transaction Volume", 
             "SELECT State, SUM(transaction_count) AS total_transaction_count FROM aggregated_transaction GROUP BY State ORDER BY total_transaction_count DESC;", ["bar","pie"]),
        ],
        '6. Insurance Engagement Analysis': [
            ("Total Insurance Transactions by State", 
             "SELECT State, SUM(transaction_count) AS total_transactions, SUM(transaction_amount) AS total_amount FROM aggregated_insurance GROUP BY State;", ["bar","scatter"]),
            ("Insurance Transaction Trends (Year and Quarter)", 
             "SELECT Year, Quarter, SUM(transaction_count) AS total_transactions, SUM(transaction_amount) AS total_amount FROM aggregated_insurance GROUP BY Year, Quarter ORDER BY Year, Quarter;", ["bar","heatmap"]),
            ("Total Number of Users Engaging in Insurance by State", 
             "SELECT State, SUM(Aggregated_count) AS total_users_engaged FROM aggregated_user GROUP BY State;", ["line","bar"]),
            ("User Engagement Over Time (Year and Quarter)", 
             "SELECT Year, Quarter, SUM(Aggregated_count) AS total_users_engaged FROM aggregated_user GROUP BY Year, Quarter ORDER BY Year, Quarter;", ["area","scatter"]),
        ],
        '7. Transaction Analysis Across States and Districts': [
            ("Total Transaction Amount by State", 
             "SELECT State,SUM(Metric_count) AS total_transactions,SUM(Metric_amount) AS total_amount FROM map_transaction GROUP BY State ORDER BY total_amount DESC LIMIT 10;", ["bar","pie"]),
            ("Total Transaction Amount by PinCodes", 
             "SELECT State,Level AS Pincode,SUM(Metric_count) AS total_transactions,SUM(Metric_amount) AS total_amount FROM top_transaction GROUP BY State, Pincode ORDER BY total_amount DESC;", ["bar","pie"]),
        ],
        '8. User Registration Analysis': [
            ("Top Year,Quarter by Registered Users", 
             "SELECT Year,Quarter,State,SUM(RegisteredUsers) AS total_registered_users FROM top_user GROUP BY Year, Quarter, State ORDER BY Year, Quarter,State, total_registered_users DESC;", ["scatter"]),
        ],
    }
    suboptions = query_map.get(case_study, [])

    if suboptions:
        sub_choice_label = st.selectbox("Choose a sub-topic", [s[0] for s in suboptions])
        selected_query, supported_charts = [(s[1], s[2]) for s in suboptions if s[0] == sub_choice_label][0]       
        # Execute the modified query
        try:
            df = pd.read_sql_query(selected_query, con=engine)
            st.subheader(sub_choice_label)
            #st.dataframe(df)

            # Let user pick a chart type (from allowed types)
            chart_type = st.radio("Choose chart type", supported_charts, horizontal=True)

            # Display corresponding chart based on the selected chart type
            if chart_type == "bar":
                fig = px.bar(df, x=df.columns[0], y=df.columns[-1], title=sub_choice_label)
                st.plotly_chart(fig)

            elif chart_type == "pie":
                fig = px.pie(df, names=df.columns[0], values=df.columns[-1], hole=0.4, title=sub_choice_label)
                st.plotly_chart(fig)
            elif chart_type == "area":
                    fig = px.area(df, x=df.columns[0], y=df.columns[-1], title=sub_choice_label)
                    st.plotly_chart(fig)
            elif chart_type == "scatter":
                    fig = px.scatter(df, x=df.columns[0], y=df.columns[1], size=df.columns[-1], color=df.columns[0], title=sub_choice_label)
                    st.plotly_chart(fig)
            elif chart_type == "treemap":
                fig = px.treemap(df, path=[df.columns[0]], values=df.columns[-1], title=sub_choice_label)
                st.plotly_chart(fig)
            elif chart_type == "sunburst":
                fig = px.sunburst(df, path=[df.columns[0]], values=df.columns[-1], title=sub_choice_label)
                st.plotly_chart(fig)
            elif chart_type == "heatmap":
                fig = px.density_heatmap(df, x=df.columns[0], y=df.columns[1], z=df.columns[-1], title=sub_choice_label)
                st.plotly_chart(fig)


            elif chart_type == "line":
                if "quarter" in df.columns and "year" in df.columns:
                    df["time"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
                    fig = px.line(df, x="time", y=df.columns[-1], title=sub_choice_label)
                else:
                    fig = px.line(df, x=df.columns[0], y=df.columns[-1], title=sub_choice_label)
                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Failed to execute query: {e}")





