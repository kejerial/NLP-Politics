import requests
from bs4 import BeautifulSoup
import os
import time
import random

base_url = "https://www.presidency.ucsb.edu/documents/app-categories/presidential/spoken-addresses-and-remarks?items_per_page=60w&page="
pages = range(487, 538)

for page in pages:
    time.sleep(random.randint(0, 2))
    url = f"{base_url}{page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    addresses = soup.find_all(class_=lambda c: c and c.startswith('views-row'))

    for address in addresses:
        date_span = address.find('span', class_='date-display-single')
        year = date_span['content'][:4]
        if (1850 <= int(year) <= 1950):
            about_div = address.find('div', about=True)
            link = about_div['about'] if about_div else 'Attribute not found'
            full_link = f"https://www.presidency.ucsb.edu{link}"

            subpage_response = requests.get(full_link)
            subpage_soup = BeautifulSoup(subpage_response.text, 'html.parser')
            link = link.split('/')[-1]

            filename = f"{year}.{link}.txt"

            content_div = subpage_soup.find('div', class_='field-docs-content')
            content_text = content_div.get_text(separator="\n", strip=True) if content_div else "Content not found"

            subdirectory = 'addresses'
            file_path = os.path.join(subdirectory, filename)

            if not os.path.exists(subdirectory):
                os.makedirs(subdirectory)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(year + ' ' + link.title().replace('-', ' ') + '\n\n')
                file.write(content_text)
                file.close()




