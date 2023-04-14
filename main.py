import requests
import json
import webbrowser as wb
import plotly.graph_objects as go
import pandas as pd
from jinja2 import Template
import time
import subprocess
import tempfile
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

def get_location():
    ''' Connects to Google API to collect user's location

    Parameters:
        None

    Returns:
        list: list of latitude and longitude
    '''
    google_API_key = ['GOOGLE_API_KEY']
    google_url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={google_API_key}'
    IP = {'considerIP': True}
    google_request = requests.post(google_url, IP)
    google_data = json.loads(google_request.text)
    cur_latitude = google_data['location']['lat']
    cur_longitude = google_data['location']['lng']
    return [cur_latitude, cur_longitude]

def write_json(filepath, data, encoding='utf-8', ensure_ascii=False, indent=2):
    """Serializes object as JSON. Writes content to the provided filepath.

    Parameters:
        filepath (str): the path to the file
        data (dict)/(list): the data to be encoded as JSON and written to the file
        encoding (str): name of encoding used to encode the file
        ensure_ascii (str): if False non-ASCII characters are printed as is; otherwise
                            non-ASCII characters are escaped.
        indent (int): number of "pretty printed" indention spaces applied to encoded JSON

    Returns:
        None
    """

    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)

def get_detroit_restaurants():
    yelp_url = 'https://api.yelp.com/v3/businesses/search'
    yelp_API_key = ['YELP_API_KEY']
    headers = {'Authorization': 'Bearer {}'.format(yelp_API_key)}
    params = {'term': 'restaurants', 'location': 'Detroit', 'limit': 50}

    response = requests.get(yelp_url, headers=headers, params=params)
    result = response.json()
    detroit_restaurants = result['businesses']
    return detroit_restaurants

def get_local_restaurants(coordinates):
    yelp_url = 'https://api.yelp.com/v3/businesses/search'
    yelp_API_key = ['YELP_API_KEY']
    headers = {'Authorization': 'Bearer {}'.format(yelp_API_key)}
    params = {'term': 'restaurants', 'latitude': coordinates[0], 'longitude': coordinates[1], 'limit': 50}

    response = requests.get(yelp_url, headers=headers, params=params)
    result = response.json()
    local_restaurants = result['businesses']
    return local_restaurants

class Restaurant:
    def __init__(self, id=None, name=None, rating=None, category=None, image=None, price=None, phone=None, url=None, reviews=None, location=None, is_closed=None):
        self.id = id
        self.name = name
        self.rating = rating
        self.category = category
        self.image = image
        self.price = price
        self.phone = phone
        self.url = url
        self.reviews = reviews
        self.location = location
        self.is_closed = is_closed

def open_cache(CACHE_FILENAME):
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def instantiate_restaurants(data):
    CACHE_DICT = open_cache(data)
    restaurants = []
    for rest in CACHE_DICT:
        id = rest['id']
        name = rest['name']
        rating = rest['rating']
        try:
            category = rest['categories'][0]['title']
        except:
            category = None
        try:
            price = rest['price']
        except:
            price = None
        image = rest['image_url']
        phone = rest['display_phone']
        url = rest['url']
        reviews = rest['review_count']
        location = rest['location']['display_address']
        is_closed = rest['is_closed']
        restaurant = Restaurant(id=id, name=name, rating=rating, category=category, price=price, image=image, phone=phone, url=url,
                                reviews=reviews, location=location, is_closed=is_closed)
        restaurants.append(restaurant)
    return restaurants

class Node:
    def __init__(self, question, yes=None, no=None):
        self.question = question
        self.yes = yes
        self.no = no

    def traverse(self):
        if self.yes is None and self.no is None:
            return self
        print('')
        answer = input(self.question + ' Enter "yes" or "no":  ').lower()
        if answer in ['yes', 'y', 'yeah', 'ya']:
            return self.yes.traverse()
        elif answer in ['no', 'n', 'nah']:
            return self.no.traverse()
        else:
            print('Response not valid. Please enter "yes" or "no"')
            return self.traverse()

def print_recs(recommendations):
    template_str = """
    <html>
      <head>
        <title>Restaurant Recommendations</title>
      </head>
      <body>
        <h1>Based on your preferences, we recommend the following restaurants:</h1>
        <ul>
          {% for i, recommendation in enumerate(recommendations) %}
          <li>
            <p>{{ i+1 }}. {{ recommendation.name }}</p>
            <p>Restaurant type: {{ recommendation.category }}</p>
            <p>Rating: {{ recommendation.rating }}/5</p>
            <p>Review count: {{ recommendation.reviews }}</p>
            <p>Address: {{ recommendation.location[0] }}, {{ recommendation.location[-1] }}</p>
            <p>Phone number: {{ recommendation.phone }}</p>
          </li>
          {% endfor %}
        </ul>
      </body>
    </html>
    """
    template = Template(template_str)
    rendered_template = template.render(recommendations=recommendations, enumerate=enumerate)
    with open('Recommendations.html', 'w') as f:
        f.write(rendered_template)

