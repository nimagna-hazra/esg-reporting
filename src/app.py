from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import re
import pathlib

app = Dash(__name__,external_stylesheets=[dbc.themes.COSMO])
server = app.server


PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

#df = pd.read_csv(DATA_PATH.joinpath("2014_apple_stock.csv"))

df=pd.read_excel(DATA_PATH.joinpath('2024.02.28_Updated Transp. Index 2023.xlsx'),sheet_name='Full Dataset_Board', nrows=500)
dfnz2 = pd.read_excel(DATA_PATH.joinpath('2024.04.04-NZ_not full QC_ Consumer Staples.xlsx'),sheet_name='Dissertation Net Zero & Governa', nrows=496)
dfpivot = pd.read_csv(DATA_PATH.joinpath('Pivoted_master_data.csv'))

#df2 = pd.read_csv('2024.04.04_Consumer Staples NZ QCd.csv')

#data2=data[data['Date Local'].str.slice(0,4).astype(int) >= 2006]

#app = Dash(__name__)
# app.layout = dbc.Container(
#     dbc.Alert("Hello Bootstrap!", color="success"),
#     className="p-5",
# )

def company_list(sector):
    dfcs = df.loc[df['GICS.Sector'] == sector,['Company.Name','CM7a.GHG.Emissions.','CM7b.GHG.Emissions.'
                                                       ,'CM7c.GHG.Emissions.','TCFD New','CM9.Land.use.and.eco','Water amount Index','water stress index','Revenue']]
    dfcs.rename(columns={"Company.Name": "Company","CM7a.GHG.Emissions.": "GHG Scope 1 Emission", "CM7b.GHG.Emissions.": "GHG Scope 2 Emission",
                     "CM7c.GHG.Emissions.": "GHG Scope 3 Emission", "TCFD New": "TCFD",
                     "CM9.Land.use.and.eco": "Biodiversity", "Water amount Index": "Water Disclosure",
                     "water stress index": "Water Stress Disclosure",
                     "Revenue": "Revenue"},inplace=True)
    
    dfcs = dfcs.sort_values(by=['Revenue'], ascending=False)
    
    companies = dfcs['Company'].tolist()
    top_companies = dfcs.head(10)['Company'].tolist()
    
    return sorted(companies), sorted(top_companies)

def trafficlight(sector,company_list):
    dfcs = df.loc[df['GICS.Sector'] == sector,['Company.Name','CM7a.GHG.Emissions.','CM7b.GHG.Emissions.'
                                                       ,'CM7c.GHG.Emissions.','TCFD New','CM9.Land.use.and.eco','Water amount Index','water stress index','Revenue']]
    dfcs.rename(columns={"Company.Name": "Company","CM7a.GHG.Emissions.": "GHG Scope 1 Emission", "CM7b.GHG.Emissions.": "GHG Scope 2 Emission",
                     "CM7c.GHG.Emissions.": "GHG Scope 3 Emission", "TCFD New": "TCFD",
                     "CM9.Land.use.and.eco": "Biodiversity", "Water amount Index": "Water Disclosure",
                     "water stress index": "Water Stress Disclosure",
                     "Revenue": "Revenue"},inplace=True)
    
    mask = dfcs['Company'].isin(company_list)
    
    dfcs_melted = dfcs[mask].melt(id_vars=['Company'], var_name='Metric', value_name='Status')
    

    dfcs_melted['Status'].astype('string')
    categorical_mapping = {1.0: 'Full Disclosure', 0.5: 'Partial Disclosure', 0.0: 'No Disclosure'}
    dfcs_melted['Status'] = dfcs_melted['Status'].map(categorical_mapping)
    
    fig = px.scatter(dfcs_melted, y="Company", x="Metric", color="Status",
                     color_discrete_sequence=['#4E7E6B','#FFD100','#F43A00'],
                     #width = 2000, 
                     height = 1000, 
                     #title='Disclosure Status for Consumer Staples Environmental Metrics'
                    )
    fig.update_traces(marker_size=25)
    fig.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
                      title_x=0.5,xaxis=dict(side="top"),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None))
    fig.update_yaxes(categoryorder='category descending', title=None)
    fig.update_xaxes(title=None)
    fig.add_shape(
        type="line",
        x0=0,
        y0=1,
        x1=1,
        y1=1,
        line=dict(
            color="black",
            width=1,
        ),
        xref="paper",
        yref="paper"
    )
    
    return fig


def tghg1(sector,company_list):
    tghg1 = dfnz2.loc[:,['Enter the full company name', 'What is the company\'s current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)']]
    tghg1.rename(columns={"Enter the full company name": "Company",
                     "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1"},inplace=True)
    
    masknz1 = tghg1['Company'].isin(company_list)
    tghg1_sel10 = tghg1[masknz1].sort_values(by='Total GHG1', axis=0, ascending=False)
    tghg1_sel10['Total GHG1'] = tghg1_sel10['Total GHG1']/1000
    
    fig22 = px.bar(tghg1_sel10, x='Company', y='Total GHG1',text='Total GHG1',color_discrete_sequence=['#2774AE'],height = 780)
    fig22.update_layout(plot_bgcolor="white", font_family='Helvetica',
                        title_font_family="Helvetica",font=dict(size=22))
    fig22.update_xaxes(title=None)
    fig22.update_yaxes(title=None)
    fig22.update_layout(
    title=go.layout.Title(
        text="Total GHG Scope 1 Emissions<br><sup>(in kilo-metric tons)</sup>",
        #xref="paper",
        x=0.5,
        font_size=30
    ))
    fig22.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tghg1_sel10['Company'].unique().tolist()]
    fig22.update_xaxes(tickmode='array', tickvals=list(range(len(tghg1_sel10['Company'].unique().tolist()))), ticktext=wrapped_labels)
    
    return fig22


