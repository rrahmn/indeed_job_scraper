from pymongo import MongoClient
import json
import streamlit as st


MONGO_URI= st.secrets.db_credentials.MONGO_URI
DB_NAME = st.secrets.db_credentials.DB_NAME
COLLECTION_NAME= st.secrets.db_credentials.COLLECTION_NAME

def main():
    f_path = './transformed_database.json' #./transformed_database.json


    client = MongoClient(
        MONGO_URI,
        #bypass connection errors
        tls=True,  
        tlsAllowInvalidCertificates=True  
    )
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    col_counter = db['counter']

    # find current counter or initialize to 0
    doc_counter = col_counter.find_one({"_id": "job_counter"})
    if doc_counter is None:
        current_count = 0
        col_counter.insert_one({"_id": "job_counter", "count": current_count})
    else:
        current_count = doc_counter['count']



    with open(f_path, 'r') as file:
        data = json.load(file)

    total_jobs = len(data)   
    new_jobs = total_jobs - current_count  


    if new_jobs > 0:
        new_jobs = data[-new_jobs:]
        inserted_docs = collection.insert_many(new_jobs)

        # Update counter
        col_counter.update_one(
            {"_id": "job_counter"},
            {"$set": {"count": total_jobs}}
        )


    client.close()
            



if __name__ == "__main__":
    main()

    