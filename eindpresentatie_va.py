import pandas as pd
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_folium import folium_static

crime2015 = pd.read_csv('crime2015.csv', encoding= 'unicode_escape')
crime2016 = pd.read_csv('crime2016.csv')
crime2017 = pd.read_csv('crime2017.csv')
crime2018 = pd.read_csv('crime2018.csv')
crime2019 = pd.read_csv('crime2019.csv')
crime2020 = pd.read_csv('crime2020.csv', encoding= 'unicode_escape')
crime = pd.concat([crime2015, crime2016, crime2017, crime2018, crime2019, crime2020])
community = pd.read_csv('american_community_survey_blk_grp_2016_2020.csv')
crime = crime.drop_duplicates(subset = ['incident_id'])

sf = gpd.read_file('crime.shp')
shape = gpd.read_file('american_community_survey_blk_grp_2016_2020.shp')
json = gpd.read_file('American_Community_Survey_5j_(2016_2020).geojson')
json['STFID'] = json["STFID"].str[1:]
denver = gpd.sjoin(json, sf)

#%%
st.title('Criminaliteit in Denver')
st.write('Denver is de hoofdstad van de Amerikaanse staat Colorado. Het bevat 78 officiële wijken. In elke van deze wijken vindt criminaliteit plaats. Wij zullen hier onderzoek naar doen met behulp van de criminaliteits data van Denver van 2015 tot en met 2020. Daarnaast gaan we ook kijken naar de community data van Denver waar wij onder andere het inkomen en de huizenprijzen per wijk kunnen verkrijgen. Wij zullen bij deze variabelen de samenhang met de criminaliteit onderzoeken.')
st.header('Datasets')
st.subheader('Criminialiteit in Denver')
st.dataframe(data = crime)
st.write('Bron: https://www.denvergov.org/opendata/dataset/city-and-county-of-denver-crime')
st.subheader('Community in Denver')
st.dataframe(data = community)
st.write('Bron: https://denvergov.org/opendata/dataset/city-and-county-of-denver-american-community-survey-block-groups-2016-2020')

# Kolommen year en month toevoegen en alle datums na 2020 eruit filteren
crime['year'] = pd.DatetimeIndex(crime['FIRST_OCCURRENCE_DATE']).year
#crime = crime[crime['year'] < 2021]
crime['month'] = pd.DatetimeIndex(crime['FIRST_OCCURRENCE_DATE']).month

season_dict = {1: 'Winter',
               2: 'Winter',
               3: 'Lente',
               4: 'Lente',
               5: 'Lente',
               6: 'Zomer',
               7: 'Zomer',
               8: 'Zomer',
               9: 'Herfst',
               10: 'Herfst',
               11: 'Herfst',
               12: 'Winter'}
crime['season'] = crime['month'].apply(lambda x: season_dict[x])

crime['REPORTED_DATE'] =  pd.to_datetime(crime['REPORTED_DATE'], infer_datetime_format=True, format = '%d-%m-%Y %H:%M:%S')
crime['FIRST_OCCURRENCE_DATE'] =  pd.to_datetime(crime['FIRST_OCCURRENCE_DATE'], infer_datetime_format=True, format = '%d-%m-%Y %H:%M:%S')
crime['LAST_OCCURRENCE_DATE'] =  pd.to_datetime(crime['LAST_OCCURRENCE_DATE'], infer_datetime_format=True, format = '%d-%m-%Y %H:%M:%S')
crime['time'] = crime['FIRST_OCCURRENCE_DATE'].dt.time
crime['hour'] = crime['FIRST_OCCURRENCE_DATE'].dt.hour

tod_dict = {0: 'Nacht',
            1: 'Nacht',
            2: 'Nacht',
            3: 'Nacht',
            4: 'Nacht',
            5: 'Nacht',
            6: 'Ochtend',
            7: 'Ochtend',
            8: 'Ochtend',
            9: 'Ochtend',
            10: 'Ochtend',
            11: 'Ochtend',
            12: 'Middag',
            13: 'Middag',
            14: 'Middag',
            15: 'Middag',
            16: 'Middag',
            17: 'Middag',
            18: 'Avond',
            19: 'Avond',
            20: 'Avond',
            21: 'Avond',
            22: 'Avond',
            23: 'Avond'}
crime['tod'] = crime['hour'].apply(lambda x: tod_dict[x])

