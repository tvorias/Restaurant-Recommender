# SI 507 Final Project: Restaurant Recommender

## Use case
This program utilizes Google's Geolocation API and the Yelp Fusion API to provide users with restaurant recommendations that are tailored to their preferences and location. Users will have the opportunity to learn more about the program-generated restaurant recommendations, such as their rating, review count, and food type, as well as to explore the restaurant's location on an interactive map. 

## Set up
### Dependencies
- `Python3`
- `Geolocation API key`
  - To access a key, you will first have to set up a Google Cloud project. Once that's complete, you can create and secure your API key. Instructions for the necessary steps can be found [here](https://developers.google.com/maps/documentation/elevation/cloud-setup).
- `Yelp Fusion API key`
  - To access a key, you need to create an app with Yelp. Once you submit your new app form, you will receive an API key. Instructions for the necessary steps can be found [here](https://docs.developer.yelp.com/docs/fusion-authentication).
- `Google Chrome`
  - Google Chrome is set as the default web browser for this program. Users should set Google Chrome as their default web browser in order to view the html files. Otherwise, the code can be adjusted to set a different browser as the default for this program. 

### Installations
Prior to running the program, you will need to run the following installations:
- `pip install requests`
- `pip install plotly`
- `pip install jinja2`

## Running the program
- First, you will need to download and store the `main.py` file. Next, run any of the necessary pip installs. Once you've obtained both the Google Geolocation API key and Yelp Fusion API key, replace `['GOOGLE_API_KEY']` in the get_location() function with the your personal key and replace `['YELP_API_KEY']` in the get_detroit_restaurants() and get_local_restaurants() functions with your Yelp personal key. 
- From there, the program will be run on the command line. The user will be asked a set of questions related to restaurant preferences. Once those questions are answered, the program will develop a set of recommendations. Users will be asked several prompts related to learning about the recommendations. If the user chooses to view the recommendations, an html file will open in their web browser. Once the web browser is opened, the user should return to the command line for further prompts or to start a new search. 

