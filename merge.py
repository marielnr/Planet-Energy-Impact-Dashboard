import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from urllib import parse
import requests
import matplotlib.pyplot as plt
import pycountry #esta libreria pasa de iso a country name
# Función para coordenadas
#json true devuelve la respuesta completa de la api
#return_bb so es true devuelve el bounding box (caja delimitadora) de la ubicacion
"""def get_coordinates(address, return_json=False, return_bb=False):
    '''Get lat-long for a given address
    SRC : https://stackoverflow.com/questions/25888396/how-to-get-latitude-longitude-with-python'''
    
    response = requests.get('https://nominatim.openstreetmap.org/search/' + parse.quote(address) + '?format=json')
    #parse.quote codifica la cadena contenida en address para que sea un componente valido de URL
    resp = response.json()
    
    if return_json:
        return resp
    
    if return_bb:
        return [(float(resp[0]['boundingbox'][i]), float(resp[0]['boundingbox'][i+2])) for i in range(len(resp[0]['boundingbox'])//2)]
    
    return (float(resp[0]['lat']), float(resp[0]['lon']))
"""
energy = pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/owid-energy-data.csv')
energy = energy[
    (energy['year'] == 2001) | 
    (energy['year'] == 2005) | 
    (energy['year'] == 2010) | 
    (energy['year'] == 2015) | 
    (energy['year'] == 2020) | 
    (energy['year'] == 2024)
][['country', 'energy_per_capita','year']].rename(columns={'country': 'Country', 'energy_per_capita': 'Energy'})

life_exp = pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/life-expectancy.csv')

life_exp = life_exp[
    (life_exp['Year'] == 2001) |
    (life_exp['Year'] == 2005) |
    (life_exp['Year'] == 2010) |
    (life_exp['Year'] == 2015) |
    (life_exp['Year'] == 2020) |
    (life_exp['Year'] == 2024)
][['Entity', 'Period life expectancy at birth','Year']].rename(columns={'Entity': 'Country', 'Period life expectancy at birth': 'LifeExp','Year':'year'})

gdp = pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/gdp-per-capita-worldbank.csv')
gdp = gdp[
    (gdp['Year'] == 2001) |
    (gdp['Year'] == 2005) |
    (gdp['Year'] == 2010) |
    (gdp['Year'] == 2015) |
    (gdp['Year'] == 2020) |
    (gdp['Year'] == 2024) 
][['Entity', 'GDP per capita, PPP (constant 2021 international $)','Year']].rename(columns={'Entity': 'Country', 'GDP per capita, PPP (constant 2021 international $)': 'GDP','Year':'year'})

electricity_access=pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/API_acceso_electricidad.csv')
#los datos que vemos aqui son %of population con access 
id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
electricity_access_largo = electricity_access.melt(
    id_vars=id_vars,
    var_name='year',
    value_name='Access_Percentage'
)

electricity_access_largo['year'] = pd.to_numeric(electricity_access_largo['year'], errors='coerce').astype('Int64')
electricity_access_largo=electricity_access_largo[
    (electricity_access_largo['year'] == 2001) |
    (electricity_access_largo['year'] == 2005) |
    (electricity_access_largo['year'] == 2010) |
    (electricity_access_largo['year'] == 2015) |
    (electricity_access_largo['year'] == 2020) |
    (electricity_access_largo['year'] == 2024)
    ][['Country Name','year','Access_Percentage']].rename(columns={'Country Name':'Country'})

lights = pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/viirs-nighttime-lights-country.csv')
iso_codes = lights['iso'].unique()

country_object = pycountry.countries.get(alpha_3='AFG')

def iso_to_name(iso_code):
    try:
        country = pycountry.countries.get(alpha_3=iso_code)
        return country.name if country else iso_code  #si no encuentra, deja el ISO
    except:
        return iso_code

iso_to_name_dict = {code: iso_to_name(code) for code in lights['iso'].unique()}
lights['Country'] = lights['iso'].map(iso_to_name_dict)
lights = lights[
    (lights['year'] == 2015) | (lights['year'] == 2020) | (lights['year'] == 2024)][['Country','year','nlsum']].rename(columns={'nlsum': 'NightLights'})  

