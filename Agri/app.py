from __future__ import print_function

import dash
import dash_table as dt
import plotly.express as px
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from owlready2 import *
import os
import json
import urllib
import math
import arabic_reshaper
from bidi.algorithm import get_display
import datetime
#import requests

#OpenWeatherMap parameters (IF USED, should be moved after the ontology is parsed)
# city = agri[agriPlaces[0]]
# cityCoords = city.topLeft[0]
# lat,lon = cityCoords.split(', ', 1)
# months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
#           'September', 'October', 'November', 'December']
# dfClimate = pd.DataFrame(columns=['TMIN', 'TMAX', 'TAVG'])
# climateKey = 'a28ec2a03c06081399695812e7d4e109'
# climateURL = 'https://history.openweathermap.org/data/2.5/aggregated/month'
# monthCount = 0
# for i in months:
#     monthCount += 1
#     response = requests.get(climateURL, params={'month':monthCount, 'lat':lat,'lon':lon, 'appid':climateKey})
#     xyz = response.json()
#     resultC = xyz['result']
#     tempC = resultC['temp']
#     TMIN = tempC['average_min']
#     TMIN = round(float(TMIN) - 273.15, 0)
#     TMAX = tempC['average_max']
#     TMAX = round(float(TMAX) - 273.15, 0)
#     TAVG = tempC['mean']
#     TAVG = round(float(TAVG) - 273.15, 0)
#     dfClimate = dfClimate.append({'TMIN':TMIN, 'TMAX':TMAX, 'TAVG':TAVG}, ignore_index=True)
# dfClimate.index = months


# Getting IP adress of user
ip_data = json.loads(urllib.request.urlopen("http://ip.jsontest.com/").read())
your_ip = ip_data["ip"]

# Getting location of IP address
access_key=''
request_ip_url = 'http://api.ipstack.com/'+your_ip+'?access_key='+access_key
detailed_ip = json.loads(urllib.request.urlopen(request_ip_url).read())

# Getting the continent from the response
continent = detailed_ip['continent_code']
#continent = 'EU'  # setting value for continent so that we don't have to keep calling API

# Getting the climate data from json file [IF we get free access to API, we'll replace it]
climateFile = 'assets/climate.json'  # the climate json file location
f = open(climateFile, "r")  # open the climate json file
climateData = json.load(f)  # load the content of the json file
# load the data into a data frame
dfClimate = pd.DataFrame(climateData['Climates'])

# we get closest location based on continent
if continent == 'EU':
    place = 'Malta'
else:
    place = 'Palestine'


df = pd.DataFrame([
    dict(Task="Plate", Start='2021-03-01',
         Finish='2021-03-01', Completion_pct=50),
    dict(Task="Outside", Start='2021-03-01',
         Finish='2021-03-28', Completion_pct=25),
    dict(Task="Harvest", Start='2009-03-21',
         Finish='2009-03-28', Completion_pct=75)
])
fig = px.timeline(df, x_start="Start", x_end="Finish",
                  y="Task", color="Task")
#fig.update_yaxes(autorange="reversed")

# Setting Stylesheets
app = dash.Dash(__name__, external_scripts=['https://code.jquery.com/jquery-3.5.1.min.js'], external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
                                                                                                                  'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap',
                                                                                                                  'https://use.fontawesome.com/releases/v5.8.1/css/all.css'])

curDir = os.getcwd()  # getting working directory
# getting full path of the ontology
owlPath = 'file://' + curDir + '/assets/agri.owl'
agri = get_ontology(owlPath).load()  # loading the Ontology

# using the reasoner 'HERMI' to infer knowledge
with agri:
    sync_reasoner()

agriPlaces = agri.search(type=agri[place])  # get locations in that country
agriPlaces = [str(x) for x in agriPlaces]  # convert object elements to string
# trim the prefix agri. from all elements
agriPlaces = [sub[5:] for sub in agriPlaces]
agriPlaces.sort()  # Sort list alphabetically

