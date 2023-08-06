import requests
import json

SPOT_ADVISOR_JSON_URL = 'https://spot-bid-advisor.s3.amazonaws.com/spot-advisor-data.json'


class SpotUtils:
    def __init__(self, region):
        self.__region = region

    def get_spot_interruption_frequency(self, os):

        results = {}
        try:
            response = requests.get(url=SPOT_ADVISOR_JSON_URL)
            spot_advisor = json.loads(response.text)['spot_advisor']
        except requests.exceptions.ConnectionError:
            return
        rates = {
            0: {
                'min': 0,
                'max': 5,
                'rate': '<5%'
            },  # "<5%",
            1: {
                'min': 6,
                'max': 10,
                'rate': '5-10%'
            },  # "5-10%",
            2: {
                'min': 11,
                'max': 15,
                'rate': '10-15%'
            },  # "10-15%",
            3: {
                'min': 16,
                'max': 20,
                'rate': '15-20%'
            },  # "15-20%",
            4: {
                'min': 21,
                'max': 100,
                'rate': '>20%'
            }  # ">20%"
        }

        instance_data = spot_advisor[self.__region][os]

        instance_types = instance_data.keys()

        for ii in instance_types:
            try:
                rate = spot_advisor[self.__region][os][ii]['r']
                results[ii] = rates[rate]
            except (IndexError, KeyError):
                results[ii] = ""
        return results


if __name__ == '__main__':
    spot_utils = SpotUtils('us-east-1')
    result = spot_utils.get_spot_interruption_frequency('Linux')
    print(result)
