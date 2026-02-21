from requests import Session
from bs4 import BeautifulSoup
import requests
import re
import json
import time

def print_timing(func):
    '''Create a timing decorator function use @print_timing just above the function you want to time.'''

    def wrapper(*arg):
        start = time.perf_counter()
        
        # Run the function decorated
        result = func(*arg)

        end = time.perf_counter()
        execution_time = round((end - start), 2)
        print(f'{func.__name__} took {execution_time} sec')
        return result

    return wrapper


def get_first_paragraph(wikipedia_url, session: Session) -> str:
    print(wikipedia_url) # keep this for the rest of the notebook
    response = session.get(wikipedia_url, headers = {'User-Agent': 'wiki_scraper'})

    soup = BeautifulSoup(response.text, 'html.parser')

    first_paragraph = ""
    for p in soup.find_all('p'):
        text = p.get_text().strip()
    
        if len(text) < 50:
            continue
    
        if '.' not in text:
            continue
    
        first_paragraph = re.sub(r"\[.*?\]", "", text)
        break
    
    return first_paragraph


def get_leaders() -> dict:
    # assign root_url and endpoints
    root_url = "https://country-leaders.onrender.com"
    status_url = root_url + "/status"
    countries_url = root_url + "/countries"
    leaders_url = root_url + '/leaders'
    cookie_url = root_url + '/cookie'

    # query the /status endpoint using the get() method and store it in the req variable (1 line)
    req = requests.get(f"{status_url}")
    
    # Query the cookies enpoint, set the cookies variable and display it (2 lines)
    cookies_val = requests.get(f"{cookie_url}").cookies.get('user_cookie')
    print('User cookie value:', cookies_val)

    # query the /countries endpoint, assign the output to the countries variable (1 line)
    countries = requests.get(countries_url, cookies = {"user_cookie": cookies_val}).json()

    wiki_session = requests.Session()

    # display the request's status code and the countries variable (1 line)
    print(f"The request for 'countries' status code reply is: {req.status_code}, variable 'countries' return: {countries} ")

    try:
        leaders_per_country = {country: requests.get(leaders_url, cookies = {"user_cookie": cookies_val},  params = {'country': country}).json() for country in countries}
    
        for val in leaders_per_country.values():
            for d in val:
                d.update({'first_paragraph': get_first_paragraph(d['wikipedia_url'], wiki_session)})
    except:
        print(f"Status code for cookies: {requests.get(f"{cookie_url}").status_code}")
        if requests.get(f"{status_url}").status_code != 200:
            print(f"Updating cookies...")
            cookies_val = requests.get(f"{cookie_url}").cookies.get('user_cookie')
            print(f'and running the app again...')
            countries = requests.get(countries_url, cookies = {"user_cookie": cookies_val}).json()

            leaders_per_country = {country: requests.get(leaders_url, cookies = {"user_cookie": cookies_val},  params = {'country': country}).json() for country in countries}

            for val in leaders_per_country.values():
                for d in val:
                    d.update({'first_paragraph': get_first_paragraph(d['wikipedia_url'], wiki_session)})
        
    return leaders_per_country

@print_timing
def save_func():
    print(f'Beware! The app is running...')
    leaders_per_country_dict = get_leaders()
    with open('notebooks/leaders.json', 'w') as f:
        json.dump(leaders_per_country_dict, f)
    print(f"Finally finished! the result is saved into notebooks/leaders.json")
save_func()