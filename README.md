Streamlit app that displays data engineering roles scraped off indeed can be found at: https://dataengineeringindeed.streamlit.app/

### **Introduction**

### **The Job Search Dilemma**

- Overwhelming amounts of texts presented to job seekers.
- The important stuff never seems to be there or hidden.

---

### **Problem Statement**

- **Question:** "How can we extract important information from job posts and give users summaries to read?"

---

### **Solution Overview**

### **An Automated Three-Component Pipeline**

- **Frequency of Execution:** Runs every 15 minutes to ensure data is current and comprehensive.

**Component 1: Data Scraping & Extraction**

- Uses Selenium for real-time web scraping from job sites.
- Captures essential job details: titles, IDs, links, and descriptions.
- Overcomes captcha challenges using dynamically sourced free proxies.
  - Human vs bot
  - Issue when visiting indeed too often too quick
  - Solution: https://free-proxy-list.net/
- Stores data in **`raw_data.json`** for initial processing.

**Component 2: Data Transformation via LLM (ChatGPT Turbo 3.5)**

- Transforms erratic, unstructured text into concise, structured summaries.
- Ensures no duplicate processing, enhancing efficiency.
- Outputs refined data into **`transformed_database.json`**.

**Component 3: Database Integration**

- Writes transformed data to MongoDB, a flexible and scalable database.
- Only updates with new and unique entries to maintain database integrity.
- Facilitates efficient data retrieval for analysis and application use.

  ![image](https://github.com/rrahmn/indeed_job_scraper/assets/125041778/2c2e27b2-7b12-4c4b-adab-0c6518741373)
