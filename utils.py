from scipy.spatial.distance import squareform,pdist
import pandas as pd

class Property:
    def __init__(self,max_distance):
        self.MAX_DIST=max_distance
        
    def load_data(self):
        properties=pd.read_csv("resources/data/inversiones.csv")
        
        #Getting basic metrics for all properties
        properties["rentabilidad"]=(properties["renta"])*12/properties["valor_publicado"]*100
        properties["capital_invertido"]=properties["valor_publicado"]*properties["financiado"]
        properties["total_invertido"]=properties["capital_invertido"].cumsum() 
    
        #Important metrics for all properties

        #PAM (Price per square meter)= property price/area
        properties["PAM"]=properties["renta"]/properties["area"]

        #Distance measure using coordinates 
        distance_matrix=pd.DataFrame(squareform(pdist(properties[["latitud","longitud"]])),columns=properties["inmueble"].unique(),index=properties["inmueble"].unique())
        distance_matrix=distance_matrix*100


        #Get close properties list
        close_matrix=pd.eval("distance_matrix<=self.MAX_DIST and distance_matrix>0")
        close_matrix.insert(0,"imueble",close_matrix.index)

        ppam=[]

        for property in close_matrix.index:
            close=close_matrix.loc[[property]]
            close=close.loc[:,(close==True).any()].columns
            close_pam=properties[properties["inmueble"].isin(close)]["PAM"]
            close_pam=close_pam[close_pam>0].mean()
            ppam.append(close_pam)

        #PPAM (Average rent price per square meter) -> Get close properties and average their PAM
        properties["PPAM"]=ppam

        #PEA (Estimated rent price)=built area * PPAM
        properties["PEA"]=properties["PPAM"]*properties["area"]

        #PBN (Brute negotiation price)=(PEA*100)/Monthly desired rentability (percentage)
        properties["PBN"]=properties["PEA"]*100/1.3

        #PMN (Maximum negotiation price)=PBN - closing costs - fix costs - extra costs
        properties["PMN"]=properties["PBN"]-properties["valor_publicado"]*0.02

        #POI (Initial offering price)=PMN-15%
        properties["POI"]=properties["PMN"]-properties["PMN"]*0.15
        
        #metrics for bought properties
        bought=properties[properties["comprado"]==True]
        bought["valor_portafolio"]=bought["valor_publicado"].cumsum()/1000
        
        #PRM (Rent percentage of published value)
        bought["PRM"]=bought["renta"]/bought["valor_publicado"]
        
        #Property rating calculation for future bought
        properties["rent_vs_price"]=properties["PEA"]/properties["valor_publicado"]*100
        properties["offered_vs_published"]=properties["POI"]/properties["valor_publicado"]
        properties["net_rent"]=properties["PEA"]-properties["cuota"]
        properties["property_rating"]=0

        properties.update(properties[properties["rent_vs_price"]*100>1]["property_rating"]+5)
        properties.update(properties[properties["offered_vs_published"]>0.7]["property_rating"]+3)
        properties.update(properties[properties["net_rent"]>0]["property_rating"]+2)

                
        return properties, bought
        