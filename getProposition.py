import string

import requests
from bs4 import BeautifulSoup

# # MongoDB setup
# client = pymongo.MongoClient()
# db = client['manifesto-proposition']
# collection = db['test-data']
from pymongo import MongoClient
from pymongo.server_api import ServerApi


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


def format_response(proposition):
    # 개별 발의안
    # '': soup.BILL_ID.text,
    # '': soup.BILL_NO.text,
    # '': soup.BILL_NAME.text,
    # '': soup.COMMITTEE.text,
    # '': soup.PROPOSE_DT.text,
    # '': soup.PROC_RESULT.text,
    # '': soup.AGE.text,
    # '': soup.DETAIL_LINK.text,
    # '': detail_content,
    # '': soup.PROPOSER.text,
    # '': soup.MEMBER_LIST.text,
    # '': soup.RST_PROPOSER.text,
    # '': soup.PUBL_PROPOSER.text,
    # '': soup.COMMITTEE_ID.text
    return {
        id: proposition[""]
    }


def send_request(index: int, size: int):
    API_URL = "https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?"
    q_key = "KEY=64a09c1b39a9417992285f2624fb3175&"
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
        response = requests.post(url, headers=headers)
        proposal_list = response.json()["nzmimeepazxkubdpn"][1]["row"]

        code = response.json()["nzmimeepazxkubdpn"][0]["head"][1]["RESULT"]["CODE"]

        # INFO 200 : 해당하는 데이터가 없습니다, INFO 300 : 관리자에 의해 인증키 사용이 제한되었습니다.
        if code == "INFO-200" or code == "INFO-300":
            return None

        # scrape_data = list(map(lambda x: scrape_content(x['DETAIL_LINK']), proposal_list))

        """
        call function that run gpt prompt
        :param scrape_data, list of string 
        :return gpt_result 
        """

        for proposal_dict in proposal_list:
            scraped_content_data = scrape_content(proposal_dict['DETAIL_LINK'])

            # call gpt function

            gpt_result = {
                "problem": "노동위원회의 심판 기능을 전문적으로 다루는 지방노동법원으로 이관하기 위해 법률 개정이 필요하다.",
                "solution": "차별적 처우의 시정신청에 대한 노동위원회의 시정명령 기능을 지방노동법원으로 이관하고, 관련 조사, 심문, 조정, 중재 규정, 시정명령 및 과태료 규정을 삭제한다.",
                "words": [
                    {"name": "지방노동법원", "description": "노동사건을 전문적으로 다루는 법원으로, 지방 법원 내에 설치된다."},
                    {"name": "노동위원회", "description": "노동 분야의 분쟁 조정 및 노동정책에 관한 자문 역할을 하는 기관이다."},
                    {"name": "차별적 처우", "description": "근로자에게 부당한 차별을 가하는 행위를 말한다."},
                    {"name": "시정신청", "description": "부당한 처우를 받은 근로자가 그 처우를 바로잡기 위해 관련 기관에 요청하는 절차이다."},
                    {"name": "시정명령", "description": "부당한 처우를 시정하도록 명령하는 권한을 가진 기관의 결정이다."}
                ]
            }

            proposal_dict.update({'DETAIL_CONTENT': scraped_content_data})
            proposal_dict.update({"ANALYTICS": gpt_result})

        return proposal_list

    except Exception as ex:
        print(ex)


def mongo_insert_many(scraped_content):
    uri = "mongodb+srv://ehcws333:ehcws333@manifesto.tpyq8xn.mongodb.net/?retryWrites=true&w=majority"
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
scraped_and_gpt_data = send_request(1, 5)
insert_many = mongo_insert_many(scraped_and_gpt_data)
print(insert_many.inserted_ids);
