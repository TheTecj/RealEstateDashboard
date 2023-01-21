import streamlit as st
import pandas as pd
from scipy.spatial.distance import squareform,pdist
from utils import Property

properties,bought=Property(150).load_data()

#Filter sidebar
with st.sidebar:
    st.title("Filtros avanzados")
    
    st.markdown("*Tipo de inmueble*")
    bought=st.checkbox("Comprados")
    not_bought=st.checkbox("No Comprados")
    
    #Property type fileter (bought or not bought)
    if bought and not not_bought:
        properties=bought
        
    if not_bought and not bought:
        properties=properties[properties["comprado"]==False]
    
    st.markdown("*Precio maximo (decenas de millones)*")
    
    #Max price filter
    max_price=st.slider("")
    
    if max_price:
        properties=properties[properties["valor_compra"]<=int(max_price)*10000000]
    
    properties["fecha_compra"]=pd.to_datetime(properties["fecha_compra"])
    
    #Bought date filter
    bought_date_filter=st.checkbox("Filtrar por fecha de compra")

    if bought_date_filter:
      bought_date=st.date_input("Fecha de compra").strftime('%d/%m/%Y')
      properties=properties.loc[(properties["fecha_compra"]==bought_date)]

    registered_date_filter=st.checkbox("Filtrar por fecha de registro")
    
    #Registered date filter
    if registered_date_filter:
      register_date=st.date_input("Fecha de registro").strftime('%d/%m/%Y')
      properties=properties.loc[(properties["fecha_registro"]==register_date)]


#Selectbox to pick the property to analyze
selected=st.selectbox(label="Selecciona uno de tus inmuebles",options=properties["inmueble"])
selected=properties[properties["inmueble"]==selected]

st.title("Métricas para inmuebles especificos")

#Property quality rating
property_rating=0

rent_vs_price=selected["PEA"]/selected["valor_publicado"]*100
offered_vs_published=selected["POI"]/selected["valor_publicado"]
net_rent=selected["PEA"]-selected["cuota"]

if rent_vs_price.iloc[0]*100>1:
    property_rating+=5

if offered_vs_published.iloc[0]>0.7:
    property_rating+=3 

if net_rent.iloc[0]>0:
    property_rating+=2

if property_rating>7:
    score_color="green"
elif property_rating>=5:
    score_color="orange"
else:
    score_color="red"
 
score=f"""
<p>Calificacion del inmueble:</p>
<h1 style="color:{score_color}">{property_rating}</h1>
"""
st.markdown(score,unsafe_allow_html=True)
    
col1,col2=st.columns(2)

with col1:
    #Metrics for opportunities (not bought)
    if selected["comprado"].iloc[0]==False:
        st.metric(label="Porcentaje mensual estimado alquiler/Precio", value=selected["PEA"]/selected["valor_publicado"]*100)
        st.metric(label="Valor publicado",value=selected["valor_publicado"])
        st.metric(label="Precio de oferta inicial",value=selected["POI"])
        st.metric(label="Precio Maximo de negociacion",value=selected["PMN"])
    #Metrics for owned properties
    else:
        st.metric(label="Porcentaje mensual alquiler/Precio", value=selected["renta"]/selected["valor_compra"]*100)
        st.metric(label="Valor recomendado arriendo",value=selected["PEA"]+selected["PEA"]*0.1)
                
with col2:
    #Metrics for opportunities (not bought)
    if selected["comprado"].iloc[0]==False:
        st.metric(label="Renta neta mensual estimada(Quitando gastos fijos)", value=selected["PEA"]-selected["cuota"])
    #Metrics for owned properties
    else:
        st.metric(label="Rentabilidad neta mensual(Quitando gastos fijos)", value=selected["renta"]-selected["cuota"])
        st.metric(label="Valor del PAM vs propiedades cercanas", value=selected["PAM"]-selected["PPAM"])


st.metric(label="Area", value=selected["area"])

#Historical data of the property (owned)
if selected["comprado"].iloc[0]==True:
    st.subheader("Informacion historica del inmueble")
    st.metric(label="Renta Bruta", value=selected["renta"])
    st.metric(label="Fecha compra", value=selected["fecha_compra"].iloc[0].strftime('%Y-%m-%d'))
    st.metric(label="Valor compra", value=selected["valor_compra"])
    
#Filtered properties table
st.markdown("*Propiedades similares*")
st.table(properties)