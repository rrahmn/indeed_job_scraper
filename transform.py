import openai
import json
import streamlit as st

# Set up OpenAI API key
openai.api_key = st.secrets.db_credentials.api_key

def generate_response(job_text_summary):
    """function to extract key info from job text"""
    job_text_summary = job_text_summary.replace("&nbsp", "")
    key_prompt_info = """Don't do anything until you've read the text. Once you've read it, extract the location, industry, job type(permanent or temporary etc), hybrid/remote/onprem, company name, salary per year, summary of job post, top 3 tech stacks, top 3 skills required, whether the job is suited for a junior/senior. If any info is missing just say n/a and if salary is per day or per week or a range estimate itper year or take average of range. Return the results always in lower case in the following example json format {"location" : "london", "industry": "retail", "job type": "permanent", "wfh": "onprem", "company name": "sky", "salary_per_year": "20000", "summary": "", "tech_stack": "", "skills": "", "level": "junior"}"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"{key_prompt_info} Here is the text : {job_text_summary}"}
        ],
        max_tokens=200,
        n=1
    )
    return response['choices'][0]['message']['content'].strip()


def validate_response(response):
    """Check if the response matches the desired format"""
    try:
        data = json.loads(response)
        required_keys = ["location", "industry", "job type", "wfh", "company name", "salary_per_year", "summary", "tech_stack", "skills", "level"]
        if all(key in data for key in required_keys):
            return True
    except json.JSONDecodeError:
        return False
    return False


def get_valid_response(job_text_summary, n=3):
    """Attempt to generate a valid response up to n times."""
    attempts = 0
    while attempts < n:
        response = generate_response(job_text_summary)
        if validate_response(response):
            return response
        attempts += 1
    
    # Return a response with "n/a" for all fields if unable to generate a valid response
    return json.dumps({
        "location": "n/a",
        "industry": "n/a",
        "job type": "n/a",
        "wfh": "n/a",
        "company name": "n/a",
        "salary_per_year": "n/a",
        "summary": "n/a",
        "tech_stack": "n/a",
        "skills": "n/a",
        "level": "n/a"
    })

def open_database(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except:
        with open(file_path, 'w') as file:
            json.dump([], file)  # Initialize file with an empty list
            return []

def save_to_transformed_database(file_path, data):
    """Appends data to the JSON file specified by file_path. If the file does not exist, it will be created."""
    database = open_database(file_path)  
    database.append(data)  
    with open(file_path, 'w') as file:
        json.dump(database, file, indent=4)  

def main():
    database = open_database("raw_database_data_engineer.json")
    transformed_database = open_database("transformed_database.json")
    
    transformed_ids = {entry['id'] for entry in transformed_database} 
    for entry in database:
        if entry['id'] in transformed_ids:
            continue  # Skip this iteration if the ID is already in the transformed database

        job_text_summary = entry['description']
        merged_result = {key: entry[key] for key in entry if key != 'description'}
        
        additional_data = json.loads(get_valid_response(job_text_summary))
        merged_result.update(additional_data)
        
        save_to_transformed_database("transformed_database.json", merged_result)
        transformed_ids.add(entry['id'])  # Update the set of IDs with the new entry

if __name__ == "__main__":
    main()