tipos_energia=pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/yearly_full_release_long_format.csv')
tipos_energia = tipos_energia.dropna(subset=['Continent'])
tipos_energia=tipos_energia[['Area','Year','Category','Variable','Unit','Value']].rename(columns={'Area':'Country','Year':'year'})
tipos_energia['Unique_Variable'] = tipos_energia['Category'] + '_' + tipos_energia['Variable']+'('+tipos_energia['Unit']+')'

#agrupar y Calcular la Media (para resolver duplicados residuales)
#agrupamos por las 3 dimensiones finales: País, Año, y la Nueva Variable Única
tipos_energia_agregada = tipos_energia.groupby(
    ['Country', 'year', 'Unique_Variable']
)['Value'].mean().reset_index()

#Pivotar el DataFrame (usando la nueva columna única)
tipos_energia_pivot = tipos_energia_agregada.pivot(
    #Columnas de índice para la tabla final (País y Año)
    index=['Country', 'year'],
    #columna que se convierte en los nuevos encabezados
    columns='Unique_Variable',
    #valores de la celda
    values='Value'
).reset_index()

life_exp_w=pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/API_SP.DYN.LE00.FE.IN_DS2_en_csv_v2_8069.csv')

life_exp_w_melt=life_exp_w.melt(
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    var_name='year',
    value_name='Life Expectancy Female (years)'
    )

life_exp_w_melt['year'] = pd.to_numeric(life_exp_w_melt['year'], errors='coerce')
life_exp_w_melt=life_exp_w_melt[
    (life_exp_w_melt['year'] == 2001) |
    (life_exp_w_melt['year'] == 2005) |
    (life_exp_w_melt['year'] == 2010) |
    (life_exp_w_melt['year'] == 2015) |
    (life_exp_w_melt['year'] == 2020) |
    (life_exp_w_melt['year'] == 2024) ][['Country Name','year','Life Expectancy Female (years)']].rename(columns={'Country Name':'Country'})

life_exp_m=pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/API_SP.DYN.LE00.MA.IN_DS2_en_csv_v2_126205.csv')
life_exp_m_melt=life_exp_m.melt(
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    var_name='year',
    value_name='Life Expectancy Men (years)'
    )
life_exp_m_melt['year'] = pd.to_numeric(life_exp_m_melt['year'], errors='coerce')
life_exp_m_melt=life_exp_m_melt[
    (life_exp_m_melt['year'] == 2001) |
    (life_exp_m_melt['year'] == 2005) |
    (life_exp_m_melt['year'] == 2010) |
    (life_exp_m_melt['year'] == 2015) |
    (life_exp_m_melt['year'] == 2020) |
    (life_exp_m_melt['year'] == 2024) ][['Country Name','year','Life Expectancy Men (years)']].rename(columns={'Country Name':'Country'})


co2=pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/owid-co2-data.csv')
co2=co2[
    (co2['year'] == 2001) |
    (co2['year'] == 2005) |
    (co2['year'] == 2010) |
    (co2['year'] == 2015) |
    (co2['year'] == 2020) |
    (co2['year'] == 2024)][['country','year','co2','co2_per_capita']].rename(columns={'country':'Country'})

gini=pd.read_csv('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/economic-inequality-gini-index.csv')
gini=gini[
    (gini['Year'] == 2001) |
    (gini['Year'] == 2005) |
    (gini['Year'] == 2010) |
    (gini['Year'] == 2015) |
    (gini['Year'] == 2020) |
    (gini['Year'] == 2024)][['Entity','Year','Gini coefficient (2021 prices)']].rename(columns={'Entity':'Country','Year':'year','Gini coefficient (2021 prices)':'Gini coefficient'})