# choose the climate of the specified location from the df
climate = dfClimate[agriPlaces[0]]
# converting the selected data into the final df
yourClimate = pd.DataFrame(climate[0][0])

# Get list of all instances of type Plant
agriPlants = agri.search(type=agri.Plant)
agriPlants = [str(x) for x in agriPlants]  # convert object elements to string
# trim the prefix agri. from all elements
agriPlants = [sub[5:] for sub in agriPlants]
agriPlants.sort()  # Sort list alphabetically

####Loading the DataFrame of Properties ####
plant = agri[agriPlants[0]]  # First Plant

# start an empty dataframe
df_plant = pd.DataFrame(columns=['Property', 'Value'])
# append property and its value to the dataframe
for prop in plant.get_properties():
    for value in prop[plant]:
        if prop.python_name != 'seeAlso' and prop.python_name != 'hasCompanion':
            x = str(value)
            x = x.replace("agri.", "")
            df_plant = df_plant.append(
                {'Property': prop.python_name, 'Value': x}, ignore_index=True)

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']
plant_month = {}
for m in months:
    mon = agri[m]
    try:
        malMonth = mon.seeAlso.mt[0]
        palMonth = arabic_reshaper.reshape(mon.seeAlso.ar[0])
    except:
        malComp = ''
        palComp = ''
    y = m + " . " + malMonth + " . " + palMonth
    plant_month[m] = y