def nghg1(sector,company_list):
    tghg1 = dfnz2.loc[:,['Enter the full company name', 'What is the company\'s current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)']]
    tghg1.rename(columns={"Enter the full company name": "Company",
                     "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1"},inplace=True)
    
    masknz1 = tghg1['Company'].isin(company_list)
    tghg1_sel10 = tghg1[masknz1].sort_values(by='Total GHG1', axis=0, ascending=False)
    tghg1_sel10['Total GHG1'] = tghg1_sel10['Total GHG1']/1000
    tnghg1 = df.loc[:,['Company.Name','Revenue']]
    tnghg1 = tnghg1.rename(columns={"Company.Name":"Company"})
    masknz11 = tnghg1['Company'].isin(company_list)
    tnghg1 = tnghg1[masknz11]
    
    tnghg1_merged = tnghg1.merge(tghg1_sel10,on='Company')
    tnghg1_merged['Normalised GHG1'] = tnghg1_merged['Total GHG1']*1000/tnghg1_merged['Revenue']
    tnghg1_merged['Normalised GHG1 Rounded'] = pd.to_numeric(tnghg1_merged['Normalised GHG1']).round(2)
    tnghg1_merged = tnghg1_merged.sort_values(by='Normalised GHG1', ascending=False)

    
    fig2 = px.bar(tnghg1_merged, x='Company', y='Normalised GHG1',text='Normalised GHG1 Rounded',color_discrete_sequence=['#2774AE'],height = 780)
    fig2.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",font=dict(size=22))
    fig2.update_xaxes(title=None)
    fig2.update_yaxes(title=None)
    fig2.update_layout(
    title=go.layout.Title(
        text="Normalised GHG Scope 1 Emissions<br><sup>(in metric tons per $M revenue)</sup>",
        #xref="paper",
        x=0.5,
        font_size=30
    ))
    fig2.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tnghg1_merged['Company'].unique().tolist()]
    fig2.update_xaxes(tickmode='array', tickvals=list(range(len(tnghg1_merged['Company'].unique().tolist()))), ticktext=wrapped_labels)

    
    return fig2

def tghg2(sector,company_list):
    tghg2 = dfnz2.loc[:,['Enter the full company name', 'Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)',
                     'Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)',
                     'Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)' ]]
    tghg2.rename(columns={"Enter the full company name": "Company",
                     "Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
                     "Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)":"Total location-based GHG 2",
                     "Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)":"Total uncategorised GHG 2"},inplace=True)

    
    masknz2 = tghg2['Company'].isin(company_list)
    tghg2 = tghg2[masknz2]
    tghg2_melted = pd.melt(tghg2, id_vars='Company')
    #tghg2_melted[['Scope 2 type']] = re.search(r'Total(.*?)GHG', tghg2_melted['variable'])
    tghg2_melted['Scope 2 Category'] = tghg2_melted['variable'].apply(lambda x: re.search(r'Total(.*?)GHG', x).group(1).strip() if re.search(r'Total(.*?)GHG', x) else None)
    tghg2_melted['value'] = pd.to_numeric(tghg2_melted['value']/1000, errors='coerce')
    tghg2_melted['value_rounded'] = (tghg2_melted['value']).round(2).astype(str).str.replace('nan', 'NR')

    tghg2_melted = tghg2_melted.sort_values(by='value', axis=0, ascending=False)

    
    fig32 = px.bar(tghg2_melted, x="Company", y="value", 
                 color="Scope 2 Category", barmode="group",text='value_rounded',
              color_discrete_sequence=['#F47C30','#2774AE','#FFB81C'],height = 780)
#fig2 = px.bar(dfghg1_sorted, x='CompanyName', y='Value',text='value_rounded',color_discrete_sequence=['#2774AE'])
    fig32.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
                  font=dict(size=22), uniformtext_mode='hide',
                  legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="left",
                      x=0.85                      
                  ),
                  xaxis=dict(categoryorder='array', categoryarray= tghg2_melted["Company"].unique()))

    fig32.update_xaxes(title=None)
    fig32.update_yaxes(title=None)
    fig32.update_layout(
    title=go.layout.Title(
        text="Total GHG Scope 2 Emissions<br><sup>(in kilo-metric tons)</sup>",
        #xref="paper",
        x=0.5,
        font_size = 30
    ))
    fig32.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tghg2_melted['Company'].unique().tolist()]

    fig32.update_xaxes(tickmode='array', tickvals=list(range(len(tghg2_melted['Company'].unique().tolist()))), ticktext=wrapped_labels)
    
    return fig32


