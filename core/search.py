import openai
import json
import requests
import tiktoken
import urllib.parse
from bs4 import BeautifulSoup
from config import OPENAI_KEY, brave_search_api_key, scraperapi_key

def create_message(name, url):
    return [
        {
            "role": "system",
            "content": f"Please prepare a detailed research report on {name}. The primary source for this report is {url}. The report should contain key insights, relevant statistics, and notable findings from the source. Structure the report with an introduction, body, and conclusion."
        }
    ]


def create_search_message(profile, name):
    return [
        {
            "role": "system",
            "content": f"Given the existing research report on {name} - {profile}, please suggest a search term that would be most useful for further refining and enhancing the report. Your response should solely consist of the proposed search term which is expected to yield additional relevant and beneficial information."
        }
    ]


def create_update_message(profile, name, search_content):
    return [
        {
            "role": "system",
            "content": f"The current report on {name} is as follows: {profile}. Please add to and revise this report using the following additional content: {search_content}. In your response, please provide the entire revised report."
        }
    ]



def get_page_content(url):
    headers = {"apikey": scraperapi_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Use BeautifulSoup to parse HTML and extract text
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style tags
        for script in soup(["script", "style"]):
            script.extract()
        
        page_content = soup.get_text(separator=' ')  # Add a space as a separator for better tokenization
        
        # Trim content to token limit
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(page_content)
        if len(tokens) > 2000:  # If tokens exceed the limit
            excess = len(tokens) - 2000
            page_content = tokenizer.decode(tokens[:-excess])
        return page_content
    else:
        return None


def search_brave(search_term):
    headers = {"Accept": "application/json", "X-Subscription-Token": brave_search_api_key}
    query = urllib.parse.quote(search_term)
    response = requests.get(f"https://api.search.brave.com/res/v1/web/search?q={query}", headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)  # Print the response to debug
        try:
            return response_json['web']
        except KeyError:
            print("No 'web' key in the response. The search term might not have returned any results.")
            return None
    else:
        print(f"Request to Brave Search API failed with status code {response.status_code}.")
        return None



def prospect(name, rounds):
    rounds = int(rounds)
    openai.api_key = OPENAI_KEY
    scraped_urls = []  # store the scraped urls here

    print(f"Searching for initial information about {name}...")
    initial_search_results = search_brave(name)
    if initial_search_results and initial_search_results['results']:
        print("Scraping content from the first search result...")
        first_result = initial_search_results['results'][0]
        scraped_urls.append(first_result['url'])  # add url to scraped urls
        page_content = get_page_content(first_result['url'])

        print("Creating initial profile...")
        initial_message = create_message(name, page_content)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=initial_message
        )

        profile = response.choices[0].message['content']
        print(f"Initial profile for {name}: {profile}")

        # Save the initial profile to a text file
        print(f"Saving initial profile to a text file...")
        with open(f"{name}_profile_round_0.txt", "w") as file:
            file.write(profile)

    else:
        print("No search results found for initial search.")
        return

    # Iteratively refine the profile
    for i in range(rounds):
        print(f"Starting refinement round {i + 1}...")
        search_message = create_search_message(profile, name)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=search_message
        )

        search_term = response.choices[0].message['content']
        search_term = search_term.replace("Search: ", "")
        search_term = search_term.replace('"', '')  # remove quotes from search term
        print(f"Search term for this round: {search_term}")

        print("Getting search results from Brave Search...")
        search_results = search_brave(search_term)
        if search_results and search_results['results']:
            print("Scraping content from the first search result not yet scraped...")
            for result in search_results['results']:
                if result['url'] not in scraped_urls:  # check if the url is not already scraped
                    first_result = result
                    scraped_urls.append(first_result['url'])  # add url to scraped urls
                    page_content = get_page_content(first_result['url'])

                    print("Updating profile with new information...")
                    update_message = create_update_message(profile, name, page_content)
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=update_message
                    )

                    profile = response.choices[0].message['content']
                    print(f"Updated profile for {name}: {profile}")
                    
                    # Save the updated profile to a text file
                    print(f"Saving profile after round {i + 1} to a text file...")
                    with open(f"{name}_profile_round_{i + 1}.txt", "w") as file:
                        file.write(profile)
                    break

    # Save the final profile to a text file
    print("Saving final profile to a text file...")
    with open(f"{name}_final_profile.txt", "w") as file:
        file.write(profile)
    
    return profile 

    # Print the final profile
    print(f"Here is the final profile for {name}: {profile}")