app.layout = html.Div([
    html.Div([
        html.Script(src=app.get_asset_url('js/main.js')),
        html.P([
        html.I(className="fas fa-map-marker-alt"), html.Span(place, className='countryLocation')], className='titleLocation'),
        html.Div([
            html.Div([
                html.Button([
                    html.Div([
                        html.Img(src=app.get_asset_url('img/crops.png'),
                                 className='card-img-top cropImage'),
                        html.P(["Select a Crop", html.Br(), "Għazel x'tixtieq tiżra", html.Br(), "المحصول"],
                               className='card-text')
                    ], className='card-body')
                ], n_clicks=0, className='card', id='cropButton')
            ], className='col-sm-6'),
            html.Div([
                html.Button([
                    html.Div([
                        html.Img(src=app.get_asset_url('img/period.png'),
                                 className='card-img-top cropImage'),
                        html.P(["Select a Period", html.Br(), "Għazel perjodu", html.Br(), "الفترة"],
                               className='card-text')
                    ], className='card-body')
                ], n_clicks=0, className='card', id='plantingPeriodButton')
            ], className='col-sm-6')
        ], className='row'),

        html.Div([
            html.H4(
                "When would you like to plant?   •   Meta tixtieq tiżra?   •   الموسم؟"),
            dcc.Dropdown(
                id='loading-month',
                options=[
                    {'label': y, 'value': x}
                    for x, y in plant_month.items()
                ],
                value='January'
            )], className="userInput plantTimeInput"),
        html.Div([
            html.H4(
                "What crop would you like to plant?   •   X'tixtieq tiżra?   •   المحصول المرغوب؟"),
            dcc.Dropdown(
                id='loading-plants',
                options=[
                    {'label': prop, 'value': prop}
                    for prop in agriPlants
                ],
                value=agriPlants[0]
            )
        ], className="userInput"),
        html.Div([
            html.H4(
                ["Specify the area of bed   •   Il-qies tar-raba'   •   المسطبة"]),
            dcc.Input(
                id="dtrue", type="number", className="form-control", placeholder="in metres squared",
                debounce=True, value='10', min=1, max=1000
            )
        ], className="userInput")
    ], id='col-left', className='col-lg-3'),
    html.Div([
        html.Div('Select an option to show data',
                 className='noDataSelectedText'),
        html.Div([
            html.Div('A guide to growing carrots', id='vegetableName'),
            html.Div("Gwida għat-tkabbir ta' zunnarija", id='vegetableNameMt'),
            html.Div("دليل لزراعة الجزر", id='vegetableNameAr'),
            html.Div([html.Div(id='growthStartDate',
                               children=[
                                   html.H3("Ideal planting month is"),
                                   html.H4("Ix-xahar ideali biex tiżra"),
                                   html.H4("الشهر المثالي للزراعة"),
                                   html.Div("March", className="answer",
                                            id="cropSeason"),
                                   html.H4("Month in Maltese",
                                           id="cropSeasonMt"),
                                   html.H4("Month in Arabic",
                                           id="cropSeasonAr"),
                               ], className='dashboardComponent'),
                      html.Div([
                          html.H3('Accompanied by'),
                          html.H4('Akkompanjament'),
                          html.H4('بمرافقة'),
                          dcc.Dropdown(
                              id='companions-dropdown',
                              multi=False
                          ),
                      ], className='dashboardComponent'),
                      html.Div(id='seedsRequired',
                               children=[
                                   html.H3("Seeds required"),
                                   html.H4("Żerriegħa"),
                                   html.H4("البذور"),
                                   html.Div("5.67g", className="answerNumeric",
                                            id="seedsAmount")
                               ], className='dashboardComponent'),

                      html.Div([
                          html.Div([
                              html.H3('Growth Timeline in weeks'),
                              html.H4('Skeda'),
                              html.H4('جدول النمو'),
                          ], className='growthTimelineMain'),
                          dt.DataTable(id='growthTable', columns=[{"name": i, "id": i} for i in df_plant.columns],
                                       style_header={'display': 'None'},
                                       style_cell_conditional=[{
                                           'if': {'column_id': c}, 'textAlign': 'center', 'width': '200px'} for c in ['Value']]),
                          html.H4('Note: Companion plants should be planted in the bed in the same day.',
                                  className="plateGrowthNote"),
                          html.H4("Nota: Il-pjanta ewlenija u l-akkompanjament għandhom jitħawlu fl-istess ġurnata.",
                                  className="plateGrowthNote"),
                          html.H4('ملاحظة: النباتات المرافقة يجب أن تزرع في المسطبة في نفس الوقت.',
                                  className="plateGrowthNote")

                      ], className='dashboardComponent'),
                      html.Div([dcc.Graph(figure=fig)],
                               className='dashboardComponent ganttChart', id="ganttChart"),
                      html.Div(
                children=[
                    html.H3("Maximum Seedlings"),
                    html.H4("L-akbar ammont ta' nebbieta"),
                    html.H4('عدد النباتات الممكنة'),
                    html.Div(id='maximumSeedlings', className="answerNumeric")
                ], className='dashboardComponent'),

                html.Div(
                children=[
                    html.H3("Seedlings Distance"),
                    html.H4("Distanza bejn in-nebbieta"),
                    html.H4("المسافة بيت النباتات"),
                    html.Div(id='seedlingsDistance', className="answerNumeric")
                ], className='dashboardComponent'),

                html.Div([
                    html.H3('Expected Harvest'),
                    html.H4("Ħsad mistenni"),
                    html.H4("الحصاد المتوقع"),

                    dt.DataTable(id='table2', columns=[{"name": i, "id": i} for i in df_plant.columns],
                                 data=df_plant.to_dict('records'),
                                 style_cell={'padding': '5px',
                                             'textAlign': 'center'},
                                 style_as_list_view=True,
                                 style_header={'display': 'None'},
                                 style_table={'width': '200px'},
                                 style_cell_conditional=[{
                                     'if': {'column_id': c}, 'width': '200px'} for c in ['Value']])

                ], className='dashboardComponent'),
                html.Div([
                    html.H3('Temperature Range'),
                    html.H4("Temperatura"),
                    html.H4("نطاق الحرارة"),
                    daq.Thermometer(
                        id='my-2thermometer',
                        value=25,
                        min=5,
                        max=35,
                        color='#003E59'
                    ),
                    html.H3('', className = 'descTemperature', id='descT'),
                    html.H4('', id='descTmt'),
                    html.H4('', id='descTar'),

                ], className='dashboardComponent'),
                html.Div([
                    html.H3('Companion Requirements'),
                    html.H4('Rekwiżiti għall-akkompanjament'),
                    html.H4('بيانات النبات المرافق'),
                    html.Div("Lettuce", id='companionName',
                             className="answer"),
                    html.Div([
                        html.H3('Growth Timeline in weeks'),
                    ]),
                    dt.DataTable(id='growthTableCompanion', columns=[{"name": i, "id": i} for i in df_plant.columns],
                                 style_header={'display': 'None'},
                                 style_cell_conditional=[{
                                     'if': {'column_id': c}, 'width': '200px'} for c in ['Value']]),
                    html.Hr(),
                    html.H3("Seeds required"),
                    html.Div("5.67g", className="answer",
                             id="seedsAmountCompanion"),
                    html.Hr(),
                    html.H3('Expected Harvest'),
                    dt.DataTable(id='expectedHarvestTableCompanion', columns=[{"name": i, "id": i} for i in df_plant.columns],
                                 data=df_plant.to_dict('records'),
                                 style_cell={'padding': '5px'},
                                 style_as_list_view=True,
                                 style_header={'display': 'None'},
                                 style_cell_conditional=[{
                                     'if': {'column_id': c}, 'width': '200px'} for c in ['Value']])

                ], className='dashboardComponent')], className='dashboard text-center'),

        ])
    ], className='col-lg-9')

], className='row')


