import pandas as pd
import numpy as np
import pickle
import seaborn as sns

from matplotlib import pyplot as plt
from medcat.cat import CAT
import re
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')


# # Load model pack and Create CAT - the main class from medcat used for concept annotation

# model_pack_path = 'mc_modelpack_snomed_int_16_mar_2022_25be3857ba34bdd5'
# cat = CAT.load_model_pack(model_pack_path)

# print('model loaded')
medical_stopwords = stopwords.words("english")
medical_stopwords.extend(['speaking', 'none', 'time', 'flush'])

def process_clinical_note(clinical_note):
    # Define the sections to remove
    sections_to_remove = [
        "Name:",
        "Unit No:",
        "Admission Date:",
        "Discharge Date:",
        "Date of Birth:",
        "Sex:",
        "Service:",
        "Allergies:",
        "Attending:",
        "Past Medical History:",
        "Social History:",
        "Family History:",
        "Vitals:",
        "Pertinent Results:",
        "Medications on Admission:",
        "Discharge Medications:",
        "Discharge Disposition:",
        "Discharge Condition:",
        "Discharge Instructions:",
        "Followup Instructions:"
    ]

    # Split the clinical note into lines
    lines = clinical_note.split('\n')

    # Initialize the processed note
    processed_note = []

    # Flag to exclude lines within unwanted sections
    exclude_section = False

    # Iterate through the lines and filter unwanted sections
    for line in lines:
        if any(section in line for section in sections_to_remove):
            exclude_section = True
        elif line.strip() == "":
            # Empty lines separate sections, so reset the flag
            exclude_section = False

        if not exclude_section:
            processed_note.append(line)

    # Join the lines to create the final note
    final_note = '\n '.join(processed_note)
    
    sections_to_remove = [
        r'chief complaint',
        r'history of present illness',
        r'Major Surgical or Invasive Procedure',
        r'physical exam',
        r'brief hospital course',
        r'Discharge',
        
        r'completed by',
    ]
    
    for pattern in sections_to_remove:
        final_note = re.sub(pattern, '', final_note, flags=re.IGNORECASE)

    # Define patterns to identify negations
    negation_patterns = [
        r'no\s+\w+',
        r'not\s+\w+',
        r'did\s+not\s+have\s+\w+'
    ]
    
    # Filter out sentences with negations
    sentences = [sentence for sentence in final_note.split('\n') if not any(re.search(pattern, sentence, re.IGNORECASE) for pattern in negation_patterns)]

    # Remove keys and special characters
    cleaned_note = re.sub(r'\w+:', '', '\n'.join(sentences), flags=re.IGNORECASE)  # Remove keys (case-insensitive)
    cleaned_note = re.sub(r'[^a-zA-Z\s]', '', cleaned_note)  # Remove special characters
    # Tokenize the note into sentences based on '\n'
    sentences = [sentence.strip() for sentence in cleaned_note.split('\n') if sentence.strip()]

    # Remove stop words and empty sentences
    sentences = [
        ' '.join(word for word in sentence.split() if word.lower() not in medical_stopwords)
        for sentence in sentences
    ]
    sentences = [item for item in sentences if item != '']
    
    final_text = '. '.join(sentence for sentence in sentences)
    return final_text

def reformat(code):
    code = ''.join(code.split('.'))
    code = code[:3] + '.'
    return code



model_pack_path = 'mc_modelpack_snomed_int_16_mar_2022_25be3857ba34bdd5'
cat = CAT.load_model_pack(model_pack_path)



def predict_codes_using_SNOMED(cat,processed_example):
    # Get the entities from the text
    all_entities = cat.get_entities(processed_example)

    icd_codes = set()  # Using a set to automatically remove duplicates
    for entity_id, entity_data in all_entities['entities'].items():
        icd10 = entity_data.get('icd10', [])
        for code in icd10:
            if code:  # Check if the code is not an empty string
                code = reformat(code)
                icd_codes.add(code)


    return list(icd_codes)


def main():

    st.title("ICD-10 Coder")

    html_temp = """
    <div style="background-color:green;padding:10px">
    <h2 style="color:white;text-align:center;">Covid 19 Detection App </h2>
    </div>
    """
    st.markdown(html_temp,unsafe_allow_html=True)

    text = st.text_input("Please input your clinical text")

    processed_text = process_clinical_note(text)

    resultant_icd_codes = predict_codes_using_SNOMED(cat, processed_example)



    result= []

    if st.button("Predict"):
        resultant_icd_codes = predict_codes_using_SNOMED(cat, processed_example)
    
    
    st.write(predict_note_authentication)


if __name__=='__main__':
    main()