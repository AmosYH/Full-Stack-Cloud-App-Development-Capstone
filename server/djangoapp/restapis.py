import requests
import json
from .models import CarDealer, DealerReview, CarModel
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)
    print(response.status_code)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/d5c615f0-c6ce-455d-a822-7577c56d10bf'
    api_key = 'aNCVEDTZLYYfA1tIQ4S18wXvczj0z9LQa-Mwuti9KUv1'

    authenticator = IAMAuthenticator(api_key)
    authenticator.set_disable_ssl_verification(True)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
    text=dealerreview,
    features=Features(sentiment=SentimentOptions(document=True))).get_result()

    return response["sentiment"]["label"]

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result['body']
        if reviews:
            # For each dealer object
            for i in [1]:
                # Get its content in `doc` object
                review_doc = reviews[0]
                print(review_doc["id"])
                # review_doc = 
                # NLU=analyze_review_sentiments(review_doc["review"])
                # Create a CarDealer object with values in `doc` object
                try:
                    review_obj = DealerReview(id=review_doc["id"], dealership=review_doc["dealership"], name=review_doc["name"],
                                    purchase=review_doc["purchase"], review=review_doc["review"], purchase_date=review_doc["purchase_date"],
                                    car_make=review_doc["car_make"],
                                    car_year=review_doc["car_year"], car_model=review_doc["car_model"])
                except:
                    review_obj = DealerReview(id=review_doc["id"], dealership=review_doc["dealership"],
                                    purchase=review_doc["purchase"], review=review_doc["review"])    
                # review_obj.sentiment = analyze_review_sentiments(review_obj.review)
                results.append(review_obj)

    return results