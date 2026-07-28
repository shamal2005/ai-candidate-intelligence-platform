import requests

username = input("Enter GitHub username: ")

response = requests.get(f"https://api.github.com/users/{username}/repos")
print(response.status_code)

data = response.json()
print(len(data))



language_counts = {}

for repo in data:
    language = repo["language"]
    if language in language_counts:
        language_counts[language] += 1
    else:
        language_counts[language] = 1

print(language_counts)