def nghg2(sector,company_list):
    tghg2 = dfnz2.loc[:,['Enter the full company name', 'Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)',
                     'Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)',
                     'Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)' ]]
    tghg2.rename(columns={"Enter the full company name": "Company",
                     "Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
                     "Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)":"Total location-based GHG 2",
                     "Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)":"Total uncategorised GHG 2"},inplace=True)

    
    masknz2 = tghg2['Company'].isin(company_list)
    tghg2 = tghg2[masknz2]
    
    tnghg2 = df.loc[:,['Company.Name','Revenue']]
    tnghg2 = tnghg2.rename(columns={"Company.Name":"Company"})
    masknz22 = tnghg2['Company'].isin(company_list)
    tnghg2 = tnghg2[masknz22]
    
    tnghg2_merged = tnghg2.merge(tghg2,on='Company')
    tnghg2_merged['Normalised market-based GHG2'] = tnghg2_merged['Total market-based GHG2']/tnghg2_merged['Revenue']
    tnghg2_merged['Normalised location-based GHG2'] = tnghg2_merged['Total location-based GHG 2']/tnghg2_merged['Revenue']
    tnghg2_merged['Normalised uncategorised GHG2'] = tnghg2_merged['Total uncategorised GHG 2']/tnghg2_merged['Revenue']
    tnghg2_merged.drop(labels=['Revenue','Total market-based GHG2','Total location-based GHG 2','Total uncategorised GHG 2'], axis=1, inplace=True)
    
    tnghg2_melted = pd.melt(tnghg2_merged, id_vars='Company')
#tghg2_melted[['Scope 2 type']] = re.search(r'Total(.*?)GHG', tghg2_melted['variable'])
    tnghg2_melted['Scope 2 Category'] = tnghg2_melted['variable'].apply(lambda x: re.search(r'Normalised(.*?)GHG', x).group(1).strip() if re.search(r'Normalised(.*?)GHG', x) else None)
    tnghg2_melted['value'] = pd.to_numeric(tnghg2_melted['value'], errors='coerce')
    tnghg2_melted['value_rounded'] = (tnghg2_melted['value']).round(2).astype(str).str.replace('nan', 'NR')

    tnghg2_melted = tnghg2_melted.sort_values(by='value', axis=0, ascending=False)

    
    fig322 = px.bar(tnghg2_melted, x="Company", y="value",
                    color="Scope 2 Category", barmode="group",text='value_rounded',color_discrete_sequence=['#F47C30','#2774AE','#FFB81C'],height = 780)
    fig322.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
                  font=dict(size=22), uniformtext_mode='hide',
                  legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="left",
                      x=0.85                      
                  ),
                  xaxis=dict(categoryorder='array', categoryarray= tnghg2_melted["Company"].unique()))

    fig322.update_xaxes(title=None)
    fig322.update_yaxes(title=None)
    fig322.update_layout(
    title=go.layout.Title(
        text="Normalised GHG Scope 2 Emissions<br><sup>(in metric tons per $M revenue)</sup>",
        #xref="paper",
        x=0.5,
        font_size = 30
    ))
    fig322.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tnghg2_melted['Company'].unique().tolist()]
# a = wrapped_labels[6]
# wrapped_labels[6] = wrapped_labels[7]

    fig322.update_xaxes(tickmode='array', tickvals=list(range(len(tnghg2_melted['Company'].unique().tolist()))), ticktext=wrapped_labels)
    return fig322

def category_label(row):
    column_numbers = row['Company']
    
    for i in range(7- column_numbers.count(' ') - column_numbers.count('-')):
        column_numbers = column_numbers + '<br>'
    
    column_numbers = column_numbers + '<b><i>Categories Included: </i></b>'
    
    column_numbers_all = column_numbers
    
    # Iterate over the columns from Category 1 to Category 15
    sp = 0
    tv = 0
    for i in range(1, 16):
        column_name = f'Category {i}'
        if row[column_name] == 'Yes':
            column_numbers = column_numbers + str(i) + ","
            sp = sp + len(str(i)) + 2
            tv = tv + 1
        if (sp >= 8):
            column_numbers = column_numbers + "<br>"
            sp = 0
            
    if (tv == 0):
        column_numbers = column_numbers + 'Categories not identified'
    elif (tv == 15):
        column_numbers = column_numbers_all + 'All'
    else:
        column_numbers = column_numbers[:column_numbers.rfind(',')]
    # Return the list of column numbers as a string
    return column_numbers