def print_restaurants(recommendations):
    template_str = """
    <html>
      <head>
        <title>Restaurant Recommendations</title>
      </head>
      <body>
        <h1>Based on your preferences, we recommend the following restaurants:</h1>
        <ul>
          {% for i, recommendation in enumerate(recommendations) %}
          <li>
            <p>{{ i+1 }}. {{ recommendation.name }}</p>
            <p><img src="{{ recommendation.image }}"></p>
          </li>
          {% endfor %}
        </ul>
      </body>
    </html>
    """
    template = Template(template_str)
    rendered_template = template.render(recommendations=recommendations, enumerate=enumerate)
    with open('Recommendations.html', 'w') as f:
        f.write(rendered_template)

def add_lines():
    print('''
    ''')

def open_html():
    chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    first_url = 'https://www.google.com/'
    temp_profile_dir = tempfile.mkdtemp(prefix='chrome-')
    options = f'--user-data-dir="{temp_profile_dir}"'
    command = f'\"{chrome_path}\" {options} {first_url} --new-window'
    subprocess.Popen(command, shell=True, stderr=subprocess.DEVNULL)
    time.sleep(5)
    wb.get(f'\"{chrome_path}\" {options} %s').open_new_tab("Recommendations.html")

def plot_restaurants(location):
    df = pd.read_json(location)
    lons = []
    lats = []
    names = []
    addresses = []

    for i in range(len(df)):
        restaurant = df.iloc[i]
        try:
            lon = restaurant['coordinates']['longitude']
            lat = restaurant['coordinates']['latitude']
            name = restaurant['name']
            address = ', '.join(restaurant['location']['display_address'])
            
            lons.append(lon)
            lats.append(lat)
            names.append(name)
            addresses.append(address)
        except KeyError:
            continue
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        text=[f'{name}<br>{address}' for name, address in zip(names, addresses)],
        mode='markers',
        marker=dict(size=8, symbol='circle', color = 'blue'),
    ))
    fig.update_layout(
        title='Recommended Restaurants',
        geo_scope='usa'
    )

    fig.write_html('Recommendations.html')

def plot_restaurants(location):
    df = pd.read_json(location)
    lons = []
    lats = []
    names = []
    addresses = []

    for i in range(len(df)):
        restaurant = df.iloc[i]
        try:
            lon = restaurant['coordinates']['longitude']
            lat = restaurant['coordinates']['latitude']
            name = restaurant['name']
            address = ', '.join(restaurant['location']['display_address'])
            
            lons.append(lon)
            lats.append(lat)
            names.append(name)
            addresses.append(address)
        except KeyError:
            continue
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        text=[f'{name}<br>{address}' for name, address in zip(names, addresses)],
        mode='markers',
        marker=dict(size=8, symbol='circle', color = 'blue'),
    ))
    fig.update_layout(
        title='Recommended Restaurants',
        geo_scope='usa'
    )

    fig.write_html('Recommendations.html')

if __name__ == '__main__':

    while True:
        add_lines()
        print("Let's get started!")
        add_lines()
        search_type = input('''Enter the number of the option you would like:
                        1. I would like to use my current location to find restaurants nearby
                        2. I would like to find restaurants in Detroit

                        ''')
        try:
            search_type = int(search_type)
            if search_type == 1:
                location = get_location()
                local_restaurants = get_local_restaurants(location)
                write_json('local_restaurants.json', local_restaurants)

                f = open('local_restaurants.json', 'r')
                data = json.load(f)
                f.close()

                restaurants = instantiate_restaurants('local_restaurants.json')
            else:
                detroit_restaurants = get_detroit_restaurants()
                write_json('detroit_restaurants.json', detroit_restaurants)

                f = open('detroit_restaurants.json', 'r')
                data = json.load(f)
                f.close()

                restaurants = instantiate_restaurants('detroit_restaurants.json')

        except:
            print('Please enter a valid number. Enter 1 to search for restaurants nearby or enter 2 to find restaurants in Detroit')
            continue
        break

    yyyy, yyyn, yyny, yynn, ynyy, ynyn, ynny, ynnn, nyyy, nyyn, nyny, nynn, nnyy, nnyn, nnny, nnnn = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
    for rest in restaurants:
        if rest.is_closed == False:
            if rest.rating >= 4:
                if rest.price == '$$$' or rest.price == '$$$$':
                    if rest.reviews >= 200:
                        yyyy.append(rest.__dict__)
                    else:
                        yyyn.append(rest.__dict__)
                else:
                    if rest.reviews >= 200:
                        yyny.append(rest.__dict__)
                    else:
                        yynn.append(rest.__dict__)
            else:
                if rest.price == '$$$' or rest.price == '$$$$':
                    if rest.reviews >= 200:
                        ynyy.append(rest.__dict__)
                    else:
                        ynyn.append(rest.__dict__)
                else:
                    if rest.reviews >= 200:
                        ynny.append(rest.__dict__)
                    else:
                        ynnn.append(rest.__dict__)
        else:
            if rest.rating >= 4:
                if rest.price == '$$$' or rest.price == '$$$$':
                    if rest.reviews >= 200:
                        nyyy.append(rest.__dict__)
                    else:
                        nyyn.append(rest.__dict__)
                else:
                    if rest.reviews >= 200:
                        nyny.append(rest.__dict__)
                    else:
                        nynn.append(rest.__dict__)
            else:
                if rest.price == '$$$' or rest.price == '$$$$':
                    if rest.reviews >= 200:
                        nnyy.append(rest.__dict__)
                    else:
                        nnyn.append(rest.__dict__)
                else:
                    if rest.reviews >= 200:
                        nnny.append(rest.__dict__)
                    else:
                        nnnn.append(rest.__dict__)


