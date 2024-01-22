import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
import streamlit as st

def create_dayUser(df):
    dayUser_df = df.groupby(by="workingday").cnt.sum().reset_index()
    dayUser_df.workingday.replace(1, "Working Day", inplace=True)
    dayUser_df.workingday.replace(0, "Holiday", inplace=True)
    
    return dayUser_df

def create_season_df(df):
    season_df = df.groupby(by="season").cnt.sum().reset_index()
    season_df.season.replace(1, "Spring", inplace=True)
    season_df.season.replace(2, "Summer", inplace=True)
    season_df.season.replace(3, "Fall", inplace=True)
    season_df.season.replace(4, "Winter", inplace=True)
    
    return season_df

def create_weather_df(df):
    weather_df = df.groupby(by="weathersit").cnt.sum().reset_index()
    weather_df.weathersit.replace(1, "Clear", inplace=True)
    weather_df.weathersit.replace(2, "Mist/Cloudy", inplace=True)
    weather_df.weathersit.replace(3, "Light Snow/Rain", inplace=True)
    weather_df.weathersit.replace(4, "Heavy Rain/Ice Pallets", inplace=True)
    
    return weather_df

def create_temp_df(df):
    # pengaruh suhu terhadap banyaknya penyewa sepeda?
    temp_df = df.groupby(by="temp").cnt.sum().reset_index()
    # mengalikan temp dengan 41 agar mendapatkan nilai sesungguhnya dan dibulatkan
    temp_df["temp"] = temp_df["temp"].apply(lambda x: x * 41).round(1)
    
    return temp_df

def create_rfm_df(df):
    # Parameter RFM
    rfm_df = df.groupby(by="instant", as_index=False).agg({
        "dteday": "max",    # mengambil tanggal order terakhir
        "cnt": "sum"
    })
    rfm_df.columns = ["ID", "max_order_timestamp", "frequency"]
    # menghitung kapan terakhir pelanggan melakukan transaksi [hari]
    rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    df["dteday"] = pd.to_datetime(df["dteday"])
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    # menghapus kolom max_order_timestamp karena sudah tidak dibutuhkan
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


main_df = pd.read_csv("final.csv")

# memanggil helper function
dayUser_df = create_dayUser(main_df)
season_df = create_season_df(main_df)
weather_df = create_weather_df(main_df)
temp_df = create_temp_df(main_df)
rfm_df = create_rfm_df(main_df)
    
    
with st.sidebar:
    # Menambahkan logo
    st.header("PedalEase Rentals")
    
    st.image("https://i.pinimg.com/564x/86/11/b4/8611b41eb22b6b594975263523441cf0.jpg")
    
    st.header("Company Description")
    st.subheader("Welcome, We are the modern solution for your cycling adventures!As pioneers in the online bike rental industry, we are committed to providing an unforgettable riding experience for our customers. With a variety of high-quality bikes and user-friendly services, we make it easy for you to explore your favorite destinations without the need to own a bike yourself")
    
    
    # mengatur "dteday" akan diatur sebagai kolom tanggal-waktu
    datetime_columns = ["dteday"]
    # mengurutkan amain_df berdasarkan kolom dteday secara ascending
    main_df.sort_values(by="dteday", inplace=True)
    # mengatur ulang indeks data frame untuk memastikan indeks menjadi urutan numerik default
    main_df.reset_index(inplace=True)    #inplace=True mengaplikasikan peruahan langsung pada dataframe
    # mengonversi nilai nilai dalam kolom yang terdaftar dalam "datetime_columns" ke tipe data datetime

    for column in datetime_columns:
        main_df[column] = pd.to_datetime(main_df[column])
  
    min_date = main_df["dteday"].min()
    max_date = main_df["dteday"].max()

    st.subheader("Time Range")
    # Mengambil start date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Date", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    # kode di atas akan membatasi rentang date time yang bisa dipilih oleh user
    
    # pada fungsi sidebar di atas akan menjadi filter order_date pada dataframe utama
    main_df = main_df[(main_df["dteday"] >= str(start_date)) & (main_df["dteday"] <= str(end_date))]


st.header("PedalEase Rentals Dashboard Analytic") 

st.subheader("The total orders from user")

col1, col2, col3 = st.columns(3)

with col1:
    # Total casual users renting.
    casual_user = main_df.casual.sum()
    st.metric("The total orders from casual users", value=casual_user)

with col2:
    # Total registered users renting.
    registered_user = main_df.registered.sum()
    st.metric("The total orders from registered users", value=registered_user)
    
with col3:
    total_user = main_df.cnt.sum()
    st.metric("The total orders from users", value=total_user)
    
