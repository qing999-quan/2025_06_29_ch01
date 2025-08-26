import  json, ssl, urllib.request

url = 'https://stats.moe.gov.tw/files/opendata/base2.json'
context = ssl._create_unverified_context()

with urllib.request.urlopen(url, context=context) as jsondata:
    #將JSON進行UTF-8的BOM解碼，並把解碼後的資料載入JSON陣列中
     data = json.loads(jsondata.read().decode('utf-8-sig'))

for i in data:
    if i['縣市名稱'] == '桃園市':
        print(i['學年度'],'\t',i['學校名稱'],'\t',i['科系名稱'],'\t',i['一年級男學生數'],'\t',i['一年級女學生數'])