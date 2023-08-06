"""
Python wrapper for website categorization API (service of www.websitecategorizationapi.com)

Explanation of available classifiers: 

Classifier_type should be set to either iab1 (Tier 1 categorization) or iab2 (Tier 2 categorization) for general websites or ecommerce1, ecommerce2 and ecommerce3 for E-commerce or product websites. 

IAB Tier 1 categorization returns probabilities of text being classified as one of 29 possible categories.

IAB Tier 2 categorization returns probabilities of text being classified as one of 447 possible categories.

Ecommerce Tier 1 categorization returns probabilities of text being classified as one of 21 possible categories.

Ecommerce Tier 2 website categorization returns probabilities of text being classified as one of 182 possible categories.

Ecommerce Tier 3 website categorization returns probabilities of text being classified as one of 1113 possible categories.
"""

import requests
import json

class websiteclassificationapi:
    def __init__(self):
        pass

    @staticmethod
    def get_categorization(url,api_key,category_type):
        """
        url = URL of website
        api_key = api key
        category_type = iab1 or iab2 for general websites, ecommerce1, ecommerce2 and ecommerce3 for E-commerce or product websites
        """
        if category_type=='iab1':
            url_api = "https://www.websitecategorizationapi.com/api/iab/iab_category1_url.php"
        elif category_type=='iab2':
            url_api = "https://www.websitecategorizationapi.com/api/iab/iab_category2_url.php"
        elif category_type=='ecommerce1':
            url_api = "https://www.websitecategorizationapi.com/api/iab/gpt/gpt_category1.php"
        elif category_type=='ecommerce2':
            url_api = "https://www.websitecategorizationapi.com/api/iab/gpt/gpt_category2.php"
        elif category_type=='ecommerce3':
            url_api = "https://www.websitecategorizationapi.com/api/iab/gpt/gpt_category3.php"                        

        if (('http://' not in url) or ('https://' not in url)):
            url = 'http://'+url
            try: 
                url = requests.utils.quote(url)
                print("URL:", url)
                payload='query='+url+'&api_key='+api_key+'&data_type=url'
                headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
                }
                response = requests.request("POST", url_api, headers=headers, data=payload)
                data = json.loads(response.text)
                try:
                    category = data['classification'][0]['category']
                except:
                    category = 'url could not be loaded'
                return category
            except Exception as e:
                print(e)
                pass