def tnghg3(sector,company_list,k1):
    k2 = k1 + " Rounded"
    k3 = k1[:-1] + " Scope 3 Emissions<br><sup>(in metric tons per $M revenue)</sup>"
    tghg3 = dfnz2.loc[:,['Enter the full company name', 'Enter the company\'s Scope 3 emissions in metric tons of CO2e.',
                  'Does the company report Category 1 (purchased goods and services) emissions?',
                  'Does the company report Category 2 (capital goods) emissions?',
                  'Does the company report Category 3 (fuel and energy related activities) emissions?',
                  'Does the company report Category 4 (upstream transportation and distribution) emissions?',
                  'Does the company report Category 5 (waste generated in operations) emissions?',
                  'Does the company report Category 6 (business travel) emissions?',
                  'Does the company report Category 7 (employee commuting) emissions?',
                  'Does the company report Category 8 (upstream leased assets) emissions?',
                  'Does the company report Category 9 (downstream transportation and distribution) emissions?',
                  'Does the company report Category 10 (processing of sold products) emissions?',
                  'Does the company report Category 11 (use of sold products) emissions?',
                  'Does the company report Category 12 (end-of-life treatment of sold products) emissions?',
                  'Does the company report Category 13 (downstream leased assets) emissions?',
                  'Does the company report Category 14 (franchises) emissions?',
                  'Does the company report Category 15 (investments) emissions?']]
    tghg3.rename(columns={'Enter the full company name': 'Company',
                     'Enter the company\'s Scope 3 emissions in metric tons of CO2e.':'Total GHG3',
                  'Does the company report Category 1 (purchased goods and services) emissions?':'Category 1',
                  'Does the company report Category 2 (capital goods) emissions?':'Category 2',
                  'Does the company report Category 3 (fuel and energy related activities) emissions?':'Category 3',
                  'Does the company report Category 4 (upstream transportation and distribution) emissions?':'Category 4',
                  'Does the company report Category 5 (waste generated in operations) emissions?':'Category 5',
                  'Does the company report Category 6 (business travel) emissions?':'Category 6',
                  'Does the company report Category 7 (employee commuting) emissions?':'Category 7',
                  'Does the company report Category 8 (upstream leased assets) emissions?':'Category 8',
                  'Does the company report Category 9 (downstream transportation and distribution) emissions?':'Category 9',
                  'Does the company report Category 10 (processing of sold products) emissions?':'Category 10',
                  'Does the company report Category 11 (use of sold products) emissions?':'Category 11',
                  'Does the company report Category 12 (end-of-life treatment of sold products) emissions?':'Category 12',
                  'Does the company report Category 13 (downstream leased assets) emissions?':'Category 13',
                  'Does the company report Category 14 (franchises) emissions?':'Category 14',
                  'Does the company report Category 15 (investments) emissions?':'Category 15'},inplace=True)

    
    masknz3 = tghg3['Company'].isin(company_list)
    tghg3_sel10 = tghg3[masknz3].sort_values(by='Total GHG3', axis=0, ascending=False)
    tghg3_sel10['Total GHG3'] = tghg3_sel10['Total GHG3']/1000
    tghg3_sel10['Total GHG3 Rounded'] = tghg3_sel10['Total GHG3'].round(2)


    masknan = (tghg3_sel10['Company'] == 'The Hershey Company') | (tghg3_sel10['Company'] == 'PepsiCo, Inc.')
    tghg3_sel10.loc[masknan]=tghg3_sel10.loc[masknan].fillna('Yes')
    #tghg3_sel10 = tghg3_sel10.fillna(0)

    tnghg3 = df.loc[:,['Company.Name','Revenue']]
    tnghg3 = tnghg3.rename(columns={"Company.Name":"Company"})
    masknz33 = tnghg3['Company'].isin(company_list)
    tnghg3 = tnghg3[masknz33]
    
    tnghg33_merged = tghg3_sel10.merge(tnghg3, on='Company')
    tnghg33_merged['Normalised GHG3'] = (tnghg33_merged['Total GHG3']*1000)/tnghg33_merged['Revenue']
    tnghg33_merged['Normalised GHG3 Rounded'] = tnghg33_merged['Normalised GHG3'].round(2)
    
    tnghg33_merged = tnghg33_merged.sort_values(by=['Total GHG3','Company'], axis = 0, ascending=False)

    # Apply the function to each row of the DataFrame
    tnghg33_merged['Modified Labels'] = tnghg33_merged.apply(category_label, axis=1)


    tnghg33_merged = tnghg33_merged.sort_values(by=[k1,'Company'], axis = 0, ascending=False)
    
    fig2 = px.bar(tnghg33_merged, x='Modified Labels', y=k1,text=k2 ,color_discrete_sequence=['#2774AE'], height = 1000)
    fig2.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",font=dict(size=18))
    fig2.update_xaxes(title=None)
    fig2.update_yaxes(title=None)
    fig2.update_layout(
    title=go.layout.Title(
        text=k3,
        #xref="paper",
        x=0.5,
        font_size=30
    ))
    fig2.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tnghg33_merged['Modified Labels'].unique().tolist()]
    fig2.update_xaxes(tickmode='array', tickvals=list(range(len(tnghg33_merged['Modified Labels'].unique().tolist()))), ticktext=wrapped_labels)


    return fig2



def water_util(sector,company_list):
    dfwwc = dfpivot.loc[((dfpivot['GICS Sector'] == sector) & (dfpivot['Cleaned_names'] == 'Withdrawals in mega litres per $M revenue')) |
                    ((dfpivot['GICS Sector'] == sector) & (dfpivot['Cleaned_names'] == 'Consumption in mega litres per $M revenue'))
                ,['CompanyName','Value','Cleaned_names']]
    dfwwc['value_rounded'] = dfwwc['Value'].round(2).astype(str).str.replace('nan', 'NR')
    dfwwc['Cleaned_names'] = dfwwc['Cleaned_names'].replace('Withdrawals in mega litres per $M revenue', 'Withdrawal')
    dfwwc['Cleaned_names'] = dfwwc['Cleaned_names'].replace('Consumption in mega litres per $M revenue', 'Consumption')
    
    mask12 = dfwwc['CompanyName'].isin(company_list)
    dfwwc_prev10 = dfwwc[mask12].sort_values(by='Value', axis=0, ascending=False)
    
    fig8 = px.bar(dfwwc_prev10, x='CompanyName', y='Value',color='Cleaned_names',text='value_rounded',color_discrete_sequence=['#2774AE','#F47C30'],height = 780, barmode='group')
    fig8.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",font=dict(size=22),
                  legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="left",
                      x=0.85                      
                  ))
    fig8.update_xaxes(title=None)
    fig8.update_yaxes(title=None)
    fig8.update_layout(
        title=go.layout.Title(
            text="Water Utilization<br><sup>(in mega litres per $M revenue)</sup>",
            #xref="paper",
            x=0.5,
            font_size=30
        ))
    fig8.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in dfwwc_prev10['CompanyName'].unique().tolist()]
    fig8.update_xaxes(tickmode='array', tickvals=list(range(len(dfwwc_prev10['CompanyName'].unique().tolist()))), ticktext=wrapped_labels)

    return fig8