typecrime_dict = {'public-disorder' : 'Licht',
                  'drug-alcohol' : 'Licht',
                  'sexual-assault' : 'Zwaar',
                  'other-crimes-against-persons' : 'Anders',
                  'all-other-crimes' : 'Anders',
                  'murder' : 'Zwaar',
                  'robbery' : 'Zwaar',
                  'aggravated-assault': 'Zwaar',
                  'arson': 'Zwaar',
                  'burglary' : 'Zwaar',
                  'larceny' : 'Licht',
                  'theft-from-motor-vehicle' : 'Licht',
                  'auto-theft': 'Licht',
                  'white-collar-crime': 'Licht'}
crime['type_crime'] = crime['OFFENSE_CATEGORY_ID'].apply(lambda x: typecrime_dict[x])

st.header('Plots')
st.subheader('Countplots')

categorie = plt.figure()
sns.countplot(data = crime, y = 'OFFENSE_CATEGORY_ID')
sns.set_palette(palette = 'Set3')
plt.title('Aantal misdaden per overtredingscategorie')
plt.ylabel('Overtredingscategorie')
plt.xlabel('Aantal')
st.write("In de onderstaande countplot is per overtredingscategorie te zien hoeveel misdaden er gepleegd zijn. Het valt op dat 'public-disorder' en 'larceny' het vaakst voorkomen. Verder komen 'arson' en 'murder' nauwelijk voor.")
plt.show()
st.pyplot(categorie)

crime_victim = crime.copy()
crime_victim['VICTIM_COUNT'] = crime_victim['VICTIM_COUNT'].replace([10, 11, 13, 32], '10 of meer')

slachtoffer = plt.figure()
sns.countplot(data = crime_victim, x = 'VICTIM_COUNT')
plt.xlabel('Aantal misdaden per slachtofferaantal')
sns.set_palette(palette='Set3')
#ax.set_xticks(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10 of meer'])
plt.yscale('log')
plt.ylabel('Aantal')
plt.title('Hoeveelheid misdaden per slachtofferaantal')
plt.show()
#10 of meer slachtoffers toevoegen
st.write('In de onderstaande countplot is te zien hoeveel slachtoffers de meeste misdaden hebben. Het valt op dat dit afneemt naarmate er meer slachtoffers zijn.')
st.pyplot(slachtoffer)

jaar = plt.figure()
sns.countplot(data = crime, x = 'year')
sns.set_palette(palette='Set3')
plt.title('Jaren wanneer de misdaden gepleegd zijn')
plt.xlabel('Jaar')
plt.ylabel('Aantal')
plt.yscale('log')
plt.ylim(50000, 60000)
plt.show()
st.write('In de onderstaande countplot is de hoeveelheid misdaden per jaar te zien. Let op dat de y-as een logaritmische schaal heeft. Er is te zien dat elk jaar meer dan 50.000 misdaden gepleegd worden. In 2015 werden de minste misdaden gepleegd en in 2018 de meeste misdaden. Het jaar 2020 is niet te zien omdat dit de datums vertegenwoordigt van de eerste voorval.')
st.pyplot(jaar)

seizoen = plt.figure()
sns.countplot(data = crime, x = 'season')
sns.set_palette(palette='Set3')
plt.title('Seizoenen wanneer de misdaden gepleegd zijn')
plt.xlabel('Seizoen')
plt.ylabel('Aantal')
plt.ylim(50000, 80000)
plt.show()
st.write('In de onderstaande countplot is per seizoen te zien hoeveel misdaden er gepleegd zijn. Het valt op dat in de winter minder misdaden worden gepleegd en in de zomer juist meer.')
st.pyplot(seizoen)

tod = plt.figure()
sns.countplot(data = crime, x = 'tod')
sns.set_palette(palette='Set3')
plt.title('Tijden van de dag wanneer de misdaden gepleegd zijn')
plt.xlabel('Tijd van de dag')
plt.ylabel('Aantal')
plt.show()
st.write('In de onderstaande countplot is te zien in welk tijd van de dag de meeste misdaden worden gepleegd. Er is te zien dat vooral in de avond en in de middag misdaden worden gepleegd.')
st.pyplot(tod)

hoods = ['five-points', 'cbd', 'capitol-hill', 'montbello', 'central-park', 'union-station', 'civic-center', 'east-colfax', 'lincoln-park', 'gateway-green-valley-ranch']
crime_unsave = crime[crime['NEIGHBORHOOD_ID'].isin(hoods)]

