import urllib2, json, time
from bs4 import BeautifulSoup
import pandas as pd

start_time = time.time()

#ward number and name
r = urllib2.urlopen('http://bcity.in/wards')
soup = BeautifulSoup(r, 'lxml')
ward_no = []
ward_name = []
table = soup.find(class_='listing')
for row in table.find_all('tr')[1:]:
    cols = row.find_all('td')
    col1 = cols[1].text
    ward_no.append(int(col1.encode('utf-8')))
    col2 = cols[0].text
    ward_name.append(col2.encode('utf-8'))

#correct urls for area and population data collection
urls = []
for ward in ward_name:
    ward = ward.lower()
    ward = ward.replace('.', '')
    ward = ward.replace(' ', '-')
    urls.append('http://bcity.in/wards/' + ward)

#area and population
def area_population(url):
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, 'lxml')
    table = soup.find(class_='info')
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if cols[0].text == 'Area':
            area = cols[1].text
            area = area.replace(' sq. km', '')
        elif cols[0].text == 'Population':
            population = cols[1].text
    return float(area.encode('utf-8')), int(population.encode('utf-8'))

area = [area_population(url)[0] for url in urls]
population = [area_population(url)[1] for url in urls]

data = pd.DataFrame()
data['Ward No.'] = ward_no
data['Ward Name'] = ward_name
data['Area(sq. km)'] = area
data['Population'] = population
data = data.sort_values('Ward No.', ascending=1)

#data error on website
data.loc[data['Ward No.'] == 164, 'Area(sq. km)'] = 3.45
data.loc[data['Ward No.'] == 182, 'Population'] = 25454

#getting each ward's co-ordinates
r = urllib2.urlopen('https://raw.githubusercontent.com/openbangalore/bangalore/master/bangalore/GIS/BBMP_Wards_2011_region.json').read()
coordinates_data = json.loads(r)
features = coordinates_data['features']
df = pd.DataFrame()
df['Ward No.'] = [int(features[i].values()[2].values()[0]) for i in range(len(features))]
df['Ward Coordinates'] = [features[i].values()[0].values()[1] for i in range(len(features))]
df = df.sort_values('Ward No.', ascending=1)

#full list of coordinates of all points of a ward
full_list = []      #list of single lists of coordinates
full_list1 = []     #list of coordinates of all wards
for i in range(len(df)):
    one = df['Ward Coordinates'][i]
    two = one[0]
    d = {}
    l = []
    single_list = []    #list of coordinates in dictonary
    for j in range(len(two)):
        three = two[j]
        if isinstance(three[0], list):
            three = three[0]
        d['lat'] = three[1]
        d['lng'] = three[0]
        single_list.append(d)
        l.append(three[1])
        l.append(three[0])
    full_list.append(single_list)
    full_list1.append(l)

#text file of coordinates of all wards (for use in google maps api)
thefile = open('test.txt', 'w')
for item in full_list:
  thefile.write("%s,\n" % item)

#updating ward_coordinates column of df dataframe
df['Ward Coordinates'] = full_list1
#merging data and df dataframes to store - Ward No., Ward Name, Area, Population and Ward Coordinates columns - in a single dataframe (data)
data = pd.merge(data, df, on='Ward No.')
#writing ward's dataframe (data) to a csv file
data.to_csv('wards.csv', index=False)
#printing runtime of the program
print '%.2f seconds' %(time.time() - start_time)
