# -*- coding: utf-8 -*-
"""Automotive.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_928V5Y2OasmzXji7RatmjNhlwSwPBMs
"""

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
from wordcloud import STOPWORDS, WordCloud, ImageColorGenerator
from PIL import Image

def create_obj_column(df, c_names):
  for c in c_names:
    df[c] = np.NaN
    df[c] = df[c].astype('object')

def brand_search(contentlist, brandlist):
  s1 = pd.Series(contentlist, name = 'A')
  s2 = pd.DataFrame({'A':brandlist, 'B':1})
  brands = pd.merge(s1,s2,how='left',on='A').groupby('A').count().sort_values('B',ascending=False)
  if brands.index[0] in brandlist:
    brands = brands[brands['B'] > 0]
    brand_dict = brands.to_dict()['B']
  else:
    brand_dict = {}
  return brand_dict

def articlefilter(df, wordlist):
  r = 0
  df1 = pd.DataFrame(columns=df.columns)
  for content in df.clean_words:
    content = content.split()
    w = [w for w in wordlist if w in content]
    if len(w) > 0:
      df1 = df1.append(df.iloc[r,:],ignore_index=True)
    r += 1
  return df1

def searchwords(df, wordlist):
  r = 0
  df1 = pd.DataFrame(columns=wordlist)
  for content in df.clean_words:
    content = content.split()
    w = [w for w in wordlist if w in content]
    if len(w) > 0:
      df1.loc[r,w] = 1
    else:
      df1.loc[r,:] = 0
    r += 1
  df1.fillna(0, inplace = True)
  return df1

def brandcounter(d_list):
  for d in d_list:
    try:
      counter += Counter(d)
    except:
      counter = Counter(d)
  return dict(counter)

def brandmatrix(brandnames):
  df = pd.DataFrame(columns=brandnames)
  for brand in brandnames:
    brand_dict = brandcounter(list(auto[auto.RelatedBrand==brand]['AllBrandsMentioned']))
    brand_dict = dict((key, brand_dict[key]) for key in brandnames if key in brand_dict)
    df[brand] = pd.Series(brand_dict)
  df = df.T.fillna(0)
  for i in range(df.shape[0]):
    df.iloc[i,i] = 0
  return df

from google.colab import files
import glob
uploaded = glob.glob('*.csv')

for files in uploaded:
  df = pd.read_csv(files, engine = 'python', error_bad_lines=False)
  df.rename({df.columns[0]:'pageLink'}, axis = 1, inplace = True)
  try:
    auto = auto.append(df, ignore_index = True)
    print(auto.shape)
  except NameError:
    auto = df.copy()
auto.reset_index(drop = True, inplace = True)
auto.dropna(inplace=True)
#auto.drop_duplicates('pageLink', inplace=True)
auto.reset_index(drop=True,inplace=True)

df = pd.read_csv('Articles1 (1).csv', index_col=0)
df.rename({df.columns[0]:'pageLink'}, axis = 1, inplace = True)
df.dropna(subset=['pageLink', 'title', 'body'],inplace=True)
df.drop_duplicates('pageLink', inplace=True)
df.reset_index(drop=True, inplace=True)
auto = df.copy()

auto1 = searchwords(auto,['carbon','electric','environment','sustainability'])
auto1.astype('category').describe()

auto = auto.drop_duplicates('pageLink')
auto.dropna(subset=['pageLink'],inplace=True)

auto['RawContent'] = auto.title + auto.body
create_obj_column(auto,['clean_words','list_clean_words'])
r = 0
for content in auto.RawContent:
  words = re.sub(r'\W+',' ', content)
  words = words.lower()
  words_list = words.split()
  words_list = [w for w in words_list if w not in list(STOPWORDS) and len(w) > 1]
  words = ' '.join(words_list)
  auto.at[r, 'clean_words'] = words
  auto.at[r, 'list_clean_words'] = words_list
  r += 1