# Choosing a planting period
@app.callback([
    Output('loading-plants', 'options')],
    [Input('loading-month', 'value'),
     Input('cropButton', 'n_clicks'),
     Input('plantingPeriodButton', 'n_clicks')]
)
def updatePeriod(month, cropBtn, periodBtn):
    global yourClimate
    global agri
    global agriPlants
    theInput = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'cropButton' in theInput:
        pdict ={}
        for i in agriPlants:
            p = agri[i]
            pmt = p.seeAlso.mt[0]
            ppt = arabic_reshaper.reshape(p.seeAlso.ar[0])
            fullP = i +' . '+ str(pmt)+ ' . '+ str(ppt)
            pdict[i] = fullP

        options = [{'label': y, 'value': x} for x, y in pdict.items()]
        return [options]
    elif 'plantingPeriodButton' in theInput or 'loading-month' in theInput:
        idealC = yourClimate[month]
        TMIN = int(idealC.loc['TMIN'])
        TMAX = int(idealC.loc['TMAX'])
        idealPlants = []
        for x in agriPlants:
            plant = agri[x]  # Find plant in ontology
            min = plant.hasIdealMinTemp
            max = plant.hasIdealMaxTemp
            try:
                if min[0] < (TMIN+1) and (TMAX-1) < max[0]:
                    idealPlants.append(x)
            except:
                min = min
        pdict ={}
        for i in idealPlants:
            p = agri[i]
            pmt = p.seeAlso.mt[0]
            ppt = arabic_reshaper.reshape(p.seeAlso.ar[0])
            fullP = i +' . '+ str(pmt)+ ' . '+ str(ppt)
            pdict[i] = fullP
        options = [{'label': y, 'value': x} for x, y in pdict.items()]
        return [options]
    else:
        raise PreventUpdate

# Choosing the primary crop to plant

