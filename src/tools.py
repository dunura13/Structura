import spacy
import re
import pandas as pd
from langchain_core.tools import tool




# load SPACY
try:
    nlp = spacy.load("en_core_web_sm")

except:

    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")



# first tool: the cleaner tool
 # this tool is to clean dirty OCR text before extraction (extra spaces, newlines), standardizes formatting
@tool
def clean_text_tool(raw_text: str) -> str:
    """
    Use this tool to clean dirty OCR text before extraction.
    It removes extra spaces, fixes newlines, and standardizes formatting.
    """
    
    # pass text through SpacCy's pipeline
    doc = nlp(raw_text)

    # cleaning logic, remove OCR artifacts
    tokens = [token.text for token in doc if not token.is_space]
    cleaned_text = " ".join(tokens)


    # Python Regex for additional space cleanup
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text



# second tool: pandas dataframe builder, simulates saving to database

def save_to_dataframe(data_dict: dict) -> pd.DataFrame:
    '''
    converts a dict of extracted data into a Pandas DataFrame
    '''

    df = pd.DataFrame([data_dict])
    return df




# test code

if __name__ == "__main__":
    messy_input = "Concrete shall be \n\n Type V   sulfate  resistant."
    print("--- RAW ----")
    print(messy_input)

    print("\n--- CLEANED (via SpaCy) ---")
    clean_output = clean_text_tool.invoke(messy_input)
    print(clean_output)




