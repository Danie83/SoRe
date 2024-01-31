import pandas as pd
import re
import string
 
datasets = ["description_1.csv", "description_3.csv"]
columns = ["Comment", "Text"]

def remove_tags(input_string):
    cleaned_string = re.sub(r'@[\w]+', '', input_string)
    cleaned_string = cleaned_string.strip()
    cleaned_string = cleaned_string.lstrip(string.punctuation)
    cleaned_string = cleaned_string.strip('"')
    cleaned_string = cleaned_string.strip()
    return cleaned_string

combined_data = pd.DataFrame()

for dataset, column in zip(datasets, columns):
    data = pd.read_csv(f"datasets/{dataset}")
    combined_data = pd.concat([combined_data, data[column]], axis=0, ignore_index=True)

combined_data.columns = ["Description"]
combined_data['Description'] = combined_data['Description'].apply(remove_tags)

combined_data.to_csv("datasets/combined_data.csv", index=False)