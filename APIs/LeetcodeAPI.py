import requests

class LeetcodeAPI:
    def __init__(self) -> None:
        self.url = 'https://leetcode.com/graphql/'

    def get_leetcode_daily(self):
        payload = {
            'query': """
            query questionOfToday {
            activeDailyCodingChallengeQuestion {
                link
                question {
                difficulty
                title
                topicTags {
                    name
                }
                }
            }
            }
            """,
            'variables': {},
            'operationName': 'questionOfToday'
        }

        response = requests.post(self.url, json=payload)
        if response.status_code == 200:
            data = response.json()
            question_data = data['data']['activeDailyCodingChallengeQuestion']
            return {
                'link': "https://leetcode.com" + question_data['link'],
                'question': {
                    'difficulty': question_data['question']['difficulty'],
                    'title': question_data['question']['title'],
                    'topicTags': [tag['name'] for tag in question_data['question']['topicTags']]
                }
            }
        else:
            return None
