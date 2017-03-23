# -*- coding: utf-8 -*-
"""
Created on Tue Feb 07 21:52:32 2017

@author: HengLiu
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
imoport os

os.chdir('/media/heng/Software/Dropbox/Schoolpredict')
gter = pd.read_csv('gter.csv')

gter = pd.read_excel('C:/Users/Yunpeng/Desktop/Schoolpredict/all-gter-processed_reviewd and modified.xls')
# drop columns not interested
gter.drop([u'Registration_Date', u'Url', u'School ID', u'Sub_Date'], axis=1, inplace=True)
# keep data where school name is available
gter = gter[gter['School'].notnull()]

# detect the language of school names, should be only English and Chinese
# but sometimes English is detected as other languages (roughly 90% accuracy)
from langdetect import detect

#create a column to store the language type of school name
gter.loc[:,'lang'] = pd.Series() 
for index, value in gter.iterrows():
    gter.loc[index,'lang'] = detect(gter.loc[index,'School'])

# translate those non-English school names to English
# create a column to store the translated results
gter.loc[:,'translate'] = pd.Series()

# the langdetect are not very accurate, usually 'zh-cn' and 'ko' are chinese
gter_translate = gter[(gter['lang'] == 'zh-cn') | (gter['lang'] == 'ko')]
                      
# a limit of 1000 words/day free usage for translate package
from translate import Translator 
translator = Translator(to_lang="en", from_lang="zh")
for index, value in gter_translate.iterrows():
    gter.loc[index,'translate'] = translator.translate(gter_translate.loc[index,'School'].encode('UTF-8')) 
    # use translated results to update the non-English name
    gter.loc[index, 'School'] = gter.loc[index,'translate'] 

#%%
# Adjust school names using google api

# school name can be incomplete, we use google api to automatically complete the name
# to better use the api, add a word 'university' to the school would help
# if school name contains 'university', 'institute', 'college', 'school', 'tech',
# or even a character 'u', we then do not add the word 'university'
name_imcomplete = gter[~gter['School'].str.lower().str.contains('university')]
name_imcomplete = name_imcomplete[~name_imcomplete['School'].str.lower().str.contains('institute')]        
name_imcomplete = name_imcomplete[~name_imcomplete['School'].str.lower().str.contains('school')]                 
name_imcomplete = name_imcomplete[~name_imcomplete['School'].str.lower().str.contains('college')] 
name_imcomplete = name_imcomplete[~name_imcomplete['School'].str.lower().str.contains('tech')] 
name_imcomplete = name_imcomplete[~name_imcomplete['School'].str.lower().str.contains('u')]                 
name_imcomplete['School'] = name_imcomplete['School']+ ' University'


# update imcomplete school name with above school name
for index, value in name_imcomplete.iterrows():
    gter.loc[index, 'School'] = name_imcomplete.loc[index,'School'] 
    
#%%           
# use google api to standardize the school names
#time.sleep(8)
import googlemaps
gmaps = googlemaps.Client(key='AIzaSyB_jUbSitAUzX0neWC4tAkDUoLuIKceaWU')

#geocode_result = gmaps.geocode('PSU University')
#address = geocode_result[0][u'formatted_address'].encode('UTF-8')
#geocode = geocode_result[0]['geometry'][u'location']
#place = gmaps.places_nearby(geocode, type='university')
#place['results'][0]['name']
#lehigh = gmaps.places_autocomplete("lehigh university",'university')

# create a new column to store standardize school names
gter.loc[:,'School_std'] = pd.Series()

for index, value in gter.iterrows():
    univ = gmaps.places_autocomplete(gter.loc[index,'School'],'university')
    name = ''
    if univ != []:
        name = univ[0]['description'].encode('UTF-8')
    gter.loc[index, 'School_std'] = name

# filter out data without valid school name
gter_eff = gter[gter['School_std'] != '']

gter_eff['school'] = gter_eff['School_std'].str.split(', ').str[0]
gter_eff['country'] = gter_eff['School_std'].str.split(', ').str[-1]
#gter_eff['state'] = gter_eff['School_std'].str.split(', ').str[-2]

gter_usa = gter_eff[gter_eff['country'] == 'United States']

#%%           
# use google custom search api to standardize the school names
school_unique = pd.Series(gter['School'].unique())
school_unique_adjust = pd.Series()

school_name = pd.concat([school_unique, school_unique_adjust], axis=1)
school_name= school_name.rename(columns={0:'ori', 1:'adj'})

from googleapiclient.discovery import build
    
service = build("customsearch", "v1", developerKey="AIzaSyB_jUbSitAUzX0neWC4tAkDUoLuIKceaWU")

for index, value in school_name.iterrows():
    query = value['ori']
    res = service.cse().list(q=query, cx='011761368493089171845:fsd_n1wdkou',lr="lang_en").execute()
    school_name.loc[index, 'adj'] = res['items'][0]['title']
    time.sleep(5) 



#%% GRE processing                             
gre = gter_usa['GRE'].fillna('') # 10054/17299 are nan values
gre_breakdown1 = gre.str.extract('[\bOverall\b]*\D*(\d*)\+*\d*\D*[\bV\b]\D*(\d*)\D*[\bQ\b]\D*(\d*)\D*[\bAW\b]\D*(\d*\.*\d*)', expand=True)
gre_breakdown1 = gre_breakdown1.rename(columns={0:'Overall', 1:'V', 2:'Q', 3:'AW'})
gre_breakdown1 = gre_breakdown1.apply(pd.to_numeric) # convert the entire df to numeric

gre.drop(gre_breakdown1[gre_breakdown1['Overall'].notnull()].index.values, inplace=True)

'''
Some patterns like below are taken care of in gre_breakdown2
V: 159+162+3.5 / Q: / AW:
V: 440 790 (3) / Q: / AW:
V: 315+3.5 / Q: / AW:
V: 150 162 3 / Q: / AW:
V: 160 + 168 + 3.5 / Q: / AW:
'''
gre_breakdown2 = gre.str.extract('[\bV\b]\D*(\d*)\D*(\d*\.*\d*)\W*(\d*\.*\d*)\W*(\d*\.*\d*)', expand=True)
gre_breakdown2 = gre_breakdown2.rename(columns={0:'Overall', 1:'V', 2:'Q', 3:'AW'})
gre_breakdown2 = gre_breakdown2.apply(pd.to_numeric) # convert the entire df to numeric
gre_breakdown2.dropna(axis=0,how='all',inplace=True)

gre.drop(gre_breakdown2[gre_breakdown2['Overall'].notnull()].index.values, inplace=True)

# correct the disorder of values
def gre_score_dection(d):
    score_type = ''
    if d > 0 and d <= 7:
        score_type = 'AW'
    elif d > 7 and d < 100:
        score_type = 'Percentage'
    elif d >= 100 and d <= 170:
        score_type = 'New V or Q'
    elif d >= 300 and d <= 340:
        score_type = 'New total'
    elif d > 340 and d <= 800:
        score_type = 'Old V or Q'
    elif d >= 1000:
        score_type = 'Old total'
    return score_type


gre_breakdown1.fillna(0,inplace=True)

for index_df, value_df in gre_breakdown1.iterrows():
    score = {'Overall':0, 'V':0, 'Q':0, 'AW':0}
    for index_se, value_se in value_df.iteritems():
        if gre_score_dection(value_se) == 'New V or Q' or gre_score_dection(value_se) == 'Old V or Q':
            if score['V'] == 0:
                score['V'] = value_se
            else:
                score['Q'] = value_se
        elif gre_score_dection(value_se) == 'New total' or gre_score_dection(value_se) == 'Old total':
            score['Overall'] = value_se
        elif  gre_score_dection(value_se) == 'AW':
            score['AW'] = value_se
    for index_se, value_se in value_df.iteritems():
        gre_breakdown1.loc[index_df, index_se] = score[index_se]

for index_df, value_df in gre_breakdown2.iterrows():
    score = {'Overall':0, 'V':0, 'Q':0, 'AW':0}
    for index_se, value_se in value_df.iteritems():
        if gre_score_dection(value_se) == 'New V or Q' or gre_score_dection(value_se) == 'Old V or Q':
            if score['V'] == 0:
                score['V'] = value_se
            else:
                score['Q'] = value_se
        elif gre_score_dection(value_se) == 'New total' or gre_score_dection(value_se) == 'Old total':
            score['Overall'] = value_se
        elif  gre_score_dection(value_se) == 'AW':
            score['AW'] = value_se
    for index_se, value_se in value_df.iteritems():
        gre_breakdown2.loc[index_df, index_se] = score[index_se]

# gre_breakdown1’s values prioritized, use values from gre_breakdown2 to fill holes:
gre_breakdown1.replace(0, np.nan, inplace=True)
gre_breakdown = gre_breakdown1.combine_first(gre_breakdown2)
gre_breakdown.fillna(0,inplace=True)

# check if the overall score is right or not, sometimes it can be wrong even only simple addition
index = gre_breakdown[(gre_breakdown['V'] != 0) & (gre_breakdown['Q'] != 0)].index.values
gre_breakdown['sum'] = pd.Series()
gre_breakdown.loc[index,'sum'] = gre_breakdown.loc[index,'V'] + gre_breakdown.loc[index,'Q']

for index, value in gre_breakdown.iterrows():
    if ~np.isnan(value['sum']):
        gre_breakdown.loc[index, 'Overall'] = value['sum']

gre_breakdown.drop(['sum'], 1, inplace=True)

# convert old gre V and Q score to new one
old_gre = gre_breakdown[gre_breakdown['Overall'] > 340]
old_gre_index = old_gre.index.values
Gre_Concordance_Table = pd.read_csv('C:/Users/hliu88/Desktop/temp/Schoolpredict/Gre_Concordance_Table.csv')
v_concordance = Gre_Concordance_Table[['OldGRE', 'NewV']]
q_concordance = Gre_Concordance_Table[['OldGRE', 'NewQ']]
old_gre_adjust = old_gre.merge(v_concordance, how='left', left_on = "V", left_index = True, right_on = 'OldGRE').set_index(old_gre_index)
old_gre_adjust.drop('OldGRE', axis=1, inplace=True)
old_gre_adjust = old_gre_adjust.merge(q_concordance, how='left', left_on = "Q", left_index = True, right_on = 'OldGRE').set_index(old_gre_index)
old_gre_adjust.drop('OldGRE', axis=1, inplace=True)
old_gre_adjust['NewOverall'] = old_gre_adjust['NewV'] + old_gre_adjust['NewQ']

# if only old GRE overall score available, use some linear regression to get new overall score
# new = 0.061*old + 264 + 4(this additional 4 is likely to overestimate some low score, but works better for high score)
index = old_gre_adjust[(old_gre_adjust['Overall'] != 0) & (old_gre_adjust['V'] == 0) & (old_gre_adjust['Q'] == 0)].index.values
old_gre_adjust.loc[index,'NewOverall'] = old_gre_adjust.loc[index,'Overall']*0.061 + 264 + 4
old_gre_adjust.loc[index,'NewOverall'] = old_gre_adjust.loc[index,'NewOverall'].round(0)
old_gre_adjust.drop(['Overall','Q','V'], axis=1, inplace=True)
old_gre_adjust.rename(columns={'NewOverall':'Overall', 'NewV':'V', 'NewQ':'Q'}, inplace=True)
old_gre_adjust = old_gre_adjust[['Overall','Q','V','AW']]

new_gre = gre_breakdown[gre_breakdown['Overall'] <= 340]
gre_breakdown = new_gre.append(old_gre_adjust)
gre_breakdown= gre_breakdown[['Overall','Q','V','AW']]

#sns.distplot(gre_breakdown['Overall'][gre_breakdown['Overall'] > 0])
#sns.distplot(gre_breakdown['V'][(gre_breakdown['V'] < 170) & (gre_breakdown['V'] > 0)])

#%% Toefl processing
toefl = gter_usa['TOEFL'].fillna('')
toefl_breakdown = toefl.str.extract('\D*(\d+)\D*(\d*)\D*(\d*)\D*(\d*)\D*(\d*)\D*', expand=True)
toefl_breakdown = toefl_breakdown.rename(columns={0:'Overall', 1:'R', 2:'L', 3:'S', 4:'W'})
toefl_breakdown = toefl_breakdown.apply(pd.to_numeric) # convert the entire df to numeric

toefl_breakdown[toefl_breakdown['Overall'] <= 30] = \
toefl_breakdown[toefl_breakdown['Overall'] <= 30].shift(periods=1, axis=1)

#some people report mutiple overall results, choose the maximum one
toefl_breakdown.loc['Overall'] = toefl_breakdown.max(1)
toefl_breakdown['Overall'][toefl_breakdown['Overall'] <= 30] = np.nan

toefl_breakdown['R'][toefl_breakdown['R'] > 30] = 0
toefl_breakdown['L'][toefl_breakdown['L'] > 30] = 0
toefl_breakdown['S'][toefl_breakdown['S'] > 30] = 0
toefl_breakdown['W'][toefl_breakdown['W'] > 30] = 0

# check if the overall score is right or not
index = toefl_breakdown[(toefl_breakdown['R'].notnull()) & (toefl_breakdown['L'].notnull()) & (toefl_breakdown['S'].notnull()) & (toefl_breakdown['W'].notnull())].index.values
toefl_breakdown['sum'] = pd.Series()
toefl_breakdown.loc[index,'sum'] = toefl_breakdown.loc[index,'R'] + toefl_breakdown.loc[index,'L'] + toefl_breakdown.loc[index,'S'] + toefl_breakdown.loc[index,'W']
toefl_breakdown.loc[toefl_breakdown['sum'].notnull().index.values, 'Overall'] = toefl_breakdown[toefl_breakdown['sum'].notnull()]['sum']
toefl_breakdown.drop(['sum'], 1, inplace=True)

#sns.distplot(toefl_breakdown['Overall'][toefl_breakdown['Overall'] > 30])
    
#%% IELTS processing 
ielts = gter_usa[gter_usa['IELTS'].notnull()]['IELTS']
ielts_breakdown = ielts.str.extract('\D*(\d*\.*\d*)\D*(\\d*\.*\d*)\D*(\d*\.*\d*)\D*(\\d*\.*\d*)\D*(\\d*\.*\d*)\D*', expand=True)
ielts_breakdown = ielts_breakdown.rename(columns={0:'Overall', 1:'R', 2:'L', 3:'S', 4:'W'})
ielts_breakdown = ielts_breakdown.apply(pd.to_numeric) # convert the entire df to numeric

#sns.distplot(ielts_breakdown['Overall'][ielts_breakdown['Overall'] > 0])

#%% LSAT Processing
lsat = gter_usa[gter_usa['LSAT'].notnull()]['LSAT']
lsat = lsat.replace('^(?!^\d{3}).*',np.nan, regex=True)
lsat = lsat.apply(pd.to_numeric) # convert the entire df to numeric

#sns.distplot(lsat[lsat > 0])

#%% GMAT Processing
gmat = gter_usa[gter_usa['GMAT'].notnull()]['GMAT']
gmat_breakdown = gmat.str.extract('\D*(\d*\.*\d*)\D*(\d*\.*\d*)\D*(\d*\.*\d*)\D*(\d*\.*\d*)\D*', expand=True)
gmat_breakdown = gmat_breakdown.rename(columns={0:'Overall', 1:'Q', 2:'V', 3:'AW'})
gmat_breakdown = gmat_breakdown.apply(pd.to_numeric) # convert the entire df to numeric

def gmat_score_dection(d):
    score_type = ''
    if d > 0 and d <= 6:
        score_type = 'AW'
    elif d > 6 and d < 10:
        score_type = 'Bullshit'
    return score_type

for index_df, value_df in gmat_breakdown.iterrows():
    for index_se, value_se in value_df.iteritems():
        if gmat_score_dection(value_se) == 'AW':
            gmat_breakdown.loc[index_df, 'AW'] = value_se

gmat_breakdown[gmat_breakdown['Q'] < 10] = np.nan
gmat_breakdown[gmat_breakdown['V'] < 10] = np.nan

#sns.distplot(gmat_breakdown['Overall'][gmat_breakdown['Overall'].notnull()])

#%% GRE_SUB Processing
gre_sub = gter_usa[gter_usa['GRE_sub'].notnull()]['GRE_sub']
gre_sub_breakdown = gre_sub.str.extract('^(?!.*\d\.\d+.*)\D*(\d+)\D*(\d*)\D*', expand=True)
gre_sub_breakdown = gre_sub_breakdown.rename(columns={0:'GRE_sub_Score', 1:'GRE_sub_pct'})
gre_sub_breakdown = gre_sub_breakdown.apply(pd.to_numeric) # convert the entire df to numeric
gre_sub_breakdown[gre_sub_breakdown['GRE_sub_Score'] <= 99] = \
gre_sub_breakdown[gre_sub_breakdown['GRE_sub_Score'] <= 99].shift(periods=1, axis=1)

#sns.distplot(gre_sub_breakdown['GRE_sub_Score'][gre_sub_breakdown['GRE_sub_Score'].notnull()])