wijk = plt.figure()
sns.countplot(data = crime_unsave, y = 'NEIGHBORHOOD_ID')
sns.set_palette(palette='Set3')
plt.title('10 meest gevaarlijke wijken')
plt.xlabel('Aantal')
plt.ylabel('Wijk')
plt.show()
st.write("In de onderstaande countplot zijn de 10 meest gevaarlijke wijken te zien. Per wijk wordt laten zien hoeveel misdaden er gepleegd zijn in die wijk. Het valt op dat in de wijk 'five-points' de meeste criminaliteit plaatsvindt. De veiligste wijk (niet te zien in deze plot) is 'indian-creek'")
st.pyplot(wijk)

type = plt.figure()
sns.countplot(data = crime, x = 'type_crime')
sns.set_palette(palette='Set3')
plt.title('Type misdaden die gepleegd zijn')
plt.xlabel('Type')
plt.ylabel('Aantal')
plt.show()
st.write('In de onderstaande plot is te zien welke type misdaden het meeste voorkomen. De misdaden zijn door ons zelf opgedeeld in de drie categorieën. ')
st.pyplot(type)

#%%

st.header('Histogrammen en boxplotten')
st.subheader('Boxplot van het aantal misdaden per wijk')

denver_dup = denver.drop_duplicates(subset = ['OFFENSE_ID'])

crime_count = denver['NEIGHBORHO'].value_counts().reset_index()
pd.DataFrame(crime_count)
crime_count = crime_count.rename(columns = {'index' : 'Wijk', 'NEIGHBORHO': 'Aantal misdaden'})

st.write('In de onderstaante boxplot is de verdeling van het aantal misdaden per wijk te zien. Er is te zien dat de meeste wijken tussen de 2000 en 4000 misdaden hebben.')

outlier = st.radio('Kies of u outliers in de plot wilt of niet: ', options = ['Wel', 'Niet'])

crime_count_outlier = crime_count[crime_count['Aantal misdaden'] < 6000]

def frame():
    if outlier == 'Wel':
        return crime_count
    if outlier == 'Niet':
        return crime_count_outlier

box = plt.figure()
sns.boxplot(data = frame(), x = 'Aantal misdaden')
plt.title('Boxplot van de verdeling van het aantal misdaden per wijk')
plt.ylabel('Aantal')
plt.show()
st.pyplot(box)

st.subheader('Histogrammen van de verdeling van variabelen')

keuze = st.selectbox('Kies een variabele: ', options = ['median_household_income', 'median_house_value'])

denver_hist = denver_dup[denver_dup[keuze] > 0]
st.write('In de onderstaande histogram is de verdeling van verschillende variabelen te zien. In de selectbox kunt u de variabele kiezen die u wilt zien.')
histvar = plt.figure()
sns.histplot(data = denver_hist, x = keuze, bins = 15)
plt.ylabel('Aantal')
plt.show()
st.pyplot(histvar)

st.write('Het figuur hieronder, bestaande uit 5 histogrammen, geeft de hoeveelheid lichte en zware misdaad aan dat heeft plaatsgevonden voor een bepaalde populatie grootte of mediaan inkomen. Let hier goed op met de assen. In de histogrammen is te zien dat zwartmisdaad niet significant anders is dan geen of lichte misdaad.')
st.image('Cornielshist.png')

st.subheader('Bivariate plot')
st.write('in de onderstaande vier histogrammen zijn de verschillende populatie groepen tegen de mediaan inkomen per huishouden gezet in de periode van 2015 tot 2020. Voor het grootste gedeelte van mensen wonende in Denver ligt de mediaan inkomen per huishouden op zo’n 50.000 dolar per jaar. Tussen de verschillende populatie groepen is maar weinig verschil te vinden. Deze histogrammen geven  dan ook goed weer dat er in Denver maar weinig verschil in armoede is tussen etniciteiten of huidskleur.')
st.image('CornielsVAeind.png')

st.header('Regressieplots')
st.subheader('Regressie tussen het aantal misdaden in een wijk en andere variabelen')

st.write('In de onderstaande plot zijn de regressie plots weergegeven. Met behulp van de selectbox kun u uw variabelen kiezen. Bij beide variabelen zijn de outliers al weggehaald. Bij de relatie tussen de mediaan van huiswaarde en het aantal misdaden is weinig correlatie te zien. We kunnen dus concluderen dat de twee variabelen weinig invloed hebben op elkaar. Bij der relatie tussen de mediaan van het inkomen per huishouden en het aantal misdaden is meer correlatie te zien maar nog steeds niet veel. We kunnen concluderen dat de twee variabelen enige invloed hebben elkaar.')

