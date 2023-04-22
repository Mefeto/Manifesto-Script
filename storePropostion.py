import openai
import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient

# GPT-3 parameters
model_engine = "text-davinci-003"
prompt = "어려운 내용을 쉽게 해설해주는 선생님으로 작동해줘." \
         "나는 한국어로 요청을 줄 것이며 응답은 json 형태로만 해줘. 미사여구는 붙이지마." \ 
         "너에게는 국회의원 발의법률안의 제안이유와 주요내용이 주어질 거야." \ 
         "너는 이 내용이 조명하는 문제 상황, 문제를 해결하기 위해 제시한 방안, 정책이나 법률 관련 어려운 단어들을 5개 선별하여 다음과 같은 json 형태로 응답해줘." \ 
         "{'problem' : 여기에는 문제 상황을 넣어줘, 'solution': 여기에는 문제 해결 제시 방안을 넣어줘, 'words': 여기에는 5개의 단어 정보 배열 넣는데, 하나의 요소는 {'name': 단어 명, 'description': 단어의 설명} 의 형태로 넣어줘}} 이제부터 발의 법률안의 내용이 주어질거야."
temperature = 0.5
max_tokens = 512

# MongoDB setup
client = pymongo.MongoClient()

db = client['manifesto-proposition']
collection = db['test-data']


def generate_additional_content():
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        prompt_context=None,
        user=None,
        frequency_penalty=None,
        presence_penalty=None,
        logprobs=None
    )
    additionalContent = response.choices[0].text.strip()
    return additionalContent


def fetch_bill_data(bill_id):
    url = url_template.format(bill_id)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')

    if soup is None or soup.RESULT is None or soup.RESULT.CODE.text != 'INFO-000':
        return None

    # Extract detail link and summary content
    detail_link = soup.DETAIL_LINK.text
    detail_content = ''
    if detail_link:
        detail_response = requests.get(detail_link)
        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
        summary_div = detail_soup.find('div', {'id': 'summaryContentDiv'})
        if summary_div:
            summary_content = summary_div.text.strip()

            # Generate additional content using OpenAI GPT-3
            additional_content = generate_additional_content()
            detail_content = f"{summary_content}\n\n{additional_content}"
            time_estimate = len(detail_content) // 100 + 1
            detail_content = f"예상 소요시간: {time_estimate} 분\n\n{detail_content}"

    # Create bill dictionary
    bill = {
        'id': soup.BILL_ID.text,
        'number': soup.BILL_NO.text,
        'name': soup.BILL_NAME.text,
        'committee': soup.COMMITTEE.text,
        'committee_id': soup.COMMITTEE_ID.text,
        'prop_date': soup.PROPOSE_DT.text,
        'prop_result': soup.PROC_RESULT.text,
        'age': soup.AGE.text,
        'detail_link': soup.DETAIL_LINK.text,
        'detail_content': detail_content,
        'ai_analyzed': {
            'problem': "problem",
            'solution': "solution",
            'words': [
                {
                    'name': "word1",
                    'description': "word1 description"
                },
                {
                    'name': "word2",
                    'description': "word2 description"
                },
                {
                    'name': "word3",
                    'description': "word3 description"
                },
                {
                    'name': "word4",
                    'description': "word4 description"
                },
                {
                    'name': "word5",
                    'description': "word5 description"
                },
            ]
        },
        'proposer': soup.PROPOSER.text,
        'members': soup.MEMBER_LIST.text,
        'rst_proposer': soup.RST_PROPOSER.text,
        'pub_proposer': soup.PUBL_PROPOSER.text,

    }

    return bill


# Loop through bill IDs and fetch data from API
url_template = 'https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?BILL_NO={}&AGE=21'
bills = []
for bill_id in range(2121448, 2121438, -1):
    url = url_template.format(bill_id)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')

    if soup is None or soup.RESULT is None or soup.RESULT.CODE.text != 'INFO-000':
        continue

    # Extract detail link and summary content
    detail_link = soup.DETAIL_LINK.text
    detail_content = ''
    if detail_link:
        detail_response = requests.get(detail_link)
        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
        summary_div = detail_soup.find('div', {'id': 'summaryContentDiv'})
        if summary_div:
            summary_content = summary_div.text.strip()

            # Generate additional content using OpenAI GPT-3
            response = openai.Completion.create(
                model=model_engine,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                prompt_context=None,
                user=None,
                frequency_penalty=None,
                presence_penalty=None,
                logprobs=None
            )
            additional_content = response.choices[0].text.strip()
            detail_content = f"{summary_content}\n\n{additional_content}"
            time_estimate = len(detail_content) // 100 + 1
            detail_content = f"예상 소요시간: {time_estimate} 분\n\n{detail_content}"

        # Create bill data dictionary
        bill = {
            'BILL_ID': soup.BILL_ID.text,
            'BILL_NO': soup.BILL_NO.text,
            'BILL_NAME': soup.BILL_NAME.text,
            'COMMITTEE': soup.COMMITTEE.text,
            'PROPOSE_DT': soup.PROPOSE_DT.text,
            'PROC_RESULT': soup.PROC_RESULT.text,
            'AGE': soup.AGE.text,
            'DETAIL_LINK': soup.DETAIL_LINK.text,
            'DETAIL_CONTENT': detail_content,
            'PROPOSER': soup.PROPOSER.text,
            'MEMBER_LIST': soup.MEMBER_LIST.text,
            'RST_PROPOSER': soup.RST_PROPOSER.text,
            'PUBL_PROPOSER': soup.PUBL_PROPOSER.text,
            'COMMITTEE_ID': soup.COMMITTEE_ID.text
        }
        bills.append(bill)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    collection.insert_many(bills)
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
