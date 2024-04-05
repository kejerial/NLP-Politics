import requests
from bs4 import BeautifulSoup
import os
import time
import random
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import spacy
'''
Want to chart the raw counts of occurrences of terms “America”, “Fredonia”, “Columbia”, "United States" 
in State of the Union Addresses and Inaugural Addresses
'''
nlp = spacy.load("en_core_web_sm")

def scraper(base_url, page_range, subdir):
    base_url = base_url
    pages = page_range

    for page in pages:
        time.sleep(random.randint(0, 2))
        url = f"{base_url}{page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        addresses = soup.find_all(class_=lambda c: c and c.startswith('views-row'))

        for address in addresses:
            date_span = address.find('span', class_='date-display-single')
            year = date_span['content'][:4]
        
            about_div = address.find('div', about=True)
            link = about_div['about'] if about_div else 'Attribute not found'
            full_link = f"https://www.presidency.ucsb.edu{link}"

            subpage_response = requests.get(full_link)
            subpage_soup = BeautifulSoup(subpage_response.text, 'html.parser')
            link = link.split('/')[-1]

            filename = f"{year}.{link}.txt"

            content_div = subpage_soup.find('div', class_='field-docs-content')
            content_text = content_div.get_text(separator="\n", strip=True) if content_div else "Content not found"

            subdirectory = subdir
            file_path = os.path.join(subdirectory, filename)

            if not os.path.exists(subdirectory):
                os.makedirs(subdirectory)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(year + ' ' + link.title().replace('-', ' ') + '\n\n')
                file.write(content_text)
                file.close()

def runScrapers():
    # State of the Union Addresses
    scraper("https://www.presidency.ucsb.edu/documents/app-categories/spoken-addresses-and-remarks/presidential/state-the-union-addresses?page=", range(0,10), "presidential_documents/state-of-the-union")
    scraper("https://www.presidency.ucsb.edu/documents/app-categories/citations/presidential/state-the-union-written-messages?page=", range(0,15), "presidential_documents/state-of-the-union")

    # Inaugural Addresses
    scraper("https://www.presidency.ucsb.edu/documents/app-categories/spoken-addresses-and-remarks/presidential/inaugural-addresses?page=", range(0,7), "presidential_documents/inaugural")

def displayData(dict):
    # Sort the years for consistent plotting
    years = sorted(dict.keys())
    
    # Assuming all years have the same structure, use the first year to get the list of terms
    terms = dict[next(iter(years))].keys()
    
    # Preparing data for plotting: For each term, compile its counts across all years
    data = {term: [dict[year][term] for year in years] for term in terms}
    
    # Setting up the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Number of terms and creating an index for each year group
    num_terms = len(data)
    indices = np.arange(len(years))
    
    # Width of a bar
    width = 0.2

    # Plotting each term
    for i, (term, counts) in enumerate(data.items()):
        ax.bar(indices + i * width, counts, width, label=term)

    # Adding some text for labels, title, and custom x-axis tick labels, etc.
    ax.set_xlabel('Year')
    ax.set_ylabel('Counts')
    ax.set_title('Counts by Year for Each Term in State of the Union Addresses')
    ax.set_xticks(indices + width * (num_terms - 1) / 2)
    ax.set_xticklabels(years)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.legend()

    # Rotating the x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.legend(title="Terms")
    plt.tight_layout()

    plt.show()

def check_context(ent):
    ent_text = ent.text.lower()
    """ if 'united states' in ent_text:
        right_sibling = ent.root.right_edge.i  
        if right_sibling > ent.end:  
            following_token = ent.doc[ent.end]  
            if following_token.text.lower() == "of":
                return False """
    if 'america' in ent_text:
        left_sibling = ent.root.head.left_edge.i
        right_sibling = ent.root.head.right_edge.i
        tokens = ent.doc[left_sibling:right_sibling + 1]

        for token in tokens:
            if token.text.lower() in ['south', 'central', 'north', 'latin']:
                return False
        """     
    elif ent_text == 'columbia':
        left_sibling = ent.root.left_edge.i
        if left_sibling < ent.start:
            preceding_token = ent.doc[ent.start]
            if preceding_token.text.lower() == "of":
                return False """
    return True

def process_file(file_path, dictionary):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        doc = nlp(text)
        year = os.path.basename(file_path)[:4]
        phrases = ['united states', 'america', 'fredonia']

        for ent in doc.ents:
            ent_text = ent.text.lower()
            if any(ele in ent_text for ele in phrases) and check_context(ent):
                # America but not United States of America or American
                if "america" in ent_text and "american" not in ent_text and "united states" not in ent_text:
                    dictionary[year]["America"] += 1
                # United States or United States of America
                elif "united states" in ent.text.lower() and "constitution" not in ent_text:
                    dictionary[year]["United States"] += 1
                elif "fredonia" in ent.text.lower():
                    dictionary[year]["Fredonia"] += 1

def analysis(directory_path, dictionary):
    files = os.listdir(directory_path)

    for filename in files:
        if int(filename[:4]) in range(1850,1950):
            process_file(os.path.join(directory_path, filename), dictionary)
            print(filename)

    # Print results
    for year, counts in sorted(dictionary.items()):
        print(f"Year: {year}")
        for phrase, count in counts.items():
            print(f"  {phrase}: {count}")
    
    return dictionary

def main():
    inaugural_counts = defaultdict(lambda: {"United States": 0, "America": 0, "Fredonia": 0})
    sotu_counts = defaultdict(lambda: {"United States": 0, "America": 0, "Fredonia": 0})
    #inaugural_counts = analysis("./presidential_documents/inaugural", inaugural_counts)
    sotu_counts = analysis("./presidential_documents/state-of-the-union", sotu_counts)
    #displayData(inaugural_counts)
    displayData(sotu_counts)

if __name__=="__main__":
    main()