def biodiver(sector,company_list):
    dfbi = dfpivot.loc[(dfpivot['GICS Sector'] == sector) & (dfpivot['Cleaned_names'] == 'Area in hectares per $M revenue')
                ,['CompanyName','Value']]
    dfbi['value_rounded'] = dfbi['Value'].round(2).astype(str).str.replace('nan', 'NR')
    dfbi_sorted = dfbi.sort_values(by='Value', axis=0, ascending=False).head(10)
    mask7 = dfbi['CompanyName'].isin(company_list)
    dfbi_prev10 = dfbi[mask7].sort_values(by='Value', axis=0, ascending=False)
    
    fig7 = px.bar(dfbi_prev10, x="CompanyName", y="Value",text='value_rounded',
              color_discrete_sequence=['#2774AE','#FFB81C','#F47C30'],barmode="group", height = 780)
    fig7.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
                  font=dict(size=22))


    fig7.update_xaxes(title=None)
    fig7.update_yaxes(title=None)
    fig7.update_layout(
    title=go.layout.Title(
        text="Biodiversity Areas<br><sup>(in hectares per $M revenue)</sup>",
        #xref="paper",
        x=0.5,
        font_size = 30
    ))
    fig7.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in dfbi_prev10['CompanyName'].unique().tolist()]
    fig7.update_xaxes(tickmode='array', tickvals=list(range(len(dfbi_prev10['CompanyName'].unique().tolist()))), ticktext=wrapped_labels)

    return fig7


def enviromentalgovernacemetrics(sector,company_list):
    emg1 = df.loc[:,['Company.Name', 'Audited.Report','TCFD New']]
    emg1.rename(columns={"Company.Name": "Company",
                     "Audited.Report": "GHG Assurance",
                     "TCFD New":"TCFD Disclosure"},inplace=True)

    mask = emg1['Company'].isin(company_list)
    emg1 = emg1[mask]

    categorical_mapping = {1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'}
    emg1['GHG Assurance'] = emg1['GHG Assurance'].map(categorical_mapping)
    emg1['TCFD Disclosure'] = emg1['TCFD Disclosure'].map(categorical_mapping)
    
    emg2 = dfnz2.loc[:,['Enter the full company name','Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?', 'Is Executive Compensation tied to any ESG milestones?']]
    emg2.rename(columns={"Enter the full company name": "Company",
                     "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?": "Environmental Skill as key board competency",
                     "Is Executive Compensation tied to any ESG milestones?":"Executive Compensation tied to ESG milestones"},inplace=True)

    mask = emg2['Company'].isin(company_list)
    emg2 = emg2[mask]
    
    emg = emg1.merge(emg2, on='Company')
    
    emg_melted = emg.melt(id_vars = 'Company', var_name='Metric', value_name='Status')
    emg_melted = emg_melted.sort_values(by=['Metric','Company'])
    
    fig = px.scatter(emg_melted, y="Company", x="Metric", color="Status",
                 color_discrete_sequence=['#4E7E6B','#F43A00','#FFD100','#2774AE'],height = 920, 
                 title='Environmental Metrics Governance: Consumer Staples')
    fig.update_traces(marker_size=34)
    fig.update_layout(plot_bgcolor="white", font=dict(family="Verdana",size=19), title_font_family="Helvetica", title_x=0.5,
                 legend=dict( yanchor="bottom",orientation="h",  xanchor="right", x=1, title=None),
                 margin=dict(t=190),title_font_size=30,xaxis_tickformat='wrap',
                 xaxis=dict(side="top",categoryorder='array', categoryarray= emg_melted["Company"].unique()))
    fig.update_yaxes(title=None)
    fig.update_xaxes(categoryorder='category ascending',title=None, tickformat='wrap')

    max_label_length = 20
    wrapped_labels = [label[:[m.start() for m in re.finditer(r' ', label)][2]] + '<br>' + label[[m.start() for m in re.finditer(r' ', label)][2]:] if label.find(' ')>5 else label for label in emg_melted['Metric'].unique().tolist()]
    fig.update_xaxes(tickmode='array', tickvals=list(range(len(emg_melted['Metric'].unique().tolist()))), ticktext=wrapped_labels)

    fig.add_shape(
        type="line",
        x0=0,
        y0=1,
        x1=1,
        y1=1,
        line=dict(
            color="black",
            width=1,
        ),
        xref="paper",
        yref="paper"
    )
    
    return fig


def tcfdpercentage(sector,company_list):
    tcfd = df.loc[:,['Company.Name','TCFD average']]
    tcfd.rename(columns={"Company.Name": "Company"},inplace=True)

    tcfd['TCFD average'] = tcfd['TCFD average']*100
    tcfd['label'] = tcfd['TCFD average'].astype(int).astype(str) + '%'

    mask = tcfd['Company'].isin(company_list)
    tcfd = tcfd[mask].sort_values(by=['TCFD average','Company'],ascending=False)
    
    fig7 = px.bar(tcfd, x='Company', y='TCFD average',text='label',
              color_discrete_sequence=['#003B5C'],barmode="group")
    fig7.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica")
    fig7.update_xaxes(title=None)
    fig7.update_yaxes(title=None)
    fig7.update_layout(
        title=go.layout.Title(
            text="TCFD Disclosure Percentage<br><sup></sup>",
            #xref="paper",
            x=0.5
        ))
    fig7.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tcfd['Company'].unique().tolist()]
    fig7.update_xaxes(tickmode='array', tickvals=list(range(len(tcfd['Company'].unique().tolist()))), ticktext=wrapped_labels)

    fig7.update_layout(height = 780,font_family='Helvetica', title_font_family="Helvetica",font=dict(size=22))
    
    return fig7


