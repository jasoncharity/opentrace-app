import requests
import json

def search_reddit(query, size=10):
    url = "https://api.pushshift.io/reddit/search/submission/"
    params = {
        "q": query,
        "sort": "desc",
        "sort_type": "score",
        "size": size
    }
    response = requests.get(url, params=params)
    return response.json().get("data", [])

def save_reddit_results(posts, filename="output_reddit.json"):
    with open(filename, "w") as f:
        json.dump(posts, f, indent=2)

if __name__ == "__main__":
    name = "Alexander Jones Doncaster"
    results = search_reddit(name)

    print(f"Found {len(results)} Reddit posts")
    for post in results:
        print(f"- {post.get('title', 'No title')}")
        print(f"  https://reddit.com{post.get('permalink', '')}\n")

    save_reddit_results(results)
    print("Saved Reddit posts to output_reddit.json")