import json, ssl, urllib.request

# API網址
url = 'https://data.moenv.gov.tw/api/v2/stat_p_129?api_key=58d6040c-dca7-407f-a244-d0bfdfa8144a&limit=100&sort=ImportDate%20desc&format=JSON'
context = ssl._create_unverified_context()

# 讀取 JSON
with urllib.request.urlopen(url, context=context) as jsondata:
    data = json.loads(jsondata.read().decode('utf-8-sig'))

# 建立統計區清單 (item2)
stat_areas = []
for i in data['records']:
    area = i['item2']
    if area not in stat_areas:
        stat_areas.append(area)

# 列出可選擇的統計區
print("可選擇的統計區：")
for idx, area in enumerate(stat_areas, 1):
    print(f"{idx}. {area}")

# 讓使用者輸入選擇
choice = int(input("請輸入要查詢的統計區編號："))
selected_area = stat_areas[choice - 1]
print(f"\n你選擇的是：{selected_area}\n")

# 顯示該統計區的統計資料
for i in data['records']:
    if i['item2'] == selected_area:
        print(
            f"統計期: {i['item1']}\t",
            f"總處理量: {i['value1']}\t",
            f"回收再利用量: {i['value2']}\t",
            f"焚化量: {i['value3']}\t",
            f"衛生掩埋量: {i['value4']}\t",
            f"其他處理量: {i['value5']}"
        )