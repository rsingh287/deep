import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")


def get_w3schools_tutorial(topic="python dictionary"):
    clean_topic = re.sub(
        r"^(w3schools|w3school|w3schools search|w3)\s+", "", topic, flags=re.IGNORECASE
    ).strip()

    # Common W3Schools Direct Topic Mapping
    direct_topics = {
        "html": "https://www.w3schools.com/html/",
        "css": "https://www.w3schools.com/css/",
        "javascript": "https://www.w3schools.com/js/",
        "js": "https://www.w3schools.com/js/",
        "python": "https://www.w3schools.com/python/",
        "sql": "https://www.w3schools.com/sql/",
        "java": "https://www.w3schools.com/java/",
        "cpp": "https://www.w3schools.com/cpp/",
        "c++": "https://www.w3schools.com/cpp/",
        "c#": "https://www.w3schools.com/cs/",
        "cs": "https://www.w3schools.com/cs/",
        "react": "https://www.w3schools.com/react/",
        "php": "https://www.w3schools.com/php/",
        "bootstrap": "https://www.w3schools.com/bootstrap5/",
        "howto": "https://www.w3schools.com/howto/",
    }

    low = clean_topic.lower()
    if low in direct_topics:
        target_url = direct_topics[low]
    else:
        # Search W3Schools Google CS / DuckDuckGo
        target_url = f"https://www.w3schools.com/howto/howto_search.asp?q={urllib.parse.quote(clean_topic)}"

    return target_url


print("Python Dict:", get_w3schools_tutorial("w3schools python dictionary"))
print("CSS Flexbox:", get_w3schools_tutorial("w3schools css flexbox"))
print("HTML:", get_w3schools_tutorial("w3schools html"))
