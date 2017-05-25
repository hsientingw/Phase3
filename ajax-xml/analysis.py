'''prints out data series/points for highchart graphs, using csv files
'''


f=open("countriesdata.csv", 'r').readlines()
countries=[]
for i in f:
    countries.append([j for j in i.rstrip("\n\r").split(",")])


bubbledata=''
n=1
while n<len(countries):
    bubbledata+="{x: " + countries[n][4] + ", y: " +countries[n][3]+ ", z: " +countries[n][5]
    bubbledata+=", name: '" + countries[n][1] + "', country: '" +countries[n][0] + "'},\n"
    n+=1
print bubbledata
#prints data points for bubble chart

barcategory=[]
bardata=[]
for rows in countries[1:]:
    barcategory.append(rows[0])
    bardata.append(int(rows[5]))
print barcategory
print bardata
#prints categories and data points for bar chart

f2=open("continentsdata.csv", 'r').readlines()
continents=[]
for i in f2:
    continents.append([j for j in i.rstrip("\r\n").split(",")])

continents_list=['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania']
scatterdata=''
for cons in continents_list:
    scatterdata+="{\nname: '" + cons + "', \ndata: ["
    for rows in countries[1:]:
        if rows[2] == cons:
            scatterdata+='[' + str(rows[5]) + ', ' + str(rows[3]) + '],'
    scatterdata=scatterdata[:-1]
    scatterdata+=']\n},'
print scatterdata
#prints data points for scatterplot

print continents
columndata='['
n=1
while n<len(continents[0])-1:
    columndata+="{\nname: '" + continents[0][n]+ "', \ndata: ["
    for rows in continents[1:-1]:
        columndata+=rows[n] +", "
    columndata+=continents[-1][n]+"]\n}, "
    n+=1
print columndata
#prints data points for column graph