# paling banyak sepeda akan disewa ketika hari libur atau hari kerja?
st.subheader("Number of rented bikes on weekends and holidays")

fig, ax = plt.subplots(figsize=(20, 13))
colors=["#004c6d", "#346888"]
# convert to million
dayUser_df["cnt"] = dayUser_df["cnt"].apply(lambda x: x / 1e6)

sns.barplot(
    x="workingday",
    y="cnt",
    data=dayUser_df.sort_values(by="cnt", ascending=False),
    hue="workingday",
    palette=colors,
    ax=ax)
ax.bar_label(ax.containers[0], fmt='%.2f million', fontsize=25)
ax.bar_label(ax.containers[1], fmt='%.2f million', fontsize=25)
ax.set_ylabel("In million", fontsize=30)
ax.set_xlabel(None)
ax.tick_params(axis="x", labelsize=30)
ax.tick_params(axis="y", labelsize=20)
st.pyplot(fig)


# pada musim apa sepeda paling banyak disewa dan pada musim apa sepeda paling sedikit disewa
st.subheader("Season are bikes most frequently rented")
dayUser_df["cnt"] = dayUser_df["cnt"].apply(lambda x: x / 1e6)

fig, ax = plt.subplots(figsize=(20, 13))
colors = ["#004c6d", "#346888", "#5886a5", "#7aa6c2"]
# convert to million
season_df["cnt"] = season_df["cnt"].apply(lambda x: x / 1e6)

sns.barplot(
    y="cnt",
    x="season",
    data=season_df.sort_values(by="cnt", ascending=False),
    hue="season",
    palette=colors,
    ax=ax
)
ax.bar_label(ax.containers[0], fmt='%.2f million', fontsize=25)
ax.bar_label(ax.containers[1], fmt='%.2f million', fontsize=25)
ax.bar_label(ax.containers[2], fmt='%.2f million', fontsize=25)
ax.bar_label(ax.containers[3], fmt='%.2f million', fontsize=25)
ax.set_xlabel("Season", fontsize=30)
ax.set_ylabel("In million", fontsize=30)
ax.tick_params(axis="y", labelsize=30)
ax.tick_params(axis="x", labelsize=20)
st.pyplot(fig)


# pada cuaca apa sepeda paling banyak disewa dan pada musim apa sepeda paling sedikit disewa?
st.subheader("Weather are bikes most frequently rented")
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 13))
colors = ["#004c6d", "#346888", "#5886a5"]
# convert to million
weather_df["cnt"] = weather_df["cnt"].apply(lambda x: x / 1e6)

sns.barplot(
    y="cnt",
    x="weathersit",
    data=weather_df.sort_values(by="cnt", ascending=False),
    palette=colors,
    hue="weathersit",
    ax=ax
)
ax.bar_label(ax.containers[0], fmt='%.2f million', fontsize=25)
ax.bar_label(ax.containers[1], fmt='%.2f million', fontsize=25)
ax.bar_label(ax.containers[2], fmt='%.2f million', fontsize=25)
ax.set_xlabel("Weather", fontsize=30)
ax.set_ylabel("In million", fontsize=30)
ax.tick_params(axis="y", labelsize=30)
ax.tick_params(axis="x", labelsize=20)
st.pyplot(fig)


# pengaruh suhu terhadap banyaknya penyewa sepeda?
st.subheader("The effect of temperature on tenants")
    
# convert to million
temp_df["cnt"] = temp_df["cnt"].apply(lambda x: x / 1e6)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 13))
sns.histplot(data=temp_df, x="temp", kde=True, ax=ax, bins=40, color='#5886a5', line_kws={'color': '#346888'})
ax.tick_params(axis="y", labelsize=30)
ax.tick_params(axis="x", labelsize=20)
ax.set_ylabel(None)
ax.set_xlabel("Temp in Celcius", fontsize=30)
st.pyplot(fig)


# RFM Analysis
st.subheader("RFM Analysis")

col1, col2 = st.columns(2)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
    
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 15))
colors=["#004c6d", "#004c6d", "#004c6d", "#004c6d", "#004c6d"]
sns.barplot(
    y="recency",
    x="ID",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=colors,
    hue="ID",
    ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("ID", fontsize=25)
ax[0].set_title("By Recency (Days)", loc="center", fontsize=40)
ax[0].tick_params(axis="x", labelsize=25)
ax[0].tick_params(axis="y", labelsize=25)

sns.barplot(
    y="frequency",
    x="ID",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=colors,
    hue="ID",
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("ID", fontsize=25)
ax[1].set_title("By Frequency", loc="center", fontsize=40)
ax[1].tick_params(axis="x", labelsize=25)
ax[1].tick_params(axis="y", labelsize=25)

st.pyplot(fig)