tree = Node('Are you looking for a restaurant that is currently open?',
            Node('Would you like a restaurant that has a rating of at least 4 out of 5?',
                Node('Are you okay with an expensive restaurant?',
                    Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(yyyy),
                        Node(yyyn)),
                    Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(yyny),
                        Node(yynn))),
                Node('Are you okay with an expensive restaurant?',
                     Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(ynyy),
                        Node(ynyn)),
                    Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(ynny),
                        Node(ynnn)))),
            Node('Would you like a restaurant that has a rating of at least 4 out of 5?',
                Node('Are you okay with an expensive restaurant?',
                    Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(nyyy),
                        Node(nyyn)),
                    Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(nyny),
                        Node(nynn))),
                Node('Are you okay with an expensive restaurant?',
                    Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(nnyy),
                        Node(nnyn)),
                    Node('Do you prefer a restaurant with a lot of reviews?',
                        Node(nnny),
                        Node(nnnn)))))

while True:
    recommendations = tree.traverse()
    add_lines()
    print('Thank you for trying us out! We are gathering your recommendations right now!')
    add_lines()
    if len(recommendations.question) == 0:
        add_lines()
        print("Unfortunately, there are no restaurants that match your criteria.")
        add_lines()
        response = input('Would you like to try another search?  ')
        if response in ['yes', 'y', 'yeah']:
            continue
        else:
            add_lines()
            print("Thank you for trying me out! Better luck next time <3")
            break
    else:
        add_lines()
        answer = input('''

        Would you like to see a map of all the restaurants we found in your search area? Enter "yes" or "no"  

        ''')
        if answer.lower() in ['yes', 'y', 'yeah', 'ya']:
            if search_type == 1:
                location = 'local_restaurants.json'
                plot_restaurants(location)
            else:
                location = 'detroit_restaurants.json'
                plot_restaurants(location)
            open_html()
        add_lines
        answer = input('''
        
        Would you like to see a list of recommened restaurants based on your preferences? Enter "yes" or "no"
        
        ''')
        add_lines
        if answer.lower() in ['yes', 'y', 'yeah', 'ya']:
            print_restaurants(recommendations.question)
            open_html()
        add_lines()
        answer = input('''

        Would you like to learn more about those restaurants? Enter "yes" or "no" 

        ''')
        if answer.lower() in ['yes', 'y', 'yeah', 'ya']:
            print_recs(recommendations.question)
            open_html()
            add_lines()
            answer = input(''''
            
            Would you like to go to the Yelp page of any the recommended restaurants? Enter "yes" or "no"  
            
            ''')
            add_lines
            while True:
                if answer.lower() in ['yes', 'y', 'yeah', 'ya']:
                    add_lines()
                    rest_num = input('''
                    
                    Please enter the NUMBER of the restaurant (e.g. 1, 2, 3):  
                    
                    ''')
                    try:
                        rest_num = int(rest_num) - 1
                        url = recommendations.question[rest_num]['url']
                        wb.open(url)
                        add_lines()
                        response = input('''
                        
                        Would you like to look at the Yelp page of another restaurant? Enter "yes" or "no": 
                        
                        ''')
                        add_lines()
                        if response in ['yes', 'y', 'yeah', 'ya']:
                            continue
                        else:
                            break
                    except:
                        add_lines()
                        print("Response not valid. Please enter the number of the whose Yelp page you would like to go to:  ")
                        continue
            add_lines()
            answer = input('''
            
            Would you like to start a new search? Enter "yes" or "no": 
            
            ''')
            if answer.lower() in ['yes', 'y', 'yeah', 'ya']:
                continue
            else:
                add_lines()
                print('Thank you for playing!')
                break
        else:
            add_lines()
            answer = input('''
            
            Would you like to start a new search? Enter "yes" or "no": 
            
            ''')
            if answer.lower() in ['yes', 'y', 'yeah', 'ya']:
                continue
            else:
                add_lines()
                print('Thank you for playing!')
                break