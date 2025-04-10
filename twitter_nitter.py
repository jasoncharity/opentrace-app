import requests
import json

def search_nitter(query, limit=5):
    base_url = "https://nitter.net"
    search_url = f"{base_url}/search"
    params = {
        "q": query,
        "f": "tweets"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(search_url, params=params, headers=headers)

    if response.status_code != 200:
        print("Error fetching tweets:", response.status_code)
        return []

    # Nitter doesn't have a structured API — you'd normally parse HTML
    # For now, we treat this as manual fallback or wait for SerpAPI/GPT vision
    print("HTML preview (trimmed):\n")
    print(response.text[:1000])  # Show first 1000 characters for inspection

    return response.text

if __name__ == "__main__":
    query = "Alexander Jones Doncaster"
    search_nitter(query)