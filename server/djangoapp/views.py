from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
user_is_logged_in = False

# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login the current user
            login(request, user)
            user_is_logged_in = True
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout the user in the request
    logout(request)
    user_is_logged_in = False
    # Redirect the user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://eb9bbe00.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = '</br>'.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://eb9bbe00.us-south.apigw.appdomain.cloud/api/review?dealerId=" + str(dealer_id)
        reviews = get_dealer_reviews_from_cf(url)
        reviews_list = '</br>'.join([review.review for review in reviews])
        reviews_list += '</br>'.join([review.sentiment for review in reviews])
        return HttpResponse(reviews_list)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    context = {}
    if request.method == "GET":
        cars = CarModel.objects.all().filter(dealer_id=dealer_id)
        context["cars"] = cars
        context["dealer_id"] = dealer_id
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == 'POST':
        review["review"] = request.POST['content']
        review["purchase"] = request.POST['purchasecheck']
        review["purchase_date"] = request.POST['purchasedate']
        car_id = request.POST['car.id']
        car = CarModel.objects.all().filter(id=car_id)
        review["car_make"] = car.car_model
        review["car_model"] = car.car_model
        review["car_year"] = car.car_year.strftime("%Y")
        review["dealership"] = dealer_id
        # review["id"] = dealer_id
        json_payload["review"] = review
        url = "https://eb9bbe00.us-south.apigw.appdomain.cloud/api/review?dealerId=" + str(dealer_id)
        post_request(url, json_payload)

        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