display = {'median_household_income': 'Mediaan inkomen huishouden', 'median_house_value': 'Mediaan huiswaarde'}
choice = st.selectbox('Kies een variabele die u wilt vergelijken met het aantal misdaden: ',
                      options = ('median_house_value', 'median_household_income'),
                      format_func = lambda x : display.get(x))

total_count = denver_dup[choice].value_counts().reset_index()
pd.DataFrame(total_count)
total_count = total_count[total_count[choice] < 7000]
total_count = total_count.rename(columns = {'index' : choice, choice: 'misdaden'})

regtotal = plt.figure()
sns.regplot(data = total_count, x = choice, y = 'misdaden',
            scatter_kws={"color": "black"}, line_kws={"color": "red"})
plt.ylabel('Aantal misdaden')
plt.xlabel(choice)
plt.show()
st.pyplot(regtotal)


st.subheader('Logistieke regressielijnen en regressiemodel')
st.write('Het onderstaand figuur bevat logistieke regressie modellen met daarin de populatie groepen en het mediaan inkomen per huishouden tegen de mogelijkheid tot een zware misdaad. Wat opvalt is dat het mediaan inkomen per huishouden geen indicator kan zijn voor een mogelijk zware misdaad. Verder zien we dat de lage populatie waardes een grotere kans hebben op een zware misdaad. In de model samenvatting zien we dan ook dat de populatie groepen significant niet meewegen voor het voorspellen van een mogelijke zware misdaad. Opvallend is dat hier de mediaan inkomen per huishouden een grotere indicator is voor een mogelijk zware misdaad.')
st.image('cornielslog.png')
st.image('cornielsregr.png')

st.header('Map')

st.write('In de onderstaande kaart zijn de verschillende wijken van Denver weergegeven. Daarnaast zijn ook de gepleegde misdaden weergegeven. U kun zelf met behulp van de onderstaande slider bepalen hoeveel misdaden u weergegeven wilt zien. Dit is gedaan met behulp van een random seed. Daarnaast kunt u ook bepalen welke type misdaden u weergegeven wil hebben op de kaart. Als u op een wijk klikt krijgt u de mediaan van de huiswaarde en de mediaan van het inkomen per huishouden van die specifieke wijk te zien. Verder kunt u ook op een misdaadpunt klikken om het betreffende adres te zien en wat voor misdaad het is.')
sample = st.slider('Kies het aantal punten u wilt zien: ', min_value = 10, max_value = 300000,
                         value = 5000)
crime_random = crime.sample(n=sample, replace=False, random_state=1)


m = folium.Map(location = [39.742043, -104.9], zoom_start=11)
folium.GeoJson(json, 
               popup=folium.GeoJsonPopup(["median_house_value", 'median_household_income'],
                                         aliases = ['Mediaan huiswaarde', 'Mediaan inkomen huishouden'])).add_to(m)

crime_random.dropna(subset=['type_crime', 'GEO_LON', 'GEO_LAT'],inplace=True)

type = st.radio('Kies de variabelen die u wilt zien: ',
                options = ('Alle misdaden', 'Zware misdaden', 'Lichte misdaden', 'Anders'))
def typecrime(x):
    if type == 'Alle misdaden':
        if x == 'Zwaar':
            return 'red'
        if x == 'Anders':
            return 'grey'
        if x == 'Licht':
            return 'white'

    if type == 'Zware misdaden':
        if x == 'Zwaar':
            return 'red'
        else:
            pass

    if type == 'Lichte misdaden':
        if x == 'Licht':
            return 'white'
        else:
            pass

    if type == 'Anders':
        if x == 'Anders':
            return 'grey'
        else:
            pass


crime_random['color_typecrime'] = crime_random['type_crime'].apply(lambda x: typecrime(x))

crime_random.apply(lambda x: folium.Circle(location = [x['GEO_LAT'], x['GEO_LON']],
                                           radius = 50,
                                           fill = True,
                                           color = x['color_typecrime'],
                                           popup = [x['INCIDENT_ADDRESS'], x['OFFENSE_CATEGORY_ID']]
                                           ).add_to(m), axis = 1)

st.markdown('Rood = Zware misdaad')
st.markdown('Wit = Lichte misdaad')
st.markdown('Grijs = Anders')

folium_static(m)