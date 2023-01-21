import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from importlib import reload
import pydeck as pdk
from utils import Property

properties,bought=Property(150).load_data()

#Map images
HOUSE="https://upload.wikimedia.org/wikipedia/commons/b/bc/House_image_icon.png"
OPORTUNITY="https://upload.wikimedia.org/wikipedia/commons/8/8b/Light-bulb.png"

#Map styles
bought_icon_data={
      'url':HOUSE,
      'width':20,
      'height':20,
      'anchorY':20
    }
    
oportunity_icon_data={
    'url':OPORTUNITY,
    'width':20,
    'height':20,
    'anchorY':20
}
    
properties["icon_data"]=None

#Bought vs opportunity map
st.header("Gestor de Real Estate")
st.subheader("Mapa")
     
if len(properties)==0:
    st.info("No hay properties registrados en este momento")
else:   
    if len(properties) >= 10:
         view = pdk.data_utils.compute_view(properties[["longitud", "latitud"]], 0.9)
    else: 
        view = pdk.ViewState(longitude=max(properties['longitud']),
        latitude=max(properties['latitud']), zoom=4)
    
    
    
    for i in properties.index:
        properties['icon_data'][i]=bought_icon_data if properties["comprado"][i]==True else oportunity_icon_data
        
    icon_layer=pdk.Layer(
        type="IconLayer",
        data=properties,
        get_icon="icon_data",
        get_size=4,
        size_scale=15,
        get_position=["longitud","latitud"],
        pickable=True
    )
    
r=pdk.Deck(layers=[icon_layer])
st.pydeck_chart(r,use_container_width=True)

#Total portfolio value (bought properties)
st.header("Portafolio")
st.metric(label="Capital invertido", value="$ "+str(int(properties["capital_invertido"].sum())))
st.metric(label="Porcentaje alquiler/precio",value=round(bought["PRM"].mean(),3)*100)
col1,col2=st.columns(2)

#EAR of bought properties
with col1:    
    st.metric(label="Tasa promedio (E.A)", value=str(round(bought["rentabilidad"].mean(),5))+" %")
    
    st.subheader("Capital por inmueble")
    fig=px.histogram(bought[["inmueble","fecha_compra","capital_invertido"]],x="fecha_compra",y="capital_invertido",color="inmueble")
    st.plotly_chart(fig,use_container_width=True)
    
#Net rent
with col2:
    net_rent=(bought["renta"]-bought["cuota"]).sum()
    
    st.metric(label="Rentabilidad neta mensual", value=net_rent)
    fig=px.line(bought[["fecha_compra","rentabilidad"]],x="fecha_compra",y="rentabilidad",markers=True)
    fig.update_layout({
    'plot_bgcolor':'rgb(0,0,0)'
})
    st.subheader("Rentabilidad de los properties")
    st.plotly_chart(fig,use_container_width=True)

fig=px.line(bought[["fecha_compra","valor_portafolio"]],x="fecha_compra",y="valor_portafolio",markers=True)
fig.update_traces(line_color="rgb(255,255,255)")
fig.update_layout({
    'plot_bgcolor':'rgb(0,0,0)'
})

#Chart of property value over time
st.subheader("Valor del portafolio en el tiempo (miles de pesos)")
st.write(fig)

#Table with filtered properties
st.subheader("Portafolio")
seleccion=bought[["valor_publicado","inmueble","financiado","renta","fecha_compra","cuota","PAM"]]
max_price=st.slider("Precio Maximo (decenas de millones)")

if max_price:
    st.table(seleccion[seleccion["valor_publicado"] < int(max_price)*10000000])
else:
    st.table(seleccion)
