import requests
import json

google_search_api = "AIzaSyCIkSFFwm_evB1UzTl_YPb_CaL5udRaYWM"
search_engine_id = '72dab577d8eff4361'

web_search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Use to perform a web search. Use when user needs something from the internet.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on the web."
                }
            },
            "required": ["query"]
        }
    }
}



def web_search(query:str) -> str:
    results = "[web pages] "
    results += str(google_custom_search(google_search_api, search_engine_id, query, num_results=4))
    results += " [images urls]"
    results += str(google_custom_search_images(google_search_api, search_engine_id, query, num_results=10))
    return json.dumps(results, ensure_ascii=False)
    

def google_custom_search(api_key, search_engine_id, query, num_results=10):
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'num': num_results
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        search_results = response.json()
        
        # Extract relevant information from the response
        results = []
        for item in search_results.get('items', []):
            result = {
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet')
            }
            results.append(result)
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return ["Error finding web pages"]

def google_custom_search_images(api_key, search_engine_id, query, num_results=8):

    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'num': num_results,
        'searchType': 'image'  # Specify that we want image results
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        search_results = response.json()
        # print(search_results)  # Print the full response for debugging
        
        # Extract relevant information from the response
        results = []
        for item in search_results.get('items', []):
            result = {
                'title': item.get('title'),
                'link': item.get('link'),  # URL of the image
            }
            results.append(result)
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        print(response.text)  # Print the error response for debugging
        return ["Error finding images"]


if __name__ == "__main__":
    print(web_search("масса слона"))