def boardmember(sector,company_list):
    
    pobm = dfnz2.loc[:,['Enter the full company name','Percent of board with enviro skill']]
    pobm.rename(columns={"Enter the full company name": "Company",
                    "Percent of board with enviro skill":"pobm"},inplace=True)

    pobm['pobm'] = pobm['pobm']*100
    pobm['label'] = pobm['pobm'].astype(int).astype(str) + '%'

    mask = pobm['Company'].isin(company_list)
    pobm = pobm[mask].sort_values(by=['pobm','Company'],ascending=False)
    
    fig8 = px.bar(pobm, x='Company', y='pobm',text='label',
              color_discrete_sequence=['#003B5C'],barmode="group")
    fig8.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica")
    fig8.update_xaxes(title=None)
    fig8.update_yaxes(title=None)
    fig8.update_layout(
        title=go.layout.Title(
            text="Percentage of board members with Environmental/Sustainability Capabilities<br><sup></sup>",
            #xref="paper",
            x=0.5
        ))
    fig8.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in pobm['Company'].unique().tolist()]
    fig8.update_xaxes(tickmode='array', tickvals=list(range(len(pobm['Company'].unique().tolist()))), ticktext=wrapped_labels)

    fig8.update_layout(height = 780,font_family='Helvetica', title_font_family="Helvetica",font=dict(size=22))
    
    return fig8


def environmentalgoals(sector,company_list):
    egoal = dfnz2.loc[:,['Enter the full company name',
                     'Does the company have a Net Zero/carbon neutrality goal?',
                     'Does the Net Zero goal cover Scope 1 emissions?',
                     'Does the Net Zero goal cover Scope 2 emissions?',
                     'Does the Net Zero goal cover all of Scope 3 emissions?',
                     'Is the company on the Science Based Targets Institute as working with them to develop or track it\'s Net Zero Goal?',
                     'What is the status of the company\'s goal with the Science Based Target Institute?',
                     'Does the company have an interim goal on the way to Net Zero?',
                     'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?']]
    egoal.rename(columns={"Enter the full company name": "Company",
                     "Does the company have a Net Zero/carbon neutrality goal?": "Has a Net Zero Goal (NZG)",
                     "Does the Net Zero goal cover Scope 1 emissions?":"NZG covers Scope 1 emissions",
                     "Does the Net Zero goal cover Scope 2 emissions?":"NZG covers Scope 2 emissions",
                     "Does the Net Zero goal cover all of Scope 3 emissions?":"NZG covers all of Scope 3 emissions",
                     "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?":"Working with the SBTI ",
                     "What is the status of the company's goal with the Science Based Target Institute?":"Status of the goal with SBTI",
                     "Does the company have an interim goal on the way to Net Zero?":"Has an interim goal on the way to Net Zero",
                     "Does the proxy statement mention \"Net Zero\" or \"Carbon neutral\" targets?":"\"Net Zero\" or \"Carbon neutral\" mentioned in Proxy Statement"},inplace=True)

    mask = egoal['Company'].isin(company_list)
    egoal = egoal[mask].fillna('Not Applicable')

    egoal.loc[222,'"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = 'Not Applicable'

    egoal.sort_values(by='Company')
    
    egoal_melted = egoal.melt(id_vars = 'Company', var_name='Metric', value_name='Status')
    egoal_melted = egoal_melted.sort_values(by=['Metric','Company'])
    
    column_order = ['Has a Net Zero Goal (NZG)',
                'NZG covers Scope 1 emissions',
                'NZG covers Scope 2 emissions',
                'NZG covers all of Scope 3 emissions',
                'Working with the SBTI ',
                'Status of the goal with SBTI',
                'Has an interim goal on the way to Net Zero',
                '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement']
    
    fig9 = px.scatter(egoal_melted, y="Company", x="Metric", color="Status",
                 color_discrete_sequence=['#4E7E6B','#F43A00','#313339','#2774AE','#FFD100'],height = 920, 
                 title='Environmental Goals: Consumer Staples')
    fig9.update_traces(marker_size=34)
    fig9.update_layout(plot_bgcolor="white", font=dict(family="Verdana",size=19), title_font_family="Helvetica", title_x=0.5,
                 legend=dict( yanchor="bottom",orientation="h",  xanchor="right", x=1, title=None),
                 margin=dict(t=190),title_font_size=30,xaxis_tickformat='wrap',
                 xaxis=dict(side="top",categoryorder='array', categoryarray= column_order))
    fig9.update_yaxes(title=None)
    fig9.update_xaxes(title=None, tickformat='wrap')

    max_label_length = 20
    wrapped_labels = [label[:[m.start() for m in re.finditer(r' ', label)][3]] + '<br>' + label[[m.start() for m in re.finditer(r' ', label)][3]:] if label.find(' ')>0 else label for label in column_order]
    p = wrapped_labels[7]
    wrapped_labels[7] = [p[:[m.start() for m in re.finditer(r' ', p)][5]] + '<br>' + p[[m.start() for m in re.finditer(r' ', p)][5]:]]
# p = wrapped_labels[7]
# wrapped_labels[7] = [p[:[m.start() for m in re.finditer(r' ', p)][4]] + '<br>' + p[[m.start() for m in re.finditer(r' ', p)][4]:]]
    fig9.update_xaxes(tickmode='array', tickvals=list(range(len(egoal_melted['Metric'].unique().tolist()))), ticktext=wrapped_labels)

    fig9.add_shape(
        type="line",
        x0=0,
        y0=1,
        x1=1,
        y1=1,
        line=dict(
            color="black",
            width=1,
        ),
        xref="paper",
        yref="paper"
    )
    
    return fig9

def netzerotarget(sector,company_list):
    dfty2 = dfnz2.loc[:,['Enter the full company name',
                     'Average NZ Target Year']].fillna(2015)
    dfty2.loc[311,'Average NZ Target Year'] = 2050



    dfty2['Average NZ Target Year'] = dfty2['Average NZ Target Year'].astype(int)
    dfty2['barlabel'] = dfty2['Average NZ Target Year'].astype(str).str.replace('2015', 'No NZ Goal')

    mask = dfty2['Enter the full company name'].isin(company_list)
    dfty2 = dfty2[mask].sort_values(by=['Average NZ Target Year','Enter the full company name'])

    dfty2['Enter the full company name'] = dfty2['Enter the full company name'].apply(lambda x: x + '   ')
    
    fig29 = px.bar(dfty2, y='Enter the full company name', x='Average NZ Target Year',text='barlabel',color_discrete_sequence=['#003B5C'],barmode="group")
    fig29.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica")
    fig29.update_xaxes(title=None,range=[2014.99, 2062], showgrid=True, gridcolor='lightgrey')
    fig29.update_yaxes(title=None)
    fig29.update_layout(
        title=go.layout.Title(
            text="Net Zero Target<br><sup></sup>",
            #xref="paper",
            x=0.5
        ))
    fig29.update_traces(textposition='outside', selector=dict(type='bar'))

    fig29.update_layout( height = 780,font_family='Helvetica', title_font_family="Helvetica",font=dict(size=22))
    
    return fig29





navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='/assets/Impact_Logo_Wht_PMScoated.png', height="30px"))
                    ],
                    align="center",
                    className="g-0",
                ),
                href="#",
                style={"textDecoration": "none"},
            ),
            dbc.Row(
                    [dbc.Col(dbc.NavbarBrand("OFG Case Study", className="ms-2")),
                     dbc.Col(width=1)
                    ],
                    align="center",
                    className="g-0",
                ),
            html.A()
        ],fluid=True
    ),
    color="#313339",
    dark=True,
)


