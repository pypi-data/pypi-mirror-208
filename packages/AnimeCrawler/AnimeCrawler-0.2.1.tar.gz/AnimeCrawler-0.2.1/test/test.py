import requests

a = requests.get(
    'https://www.mhyyy.com/search.html?wd=%E4%B8%AD%E4%BA%8C%E7%97%85',
    headers={'User-Agent': 'Mozilla/5.0'},
).text
with open('a.html', 'a+') as fp:
    fp.write(a)

'//div[@class=module-items module-card-items]'
