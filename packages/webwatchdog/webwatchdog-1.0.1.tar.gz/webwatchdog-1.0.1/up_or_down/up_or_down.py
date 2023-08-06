import requests
from colorama import init, Fore

init(autoreset=True)  # Initialize colorama for colored text

def check_website(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            print(Fore.GREEN + "✓ The website is up and running.")
        else:
            print(Fore.RED + "✗ The website is down.")
    except requests.ConnectionError:
        print(Fore.RED + "✗ The website is down.")

if __name__ == "__main__":
    website_url = input("Enter the website URL to check: ")
    check_website(website_url)