@app.callback(
    [
        Output('vegetableName', 'children'),
        Output('companions-dropdown', 'options'),
        Output('table2', 'data'),
        Output('growthTable', 'data'),
        Output('maximumSeedlings', 'children'),
        Output('seedlingsDistance', 'children'),
        Output('cropSeason', 'children'),
        Output('cropSeasonMt', 'children'),
        Output('cropSeasonAr', 'children'),
        Output('seedsAmount', 'children'),
        Output('my-2thermometer', 'value'),
        Output('my-2thermometer', 'min'),
        Output('ganttChart', 'children'),
        Output('descT', 'children'),
        Output('descTmt', 'children'),
        Output('descTar', 'children')],
    [Input('loading-plants', 'value'),
     Input('dtrue', 'value')],
)
def updateCrop(value, area):
    global agri
    global agriPlants
    global yourClimate
    global months

    vegetableName = 'A guide to growing %s' % value
    area = float(area)

    try:
        ####Loading the DataFrame of Properties ####
        plant = agri[value]

        # Getting Maltese and Palestinian-Arabic translations of the names
        try:
            malName = plant.seeAlso.mt[0]
            palName = arabic_reshaper.reshape(
                plant.seeAlso.ar[0])  # connect arabic letters
            # correct the direction of the word rtl
            #palName = get_display(palName)
        except:
            print('Issue with the translation of ', plant)

        # Getting ideal planting season
        try:
            idealMin = int(plant.hasIdealMinTemp[0])
            idealMax = int(plant.hasIdealMaxTemp[0])
            idealِAVG = (idealMin + idealMax)/2
            idealِAVG = math.ceil(idealِAVG)
            idealTemp = int(plant.hasIdealTemp[0])
            absMin = plant.hasMinTemp[0]
            absMax = plant.hasMaxTemp[0]
            descripT='This crop can resist temperatures between '+str(absMin)+'°C and '+str(absMax)+'°C. The ideal range is '+str(idealMin)+'°C to '+str(idealMax)+'°C, while the the best temperature is '+str(idealTemp)+'°C.'
            descripTmt = 'Din il-pjanta tiflaħ temperaturi bejn '+str(absMin)+'°C and '+str(absMax)+'°C. Idealment tinżamm temperatura bejn '+str(idealMin)+'°C to '+str(idealMax)+'°C, filwaqt li l-aħjar temperatura possibli hija dik ta '+str(idealTemp)+'°C.'
            descripTar = 'هذا المحصول يستحمل حرارة في نطاق %s و %s درجات. النطاق المثالي هو من %s إلى %s درجة، في حين أن المعدل المثالي للنمو هو %s درجة.' % (str(absMin),str(absMax), str(idealMin), str(idealMax),str(idealTemp))
            season = ''
            idealSeason = "March"
            if idealMax > 30:
                season = 'summer'
                if idealMin < 20:
                    idealSeason = "August"
                else:
                    idealSeason = "May"
            elif idealMax < 31:
                if idealMin < 12:
                    orderedClimate = yourClimate[yourClimate.columns[[0, 10]]]
                    season = 'winter'
                else:
                    orderedClimate = yourClimate[yourClimate.columns[[2, 9]]]
                    season = 'spring'

            if season != 'summer':
                orderedClimate = orderedClimate.transpose()
                orderedClimate['TMIN'] = orderedClimate['TMIN'].astype(int)
                orderedClimate = orderedClimate.sort_values(
                    ['TMIN'], ascending=False)
                y = 100
                for index, row in orderedClimate.iterrows():
                    x = int(row['TAVG'])-idealِAVG
                    if abs(x) < y:
                        idealSeason = index
                        y = abs(x)
        except Exception as e:
            print('exception')
            print(e)
            idealMin = 10
            idealMax = 25
            idealSeason = "March"
            descripT =''
            descripTmt =''
            descripTar =''

        theMonth = agri[idealSeason]
        malMonth = theMonth.seeAlso.mt[0]
        palMonth = arabic_reshaper.reshape(theMonth.seeAlso.ar[0])  # connect arabic letters
        # correct the direction of the word rtl
        #palMonth = get_display(palMonth)
        idealSeasonMt = malMonth
        idealSeasonAr = palMonth

        # Calculate harvest amount and requirements
        try:
            beginnerHarvest = plant.hasBeginnerHarvestOf[0]*area/10
            intermediateHarvest = plant.hasIntermediateHarvestOf[0]*area/10
            advancedHarvest = plant.hasAdvancedHarvestOf[0]*area/10
            maximumSeedlings = plant.hasMaximumSeedlingsOf[0]*area/10
            seedlingsDistance = plant.hasDistanceOf[0]
            seedsWeight = plant.hasSeedsWeightOf[0]*area/10
            seedsWeight = round(seedsWeight,1)
            maximumSeedlings = round(maximumSeedlings, 1)
            seedlingsDistance = round(seedlingsDistance, 1)
        except:
            beginnerHarvest = '--'
            intermediateHarvest = '--'
            advancedHarvest = '--'
            maximumSeedlings = '--'
            seedlingsDistance = '--'
            seedsWeight = '--'

        # Calculate Growth period
        try:
            plateGrowth = plant.hasPlateGrowthPeriodOf[0]
            outsideGrowth = plant.hasOutsideGrowthPeriodOf[0]
            harvestPeriod = plant.hasHarvestPeriodOf[0]
        except:
            plateGrowth = '--'
            outsideGrowth = '--'
            harvestPeriod = '--'

        # append property and its value to the dataframe
        harvestTable = [
            {'Property': 'Beginner ◦ Prinċipjant ◦ مبتدئ', 'Value': '%skg' % beginnerHarvest},
            {'Property': 'Intermediate ◦ Intermedju ◦ متوسط', 'Value': '%skg' % intermediateHarvest},
            {'Property': 'Advanced ◦ Avvanzat ◦ متقدم', 'Value':  '%skg' % advancedHarvest}
        ]
        growthTimeline = [
            {'Property': 'Plate Growth ◦ Tħawwil ġewwa ◦ في الصواني', 'Value': plateGrowth},
            {'Property': 'Outside Growth ◦ Tħawwil barra ◦ في الأرض', 'Value': outsideGrowth},
            {'Property': 'Harvesting ◦ Ħsad ◦ الحصاد', 'Value': harvestPeriod}
        ]

        # Update Gantt Chart
        try:
            monthNumber = 0
            for i in months:
                monthNumber += 1
                if i == idealSeason:
                    break
            plateDays = datetime.timedelta(days=plateGrowth*7)
            outsideDays = datetime.timedelta(days=outsideGrowth*7)
            harvestDays = datetime.timedelta(days=(harvestPeriod * 7)+1)

            startPlate = datetime.date(2021, monthNumber, 1)
            endPlate = startPlate + plateDays

            startHarvest = endPlate + outsideDays
            endHarvest = startHarvest + harvestDays

            startOutside = endPlate
            endOutside = endHarvest

            df = pd.DataFrame([
                dict(Task="Plate", Start=startPlate,
                     Finish=endPlate, Completion_pct=50),
                dict(Task="Outside", Start=startOutside,
                     Finish=endOutside, Completion_pct=25),
                dict(Task="Harvest", Start=startHarvest,
                     Finish=endHarvest, Completion_pct=75)
            ])

            fig = px.timeline(df, x_start="Start", x_end="Finish",
                              y="Task", color="Task")
            #fig.update_yaxes(autorange="reversed")
        except:
            df = pd.DataFrame([
                dict(Task="Plate", Start='2021-03-01',
                     Finish='2021-03-01', Completion_pct=50),
                dict(Task="Outside", Start='2021-03-01',
                     Finish='2021-03-28', Completion_pct=25),
                dict(Task="Harvest", Start='2021-03-21',
                     Finish='2021-03-28', Completion_pct=75)
            ])

            fig = px.timeline(df, x_start="Start", x_end="Finish",
                              y="Task", color="Task")
           # fig.update_yaxes(autorange="reversed")

        ####Loading Companions in Dropdown ####
        companionList = agri.search(hasCompanion=plant)
        plant_comp = []
        for companion in companionList:
            try:
                malComp = companion.seeAlso.mt[0]
                palComp = arabic_reshaper.reshape(companion.seeAlso.ar[0])
            except:
                malComp = ''
                palComp = ''
            x = str(companion)
            x = x.replace("agri.", "")
            y = x + " . " + malComp + " . " + palComp
            plant_comp.append({'label': y, 'value': x})

        seedsWeight = '%sg' % seedsWeight
        seedlingsDistance = '%scm' % seedlingsDistance

        return vegetableName, plant_comp, harvestTable,  \
            growthTimeline,  maximumSeedlings, \
            seedlingsDistance, idealSeason, idealSeasonMt, idealSeasonAr, seedsWeight,\
            idealMax, idealMin, dcc.Graph(figure=fig), descripT, descripTmt, descripTar
    except Exception as e:
        print('exception')
        print(e)
        empty_dict = [{'Property': '--', 'Value': '--'}]
        raise PreventUpdate

