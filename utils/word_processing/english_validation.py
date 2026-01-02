import requests

def __is_valid_in_dictionary_api(word: str) -> bool:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def __is_valid_in_cambridge(word: str) -> bool:
    url = f"https://dictionary.cambridge.org/dictionary/english/{word}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        return len(response.url) >= len(url)
    except requests.exceptions.RequestException:
        return False

def is_valid_english_word(word:str)->bool:
    return __is_valid_in_dictionary_api(word) or __is_valid_in_cambridge(word)

if __name__ == "__main__":
    word = "angus"
    print(f"\nAPI Validation: {'Valid' if is_valid_english_word(word) else 'Invalid'}")
    print(f"Cambridge Validation: {'Valid' if is_valid_english_word(word) else 'Invalid'}\n")
