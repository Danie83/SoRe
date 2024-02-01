import pandas as pd
import re
import string
import numpy as np

datasets = ["description_1.csv", "description_2.csv", "description_3.csv", "description_4.csv", "description_5.csv", "description_6.csv", "description_7.csv", "description_8.csv", "description_9.csv"]
columns = ["Comment", "Text", "Text", "text", "Subtitle", "text", "Subtitle", "text", "text"]

def remove_tags(input_string):
    cleaned_string = re.sub(r'@[\w]+', '', input_string)
    cleaned_string = cleaned_string.strip()
    cleaned_string = cleaned_string.lstrip(string.punctuation)
    cleaned_string = cleaned_string.strip('"')
    cleaned_string = cleaned_string.strip()
    return cleaned_string

def contains_word_in_brackets(cell):
    if pd.isna(cell):
        return True
    pattern = r'\[.*\]'
    return bool(re.search(pattern, cell))

combined_data = pd.DataFrame()

for dataset, column in zip(datasets, columns):
    data = pd.read_csv(f"datasets/{dataset}")
    combined_data = pd.concat([combined_data, data[column]], axis=0, ignore_index=True)

combined_data.columns = ["Description"]

combined_data["Description"] = combined_data["Description"].replace(np.nan, '', regex=True)
combined_data = combined_data.dropna(subset=['Description'])

combined_data["Description"] = combined_data["Description"].drop_duplicates(keep='first')

mask = combined_data['Description'].apply(contains_word_in_brackets)
combined_data = combined_data[~mask]

combined_data['Description'] = combined_data['Description'].apply(remove_tags)

combined_data.to_csv("datasets/combined_data.csv", index=False)