# Choosing the companion plant


@app.callback(
    [Output('vegetableNameAr', 'children'),
     Output('vegetableNameMt', 'children'),
     Output('expectedHarvestTableCompanion', 'data'),
     Output('growthTableCompanion', 'data'),
     Output('companionName', 'children'),
     Output('seedsAmountCompanion', 'children')],
    [Input('companions-dropdown', 'value'),
     Input('dtrue', 'value'),
     Input('loading-plants', 'value')]
)
def updateCompanion(value, area, primary):
    global agri
    try:
        comapnionName = value
        area = float(area)

        ####Loading the DataFrame of Properties ####
        plant = agri[value]
        plantName = agri[primary]
        # Getting Maltese and Palestinian-Arabic translations of the names
        try:
            malName = "Gwida għat-tkabbir ta' %s" % plantName.seeAlso.mt[0]
            palName = arabic_reshaper.reshape(
                plantName.seeAlso.ar[0])  # connect arabic letters
            palName = "ارشادات زراعة %s" % palName

        except:
            print('Issue with the translation of ', plantName)
        # Calculate harvest amount and requirements
        try:
            beginnerHarvest = plant.hasBeginnerHarvestOf[0] * area / 10
            intermediateHarvest = plant.hasIntermediateHarvestOf[0] * area / 10
            advancedHarvest = plant.hasAdvancedHarvestOf[0] * area / 10
            maximumSeedlings = plant.hasMaximumSeedlingsOf[0] * area / 10
            seedlingsDistance = plant.hasDistanceOf[0]
            maximumSeedlings = round(maximumSeedlings, 1)
            seedlingsDistance = round(seedlingsDistance, 1)
            seedsWeight = plant.hasSeedsWeightOf[0] * area / 10
            seedsWeight = round(seedsWeight, 1)
        except:
            beginnerHarvest = '--'
            intermediateHarvest = '--'
            advancedHarvest = '--'
            maximumSeedlings = '--'
            seedlingsDistance = '--'
            seedsWeight = '--'

        # Calculate Growth period
        try:
            plateGrowth = plant.hasPlateGrowthPeriodOf[0]
            outsideGrowth = plant.hasOutsideGrowthPeriodOf[0]
            harvestPeriod = plant.hasHarvestPeriodOf[0]
        except:
            plateGrowth = '--'
            outsideGrowth = '--'
            harvestPeriod = '--'

        # append property and its value to the dataframe
        harvestTable = [
            {'Property': 'Beginner ◦ Prinċipjant ◦ مبتدئ', 'Value': '%skg' % beginnerHarvest},
            {'Property': 'Intermediate ◦ Intermedju ◦ متوسط', 'Value': '%skg' % intermediateHarvest},
            {'Property': 'Advanced ◦ Avvanzat ◦ متقدم', 'Value':  '%skg' % advancedHarvest}
        ]
        growthTimeline = [
            {'Property': 'Plate Growth ◦ Tħawwil fuq ġewwa ◦ في الصواني', 'Value': plateGrowth},
            {'Property': 'Outside Growth ◦ Tħawwil fuq barra ◦ في الأرض', 'Value': outsideGrowth},
            {'Property': 'Harvesting ◦ Ħsad ◦ الحصاد', 'Value': harvestPeriod}
        ]

        seedsWeight = '%sg' % seedsWeight
        return palName, malName, harvestTable, growthTimeline, comapnionName, seedsWeight
    except Exception as e:
        print('exception')
        print(e)
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