card11=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select')
                ,width=12)
            ])
        ])
    
],className="m-1")

card12=dbc.Card([
    dbc.CardHeader("Disclosure Status for Consumer Staples Environmental Metrics",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="trafficlight"))])
                ])
    
],className="m-1")

card21=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select2')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select2')
                ,width=12)
            ])
        ])
    
],className="m-1")

card22=dbc.Card([
    dbc.CardHeader("GHG Scope 1 Emissions",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tghg1"))]),
            dbc.Row([dbc.Col(dcc.Graph(id="nghg1"))])
                ])
    
],className="m-1")

card31=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select3')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select3')
                ,width=12)
            ])
        ])
    
],className="m-1")

card32=dbc.Card([
    dbc.CardHeader("GHG Scope 2 Emissions",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tghg2"))]),
            dbc.Row([dbc.Col(dcc.Graph(id="nghg2"))])
                ])
    
],className="m-1")


card41=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select4')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select4')
                ,width=12)
            ])
        ])
    
],className="m-1")

card42=dbc.Card([
    dbc.CardHeader("GHG Scope 3 Emissions",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tghg3"))]),
            dbc.Row([dbc.Col(dcc.Graph(id="nghg3"))])
                ])
    
],className="m-1")

card51=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select5')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select5')
                ,width=12)
            ])
        ])
    
],className="m-1")

card52=dbc.Card([
    dbc.CardHeader("Water Utilization",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="wu"))])
                ])
    
],className="m-1")

card61=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select6')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select6')
                ,width=12)
            ])
        ])
    
],className="m-1")

card62=dbc.Card([
    dbc.CardHeader("Biodiversity Areas",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="biod"))])
                ])
    
],className="m-1")

card71=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select7')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select7')
                ,width=12)
            ])
        ])
    
],className="m-1")

card72=dbc.Card([
    dbc.CardHeader("Governance Metrics",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="envmetgov"))])
                ])
    
],className="m-1")

card81=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select8')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select8')
                ,width=12)
            ])
        ])
    
],className="m-1")

card82=dbc.Card([
    dbc.CardHeader("TCFD Disclosure Percentage",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tcfdper"))])
                ])
    
],className="m-1")


card91=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select9')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select9')
                ,width=12)
            ])
        ])
    
],className="m-1")

card92=dbc.Card([
    dbc.CardHeader("Percentage of board memebers with Environmental/Sustainability Capabilities",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="boardmem"))])
                ])
    
],className="m-1")


card101=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select10')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select10')
                ,width=12)
            ])
        ])
    
],className="m-1")

card102=dbc.Card([
    dbc.CardHeader("Environmental Goals",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="envigoals"))])
                ])
    
],className="m-1")


card111=dbc.Card([
    dbc.CardHeader("Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Sector",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in set(df['GICS.Sector'].tolist()) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select11')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Companies",style={ 'display': 'flex',  'justify-content':'center'})],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select11')
                ,width=12)
            ])
        ])
    
],className="m-1")

card112=dbc.Card([
    dbc.CardHeader("Net Zero Targets",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="nztar"))])
                ])
    
],className="m-1")