name_mapping = {
    # OWID → World Bank official name
    "United States": "United States",
    "Russia": "Russian Federation",
    "South Korea": "Korea, Rep.",
    "Czechia": "Czech Republic",
    "Democratic Republic of Congo": "Congo, Dem. Rep.",
    "Republic of Congo": "Congo, Rep.",
    "Venezuela": "Venezuela, RB",
    "Iran": "Iran, Islamic Rep.",
    "Egypt": "Egypt, Arab Rep.",
    "Vietnam": "Viet Nam",
    "Laos": "Lao PDR",
    "Syria": "Syrian Arab Republic",
    "Yemen": "Yemen, Rep.",
    "Slovakia": "Slovak Republic",
    "North Korea": "Korea, Dem. People's Rep.",
    "Cape Verde": "Cabo Verde",
    "Palestine": "West Bank and Gaza",
    "Micronesia (country)": "Micronesia, Fed. Sts.",
    "Eswatini": "Eswatini",
    "Timor": "Timor-Leste",
    "Bolivia": "Bolivia",
    "Tanzania": "Tanzania",
    "Moldova": "Moldova",
}

life_exp_m_melt['Country'] = life_exp_m_melt['Country'].replace(name_mapping)
life_exp_w_melt['Country'] = life_exp_w_melt['Country'].replace(name_mapping)
valid_iso_codes = [c.alpha_3 for c in list(pycountry.countries)]
life_exp_w = life_exp_w[life_exp_w['Country Code'].isin(valid_iso_codes)]
life_exp_m = life_exp_m[life_exp_m['Country Code'].isin(valid_iso_codes)]

#mergee
df = pd.merge(energy, life_exp, on=['Country','year'], how='inner')
df = pd.merge(df, gdp, on=['Country','year'], how='inner')
df = pd.merge(df, lights, on=['Country','year'], how='left')
df = pd.merge(df,electricity_access_largo, on=['Country','year'], how='left')
df = pd.merge(df,tipos_energia_pivot,on=['Country','year'],how='left')
df = pd.merge(df,life_exp_m_melt, on=['Country','year'], how='left')
df = pd.merge(df,life_exp_w_melt, on=['Country','year'], how='left')
df = pd.merge(df,co2,on=['Country','year'],how='left')
df = pd.merge(df,gini,on=['Country','year'], how='left')

#GeoData (versión actualizada para Geopandas 1.1+) sino no funciona
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url)

world = world.rename(columns={
    'POP_EST': 'pop_est',
    'CONTINENT': 'continent',
    'NAME': 'Country',  #Nota: En la fuente original es 'NAME'
    'ISO_A3': 'iso_a3',
    'GDP_MD': 'gdp_md_est'
})
world = world[['pop_est', 'continent', 'Country', 'iso_a3', 'gdp_md_est', 'geometry']]

df_geo = world.merge(df, on='Country', how='left')
df_geo.to_file('data.geojson', driver='GeoJSON')


df_geo.to_excel('C:/Users/marie/OneDrive/Documentos/Maestría/Semestre 2/Visualización de datos/Práctica/DF_2/final_data.xlsx', index=False)
print("DF final guardado en 'final_data.xlsx'")

"""
#Comienzo de creación de la visualizacón 
#Esta parte aún no se ha probado
#Mapa 
m = folium.Map(location=[0, 0], zoom_start=2)
folium.TileLayer('openstreetmap', name='Día (Claro)').add_to(m)
folium.TileLayer('cartodbdark_matter', name='Noche (Oscuro)').add_to(m)

folium.Choropleth(
    geo_data='data.geojson',
    data=df_geo,
    columns=['name', 'Energy'],
    key_on='feature.properties.name',
    fill_color='YlOrRd',
    legend_name='Consumo Energía (kWh/persona)',
    name='Consumo Energía'
).add_to(m)

tooltip = folium.GeoJsonTooltip(
    fields=['name', 'Energy', 'LifeExp', 'GDP', 'NightLights'],
    aliases=['País:', 'Energía (kWh):', 'Expectativa Vida:', 'PIB per cápita (USD):', 'Luces Nocturnas (Intensidad):'],
    localize=True
)
folium.GeoJson('data.geojson', tooltip=tooltip).add_to(m)

folium.LayerControl().add_to(m)
m.save('mapa_interactivo.html')
print("Mapa guardado en 'mapa_interactivo.html'")
"""
