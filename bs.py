import requests
from bs4 import BeautifulSoup

# 스크래핑할 페이지의 URL
url = "http://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_E2E3C0Z4Y0V4D1C3C1K6J5G4D3C3K5&ageFrom=21&ageTo=21"

# 페이지의 HTML을 가져옴
response = requests.get(url)
html = response.content

# BeautifulSoup 객체 생성
soup = BeautifulSoup(html, 'html.parser')

# "제안이유 및 주요내용" 부분을 포함하는 div 태그 선택
div_tag = soup.select_one('div[id="summaryContentDiv"]')

# div 태그 내용 출력
print(div_tag.text.strip())