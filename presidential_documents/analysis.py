import matplotlib.pyplot as plt
import os
from collections import defaultdict
import spacy

counts_by_year = defaultdict(lambda: {"United States": 0, "America": 0})
nlp = spacy.load("en_core_web_sm")

def check_context(ent):
    '''
    Confirms that named entity is in reference to specific context required. For 'United States', check that it is not referring to formal name of 'United States of America'. For 'America', check it is not referring to broad regions (ie: South America).
    '''
    ent_text = ent.text.lower()

    if ent_text == 'united states':
        right_sibling = ent.root.right_edge.i  
        if right_sibling > ent.end:  
            following_token = ent.doc[ent.end]  
            if following_token.text.lower() == "of":
                return False
    elif ent_text == 'america':
        left_sibling = ent.root.head.left_edge.i
        right_sibling = ent.root.head.right_edge.i
        tokens = ent.doc[left_sibling:right_sibling + 1]

        for token in tokens:
            if token.text.lower() in ['south', 'central', 'north', 'latin']:
                return False
    return True

def process_file(file_path):
    '''
    Processes text of a given file at the provided file_path by counting the number of 'United States' and 'America' that satisfy the criteria of function check_context().
    '''
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        doc = nlp(text)
        
        for ent in doc.ents:
            if ent.label_ == "GPE" and ent.text.lower() in ['united states', 'america']:
                if check_context(ent):
                    year = os.path.basename(file_path)[:4]
                    if ent.text.lower() == "america":
                        counts_by_year[year]["America"] += 1
                    else:
                        counts_by_year[year]["United States"] += 1

def display_data():
    '''
    Displays relative frequencies of 'United States' and 'America' year-by-year.
    '''
    fractions_united_states = []
    fractions_america = []
    years = sorted(counts_by_year.keys(), reverse=True)

    for year in years:
        total_mentions = counts_by_year[year]['United States'] + counts_by_year[year]['America']
        if total_mentions > 0:
            fraction_us = counts_by_year[year]['United States'] / total_mentions 
            fraction_america = counts_by_year[year]['America'] / total_mentions
        else:
            fraction_us = 0
            fraction_america = 0
        fractions_united_states.append(fraction_us)
        fractions_america.append(fraction_america)

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.barh(years, fractions_united_states, color='blue', label='United States')
    ax.barh(years, fractions_america, left=fractions_united_states, color='red', label='America')

    ax.set_xlabel('Fraction of Mentions')
    ax.set_title('Relative Frequency of "United States" vs "America" by Year')

    plt.legend()
    plt.tight_layout()
    plt.show()



def main():
    # Iterate through and process files in file_path directory
    directory_path = "./presidential_documents/addresses"
    files = os.listdir(directory_path)

    for filename in files:
        process_file(os.path.join(directory_path, filename))

    # Print results
    for year, counts in sorted(counts_by_year.items()):
        print(f"Year: {year}")
        for phrase, count in counts.items():
            print(f"  {phrase}: {count}")

    # Visualize Results
    display_data()
    

    
if __name__=="__main__": 
    main() 