app.layout = html.Div([
    dbc.Row([dbc.Col(navbar)],className="mb-4"),
    dbc.Row([dbc.Col([card11],width=3),dbc.Col([card12],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card21],width=3),dbc.Col([card22],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card31],width=3),dbc.Col([card32],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card41],width=3),dbc.Col([card42],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card51],width=3),dbc.Col([card52],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card61],width=3),dbc.Col([card62],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card71],width=3),dbc.Col([card72],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card81],width=3),dbc.Col([card82],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card91],width=3),dbc.Col([card92],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card101],width=3),dbc.Col([card102],width=9)],className="mb-4 ml-3"),
    dbc.Row([dbc.Col([card111],width=3),dbc.Col([card112],width=9)],className="mb-4 ml-3")
])

@callback(
    [Output('company_select', 'options'),
     Output('company_select', 'value')],
    [Input('sector_select', 'value')]
)
def update_companylist(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('trafficlight', 'figure'),
    [State('sector_select', 'value')],
    [Input('company_select', 'value')]
)
def update_statew(sector,company_list):
    fig=trafficlight(sector,company_list)
    return fig

@callback(
    [Output('company_select2', 'options'),
     Output('company_select2', 'value')],
    [Input('sector_select2', 'value')]
)
def update_companylist2(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    [Output('tghg1', 'figure'),
     Output('nghg1', 'figure')],
    [State('sector_select2', 'value')],
    [Input('company_select2', 'value')]
)
def update_tghg1(sector,company_list):
    fig=tghg1(sector,company_list)
    fig2=nghg1(sector,company_list)
    return fig, fig2

@callback(
    [Output('company_select3', 'options'),
     Output('company_select3', 'value')],
    [Input('sector_select3', 'value')]
)
def update_companylist3(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    [Output('tghg2', 'figure'),
     Output('nghg2', 'figure')],
    [State('sector_select3', 'value')],
    [Input('company_select3', 'value')]
)
def update_tghg2(sector,company_list):
    fig32=tghg2(sector,company_list)
    fig322=nghg2(sector,company_list)
    return fig32, fig322

@callback(
    [Output('company_select4', 'options'),
     Output('company_select4', 'value')],
    [Input('sector_select4', 'value')]
)
def update_companylist4(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    [Output('tghg3', 'figure'),
     Output('nghg3', 'figure')],
    [State('sector_select4', 'value')],
    [Input('company_select4', 'value')]
)
def update_tghg3(sector,company_list):
    fignorm=tnghg3(sector,company_list,"Normalised GHG3")
    figtotal=tnghg3(sector,company_list,"Total GHG3")
    return fignorm, figtotal

@callback(
    [Output('company_select5', 'options'),
     Output('company_select5', 'value')],
    [Input('sector_select5', 'value')]
)
def update_companylist5(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('wu', 'figure'),
    [State('sector_select5', 'value')],
    [Input('company_select5', 'value')]
)
def update_wu(sector,company_list):
    figu=water_util(sector,company_list)
    return figu

@callback(
    [Output('company_select6', 'options'),
     Output('company_select6', 'value')],
    [Input('sector_select6', 'value')]
)
def update_companylist6(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('biod', 'figure'),
    [State('sector_select6', 'value')],
    [Input('company_select6', 'value')]
)
def update_biod(sector,company_list):
    figb=biodiver(sector,company_list)
    return figb


@callback(
    [Output('company_select7', 'options'),
     Output('company_select7', 'value')],
    [Input('sector_select7', 'value')]
)
def update_companylist7(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('envmetgov', 'figure'),
    [State('sector_select7', 'value')],
    [Input('company_select7', 'value')]
)
def update_envmetgov(sector,company_list):
    figgvnmet=enviromentalgovernacemetrics(sector,company_list)
    return figgvnmet

@callback(
    [Output('company_select8', 'options'),
     Output('company_select8', 'value')],
    [Input('sector_select8', 'value')]
)
def update_companylist8(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('tcfdper', 'figure'),
    [State('sector_select8', 'value')],
    [Input('company_select8', 'value')]
)
def update_tcfdper(sector,company_list):
    figtcfdper=tcfdpercentage(sector,company_list)
    return figtcfdper

@callback(
    [Output('company_select9', 'options'),
     Output('company_select9', 'value')],
    [Input('sector_select9', 'value')]
)
def update_companylist9(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('boardmem', 'figure'),
    [State('sector_select9', 'value')],
    [Input('company_select9', 'value')]
)
def update_boardmem(sector,company_list):
    figboardmem=boardmember(sector,company_list)
    return figboardmem

@callback(
    [Output('company_select10', 'options'),
     Output('company_select10', 'value')],
    [Input('sector_select10', 'value')]
)
def update_companylist10(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('envigoals', 'figure'),
    [State('sector_select10', 'value')],
    [Input('company_select10', 'value')]
)
def update_envigoals(sector,company_list):
    figenvigoals=environmentalgoals(sector,company_list)
    return figenvigoals

@callback(
    [Output('company_select11', 'options'),
     Output('company_select11', 'value')],
    [Input('sector_select11', 'value')]
)
def update_companylist11(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('nztar', 'figure'),
    [State('sector_select11', 'value')],
    [Input('company_select11', 'value')]
)
def update_nztar(sector,company_list):
    fignztar=netzerotarget(sector,company_list)
    return fignztar



if __name__ == '__main__':
    app.run(debug=True, port=8000)