create_obj_column(auto, ['RelatedBrand','EVRelated','AllBrandsMentioned'])
brandlist = ['volkswagen','audi','skoda','porsche','peugeot','opel','citroen','jeep','seat2',
             'fiat4','renault','dacia','kia','hyundai','bmw','toyota','lexus','daimler',
             'mercedes','ford','volvo','nissan','mazda','rover','tesla','honda']
r = 0
for content in auto.clean_words:
  content = content.split()
  if 'ev' in content or 'electric' in content or 'hybrid' in content or 'plug' in content:
    auto.at[r, 'EVRelated'] = 1
  else:
    auto.at[r, 'EVRelated'] = 0
  brand_dict = brand_search(content, brandlist)
  if brand_dict != {} and list(brand_dict.values())[0] > 2:
    auto.at[r, 'RelatedBrand'] = list(brand_dict.keys())[0]
    auto.at[r, 'AllBrandsMentioned'] = brand_dict
  else:
    auto.at[r, 'RelatedBrand'] = np.nan
  r += 1

ev = auto[auto.EVRelated==1]
ev_c = ev.groupby('RelatedBrand')['pageLink'].count().rename('NumArticles').reset_index()
ev_s = ev.groupby('RelatedBrand')['Cumulative_ClientLoad'].sum().rename('TotalRead').reset_index()
ev_max = ev.groupby('RelatedBrand')['Cumulative_ClientLoad'].max().rename('MaxRead').reset_index()
ev_min = ev.groupby('RelatedBrand')['Cumulative_ClientLoad'].min().rename('MinRead').reset_index()
ev_all = pd.merge(pd.merge(ev_c,ev_s,how='outer'),pd.merge(ev_max,ev_min,how='outer'),how='outer')
ev_all['AverageRead'] = round(ev_all['TotalRead']/ev_all['NumArticles'],1)

brandnames = ['bmw','tesla','mercedes','hyundai','volkswagen','ford','audi']
sns.heatmap(brandmatrix(brandnames), cmap='YlGnBu')

mask = np.array(Image.open('car2.png'))
mask_colors = ImageColorGenerator(mask)
cloud = WordCloud(mask=mask, background_color="white", max_words=2000, max_font_size=128, 
                  width=mask.shape[1], stopwords=['will','new','may'], height=mask.shape[0], 
                  color_func=mask_colors)

auto = df[(df['RelatedBrand']=='bmw')|(df['RelatedBrand']=='audi')|(df['RelatedBrand']=='mercedes')]
cloud.generate(' '.join(auto.clean_words))
cloud.to_file('b_m_a1.png')

cloud = WordCloud(background_color='white', stopwords=['will','new'])
cloud.generate(' '.join(auto.clean_words))
plt.imshow(cloud, interpolation="bilinear")
plt.show()

auto1 = auto[auto.RelatedBrand.isin(brandnames)]
plt.figure(figsize=(12,5))
plt.ticklabel_format(style='plain')
b=sns.boxplot(x="RelatedBrand", y="Cumulative_ClientLoad", data=auto1, whis=3,
              palette='Set2',fliersize=1)
medians = ev1.groupby(['RelatedBrand'])['Cumulative_ClientLoad'].median()
vertical_offset = ev1['Cumulative_ClientLoad'].median() * 0.05
for xtick in b.get_xticks():
    b.text(xtick,medians[xtick] + vertical_offset,medians[xtick], 
            horizontalalignment='center',size='medium',color='black')

ev1 = auto1[auto1['EVRelated']==1]
plt.figure(figsize=(12,5))
plt.ticklabel_format(style='plain')
b=sns.boxplot(x="RelatedBrand", y="Cumulative_ClientLoad", data=auto1, whis=30,
              palette="Set3",fliersize=1, hue='EVRelated')

wordlist = ['wheel','bmw','mercedes']
auto2 = searchwords(auto[auto['RelatedBrand']=='audi'], wordlist)
auto2[(auto2['wheel']==1)&(auto2['bmw']==1)&(auto2['mercedes']==1)].index

auto1 = auto[auto['RelatedBrand']=='audi']
auto1.reset_index(drop=True).loc[61,'pageLink']

auto