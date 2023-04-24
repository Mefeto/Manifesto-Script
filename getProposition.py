import json
import string

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# MongoDB setup
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Get env variables
load_dotenv()
host = os.environ.get('DB_HOST')
openai_key = os.environ.get('OPENAI_KEY')
openapi_key = os.environ.get('OPENAPI_KEY')

# OpenAI setup
openai.api_key = openai_key


# detail link 통해서 컨텐츠 가져오기
def scrape_content(url: string):
    # HTML 가져오기
    res = requests.get(url)
    html = res.content

    # soup의 객체 생성
    soup = BeautifulSoup(html, 'html.parser')
    if soup is None:
        return None

    # '제안이유 및 주요내용' 부분을 포함하는 div 태그 선택
    tag = soup.select_one('div[id="summaryContentDiv"]')

    # div 태그 내의 텍스트 출력
    return tag.text.strip()


def get_ai_analyzed(detail: string):
    model = "gpt-3.5-turbo"
    messages = [
        {"role": "system",
         "content": '너는 어려운 내용을 쉽게 해설하는 선생님 역할을 해줘. 한국어로 제공된 국회의원 발의법률안의 제안 이유와 주요 내용을 바탕으로 문제 상황, 문제 해결 방안, 그리고 정책이나 법률 관련 어려운 단어 5개를 선별하여 JSON 형태로 응답해야돼. 미사여구는 붙이지마. JSON 구조는 다음과 같아: {"problem": 문제 상황, "solution": 문제 해결 제시 방안, "words":[{"name": 단어 명, "description": 단어 설명}]} 이제 발의법률안의 내용을 제공할 것이야.'},
        {"role": "user", "content": detail}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=800,
    )
    return response.choices[0].message.content


# 국회 법률 발의안 요청 보내서 스크랩핑한 결과를 gpt에 돌려 받아온 결과를 db에 넣는 로직
def send_request(index: int, size: int):
    API_URL = "https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?"
    q_key = openapi_key
    q_type = "Type=json&"
    q_pIndex = "pIndex=%d&" % index
    q_pSize = "pSize=%d&" % size
    q_age = "AGE=%d" % 21

    url = API_URL + q_key + q_type + q_pIndex + q_pSize + q_age
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Content-Language': 'ko-KR',
    }

    try:
        # 요청 보내서 발의안 목록 api 불러오기
        response = requests.post(url, headers=headers)

        # 발의안 리스트를 뽑는다.
        proposal_list = response.json()["nzmimeepazxkubdpn"][1]["row"]

        # 응답 코드를 추출하여 예외처리를 한다.
        code = response.json()["nzmimeepazxkubdpn"][0]["head"][1]["RESULT"]["CODE"]
        # INFO 200 : 해당하는 데이터가 없습니다, INFO 300 : 관리자에 의해 인증키 사용이 제한되었습니다.
        if code == "INFO-200" or code == "INFO-300":
            return None

        # 발의안 목록을 순회한다.
        for proposal_dict in proposal_list:
            # 해당 발의안의 세부 링크를 스크랩핑 해온다.
            scraped_content_data = scrape_content(proposal_dict['DETAIL_LINK'])

            # call gpt function
            gpt_result = get_ai_analyzed(scraped_content_data)

            # update proposal info
            proposal_dict.update({'DETAIL_CONTENT': scraped_content_data})
            proposal_dict.update({"ANALYTICS": json.loads(gpt_result)})

        return proposal_list

    except Exception as ex:
        print(ex)


def mongo_insert_many(scraped_content):
    uri = host
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['manifesto']
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    collection = db.get_collection('propositions')
    return collection.insert_many(scraped_content)


# 호출 해보기
scraped_and_gpt_data = send_request(21, 5)
insert_many = mongo_insert_many(scraped_and_gpt_data)
print(insert_many.inserted_ids)
