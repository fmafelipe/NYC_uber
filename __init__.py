#Ejemplo de como mostrar datos geograficos 

import pandas as pd 
import streamlit as st 
import numpy as np 
import altair as alt
import pydeck as pdk


st.set_page_config(layout="wide",page_title="Viajes compartidos uber", page_icon="👹")
#st.title("🚙 Viajes compartidos de uber en New York") 

# Cargar datos 
@st.experimental_singleton
def load_data():
    data = pd.read_csv('uber-raw-data-sep14.csv.gz', nrows=100000, names=["date/time","lat","lon"],
                       skiprows=1,usecols=[0,1,2], parse_dates=["date/time"])
    
    return data


# Funcion para mapas de aeropueto 

def map(data,lat,lon,zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude" : lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch":50
                },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data = data,
                    get_position = ["lon","lat"],
                    radius = 100,
                    elevation_scale= 4,
                    pickable = True,
                    extruded = True
                    )
                ]
            )
        
        )
    
    
    
# Filtrar datos para una hora especifica, cache 
@st.experimental_memo
def filterdata (df,hour_selected):
    return df[df['date/time'].dt.hour == hour_selected]
    

# calcular punto medio oara los datos
@st.experimental_memo
def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))

# filtrar datos por hora para el histograma
@st.experimental_memo
def histdata(df, hr):
    filtered = data[
        (df["date/time"].dt.hour >= hr) & (df["date/time"].dt.hour < (hr + 1))
    ]
    
    hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0,60))[0]
    
    return pd.DataFrame({"minute": range(60), "pickups": hist})

# Diseño de la aplicacion 

data = load_data()

# Diseño de la parte superior de la app
row1_1, row1_2 = st.columns((2, 3))


# Ver si se puede pasar la url con hora especifica
if not st.session_state.get("url_synced", False):
    try:
        pickup_hour = int(st.experimental_get_query_params()["pickup_hour"][0])
        st.session_state["pickup_hour"] = pickup_hour
        st.session_state["url_synced"] = True
    except KeyError:
        pass
    
# si los sliders cambian, actualizar los parametros

def update_query_params():
    hour_selected = st.session_state["pickup_hour"]
    st.experimental_set_query_params(pickup_hour=hour_selected)
    
    
with row1_1:
    st.title("NYC Uber Ridesharing Data")
    hour_selected = st.slider(
        "Select hour of pickup", 0, 23, key="pickup_hour", on_change=update_query_params
    )
    
with row1_2:
    st.write(
        """
    ##
    Examining how Uber pickups vary over time in New York City's and at its major regional airports.
    By sliding the slider on the left you can view different slices of time and explore different transportation trends.
    """
    )

# Diseño de columnas para la eccion del medio de los mapas 
row2_1, row2_2, row2_3, row2_4 = st.columns((2, 1, 1, 1))


# Configurando coordenadas y zoom para los mapas de aeropuertos

la_guardia = [40.7900, -73.8700]
jfk = [40.6650, -73.7821]
newark = [40.7090, -74.1805]
zoom_level = 12
midpoint = mpoint(data["lat"], data["lon"])


# Ploteando todos los mapas 

with row2_1:
    st.write(
        f"""**Toda la ciudad de New York {hour_selected}:00 and {(hour_selected + 1) % 24}:00**"""
    )
    map(filterdata(data, hour_selected), midpoint[0], midpoint[1], 11)

with row2_2:
    st.write("**Aeropuerto La Guardia **")
    map(filterdata(data, hour_selected), la_guardia[0], la_guardia[1], zoom_level)

with row2_3:
    st.write("**Aeropuerto JFK**")
    map(filterdata(data, hour_selected), jfk[0], jfk[1], zoom_level)

with row2_4:
    st.write("**Aeropuerto Newark**")
    map(filterdata(data, hour_selected), newark[0], newark[1], zoom_level)


# datos de histograma 

chart_data = histdata(data, hour_selected)

# mostrando seccion del histograma

st.write(f'''Especificacion de los viajes entre {hour_selected}:00 y {(hour_selected+1)%24}:00 ''')

st.bar_chart(chart_data['pickups'])








    
