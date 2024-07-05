import logging
from flask import Blueprint, request, jsonify, render_template, g
import sqlite3
import uuid
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import time
import re

logger = logging.getLogger(__name__)  # Use the existing logger

logger.info("Initializing main blueprint")
main = Blueprint('main', __name__)

load_dotenv()

# Load the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Instantiate the OpenAI client at the module level
client = OpenAI(api_key=OPENAI_API_KEY)

def json_format(value):
    return json.dumps(value, indent=2)

@main.app_context_processor
def inject_json_format():
    

def sanitize_json_string(json_string):
    # Remove any invalid control characters
    sanitized_string = re.sub(r'[\x00-\x1f\x7f]', '', json_string)
    return sanitized_string

def extract_info(submission_type, submission_text):
    submissions = submission_text.split('#DF')
    extracted_data = []

    for submission in submissions:
        
    print(f"Type of extracted_data in extract_info: {type(extracted_data)}")
    if isinstance(extracted_data, list):
        print("extracted_data is a list in extract_info.")
    elif isinstance(extracted_data, dict):
        print("extracted_data is a dictionary in extract_info.")
    else:
        print("extracted_data is neither a list nor a dictionary in extract_info.")
    return extracted_data

# Function to fetch all existing IDs from the database
def fetch_existing_ids():
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect('job_candidate_manager.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM candidate_profiles")
        existing_ids = {row[0] for row in cursor.fetchall()}
    finally:
        if cursor:
            
        if conn:
            
    return existing_ids

def process_submissions(submission_text, process_function, submission_type):
    submissions = submission_text.split('#DF')
    extracted_data = []

    # Fetch existing IDs from the database
    existing_ids = fetch_existing_ids()

    for submission in submissions:
        try:
            
        except Exception as e:
            
    return extracted_data

def extract_data_from_submission(submission, process_function):
    logging.info("Starting extract_data_from_submission")
    prompt = generate_prompt(submission, process_function)
    logging.info(f"Generated prompt: {prompt}")

    retry_attempts = 5
    for attempt in range(retry_attempts):
        logging.info(f"Attempt {attempt + 1} of {retry_attempts}")
        try:
            logging.info("Attempting to call OpenAI API")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a highly skilled information extractor."},
                    {"role": "user", "content": prompt}
                ]
            )
            logging.info("OpenAI API call successful")
            raw_response = response.choices[0].message.content
            logging.info(f"Raw API response: {raw_response}")  # Log raw API response
            break  # If the request is successful, break out of the loop
        except OpenAI.error.RateLimitError as e:
            wait_time = 2 ** attempt  # Exponential backoff
            logging.error(f"Rate limit exceeded. Retrying in {wait_time} seconds. Error: {e}")
            time.sleep(wait_time)
        except Exception as e:
            logging.error(f"Error during processing submission: {e}")
            return None
    else:
        logging.error("Exceeded maximum retry attempts due to rate limiting.")
        return None

    if not response.choices or not response.choices[0].message or not response.choices[0].message.content:
        logging.error('Invalid response from OpenAI!')
        return None

    extracted_info = raw_response.strip()
    logging.info(f"Extracted info: {extracted_info}")

    # Sanitize the extracted info
    sanitized_info = sanitize_json_string(extracted_info)
    logging.info(f"Sanitized info: {sanitized_info}")

    logging.info("Calling validate_and_clean_json")
    cleaned_json = validate_and_clean_json(sanitized_info)
    logging.info(f"validate_and_clean_json returned: {cleaned_json}")
    return cleaned_json

def generate_prompt(submission, process_function):
    if process_function == process_job_post:
        
    elif process_function == process_candidate_profile:": prompt}
                ]
            )
            logging.info("OpenAI API call successful")
            raw_response = response.choices[0].message.content
            logging.info(f"Raw API response: {raw_response}")  # Log raw API response
            break  # If the request is successful, break out of the loop
        except openai.error.RateLimitError as e:
            wait_time = 2 ** attempt  # Exponential backoff
            logging.error(f"Rate limit exceeded. Retrying in {wait_time} seconds. Error: {e}")
            time.sleep(wait_time)
        except Exception as e:
            logging.error(f"Error during processing submission: {e}")
            return None
    else:
        logging.error("Exceeded maximum retry attempts due to rate limiting.")
        return None

    if not response.choices or not response.choices[0].message or not response.choices[0].message.content:
        logging.error('Invalid response from OpenAI!')
        return None

    extracted_info = raw_response.strip()
    logging.info(f"Extracted info: {extracted_info}")

    # Sanitize the extracted info
    sanitized_info = sanitize_json_string(extracted_info)
    logging.info(f"Sanitized info: {sanitized_info}")

    logging.info("Calling validate_and_clean_json")
    cleaned_json = validate_and_clean_json(sanitized_info)
    logging.info(f"validate_and_clean_json returned: {cleaned_json}")
    return cleaned_json

def generate_prompt(submission, process_function):
    if process_function == process_job_post:
        return f"""
        Begin your response with the JSON array and make sure to return valid JSON only. Multiple job posts may be submitted, and they will be separated by '#DF'. Ensure you extract and organize the information for each job post into the following categories:
        [
            {{
                "id": "app will generate ID and populate here",
                "Company Name": "Extract the name of the company.",
                "Role": "Extract the name of the role being hired.",
                "Level": "Extract the level of seniority for the role. Normalize outputs to be one of the following: 'Manager, Senior Manager, Director, Senior Director, VP'. Note that 'Controller' falls in the VP category unless specified otherwise (e.g., 'Controller Director').",
                "Salary": "Extract the salary or salary range.",
                "Salary Median": "If the salary is a range, calculate the median and populate with it.",
                "Location": "Extract the location of the job. If the job post specifies an office location different from the company's location, use the office location.",
                "State": "Extract the state where the job is to be performed. The job location state trumps the company's state.",
                "Setting": "Specify if the job is Remote, Hybrid, or On-site.",
                "In-State?": "For remote jobs exclusively, indicate Yes or No depending on whether the company specifies that the remote employee must be located in a specific state.",
                "Industry": "Use GPT to determine the industry of the company. If mentioned in the text, use it but normalize to broad categories like Technology or Healthcare. If not known, populate 'NF'.",
                "Public": "Specify Yes or No if GPT can determine if the company is public. If not known, populate 'NF'.",
                "Employee Count": "Extract only if mentioned in the text. If not known, populate 'NF'.",
                "Revenue": "Extract only if mentioned in the text. If not known, populate 'NF'.",
                "Benefits": "Extract the benefits from the job post.",
                "Relocation": "Extract relocation details from the job post.",
                "Undergraduate": "Extract details of the required undergraduate education.",
                "Postgraduate": "Extract details of the required postgraduate education.",
                "Experience": "Extract the years of experience required.",
                "Field(s)": "Extract the tax fields of experience required.",
                "CPA": "Extract the CPA requirement. Populate as Yes, No, or Desirable depending on the wording.",
                "Certifications": "Extract other certifications mentioned. Populate as Yes, No, or Desirable for each.",
                "Strategic Responsibilities": "Extract strategic responsibilities from the job post.",
                "Operational Responsibilities": "Extract operational responsibilities from the job post.",
                "Team Management": "Extract team management responsibilities from the job post.",
                "Budgetary Control": "Extract budgetary control responsibilities from the job post.",
                "Decision-Making Authority": "Extract decision-making authority details from the job post.",
                "Reporting Structure": "Extract reporting structure details from the job post.",
                "Cross-Functional Teams": "Extract cross-functional team details from the job post.",
                "Company Culture": "Extract anything referring to company culture.",
                "Technology Proficiency": "Extract text from the job post referring to technologies used or technology experience needed or desired.",
                "Stakeholder Engagement": "Extract anything referring to engagement with stakeholders.",
                "Travel Requirements": "Extract travel requirements.",
                "Succession Planning": "Extract succession planning.",
                "Crisis Management": "Extract any reference to crisis management.",
                "Leadership Style": "Extract anything referencing leadership styles or qualities desired in a candidate.",
                "Change Management": "Extract anything that refers to change management.",
                "Risk Management": "Extract anything referencing risk management experience required or desired.",
                "Job Posting Source": "Extract from job post.",
                "Date Job Posted": "Extract the date posted from job post.",
                "Date Job Tracked": "Today's date.",
                "Works With Recruiters": "Extract whether they work with recruiters, search firms, placement firms, head hunters, or any other synonym of the profession. If nothing is mentioned about it, populate 'Yes'. If they state they don't work with recruiters, populate 'No'.",
                "Soft Skills": "Extract soft skills required from the job post.",
                "Hard Skills": "Extract hard skills required from the job post.",
                "Job Description Summary": "Extract a summary of the job description.",
                "Other Requirements": "Extract any other requirements mentioned in the job post."
            }}
        ]
        Here is the job post: {submission}
        Make sure to return valid JSON only.
        """
    elif process_function == process_candidate_profile:
        return f"""
        Multiple candidate profiles may be submitted, and they will be separated by '#DF'. Ensure you extract and organize the information for each candidate into the following categories:
        [
            {{
                "id": "app will generate ID and populate here",
                "First Name": "Extract the first name of the candidate.",
                "Last Name": "Extract the last name of the candidate.",
                "Current Title": "Extract the candidate's current job title.",
                "Current Level": "Extract and normalize the current level or seniority of the candidate.",
                "Current Company": "Extract the name of the company the candidate is currently working for.",
                "Location": "Extract the current location (city and country) of the candidate.",
                "Current Job": "Provide a description of the candidate's current job role and responsibilities.",
                "Time at Current Job": "Extract the duration the candidate has been in their current job.",
                "Previous Positions": "Extract details of the candidate's previous job positions.",
                "Current Operational Responsibilities": "Extract specific operational responsibilities from the candidate's current job.",
                "Current Strategic Responsibilities": "Extract specific strategic responsibilities from the candidate's current job.",
                "Operational Responsibilities": "Extract general operational responsibilities the candidate has handled in the past.",
                "Strategic Responsibilities": "Extract general strategic responsibilities the candidate has handled in the past.",
                "Undergraduate": "Extract details of the candidate's undergraduate education.",
                "Postgraduate": "Extract details of the candidate's postgraduate education.",
                "Skills": "List the candidate's skills.",
                "Key Skills Related to Tax/Finance": "Extract key skills specifically related to tax or finance.",
                "Projects": "Extract information about significant projects the candidate has worked on.",
                "Achievements": "Extract notable achievements of the candidate.",
                "Awards and Honors": "Extract any awards and honors the candidate has received.",
                "Group Memberships": "Extract information about professional or industry group memberships.",
                "Causes": "Extract information about causes the candidate supports or is passionate about.",
                "Newsletters": "Extract information about any newsletters the candidate subscribes to or publishes.",
                "Interests": "Extract interests.",
                "Tax Specialization": "Analyze entire profile and determine areas of tax specialization.",
                "Links to Blog Posts": "Extract links to any blog posts written by the candidate.",
                "Articles": "Extract titles and links to any articles written by the candidate.",
                "CPA": Extract whether the candidate is a CPA. "Y" if they are, "NA" if they aren't or it isn not mentioned.",
                "Certifications": "Extract details of any certifications the candidate holds.",
                "Professional Associations": "Extract professional associations.",
                "Tax Software Experience": "Extract experience with tax software.",
                "Indsutry Experience": Extract industries the candidate has experience in. You can infer this from the companies they have worked for or explicit description in profile.",
                "Languages": "Extract languages spoken",
                "Experience": "Extract years of experience in tax roles (example: 3 years experience in property tax, 5 years experience in international tax, etc.)",
            }}
        ]
        Here is the candidate profile: {submission}
        Make sure to return valid JSON only.
        """

def validate_and_clean_json(extracted_info):
    logging.info(f"Validating and cleaning JSON: {extracted_info}")
    try:
        if extracted_info.startswith("```json"):
            extracted_info = extracted_info[7:-4].strip()
            logging.info("Removed ```json formatting from extracted info")

        extracted_info_data = json.loads(extracted_info)
        
        # Check if the extracted info is a list or a single object
        if isinstance(extracted_info_data, list):
            logging.info("Extracted info is a valid list")
            for item in extracted_info_data:
                logging.info(f"Item type: {type(item)}, Item content: {item}")
            return extracted_info_data
        elif isinstance(extracted_info_data, dict):
            logging.info("Extracted info is a valid dict")
            logging.info(f"Dict content: {extracted_info_data}")
            return [extracted_info_data]
        else:
            logging.error("Extracted info is neither a list nor a dict")
            return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON at line {e.lineno} column {e.colno}: {e.msg}")
        logging.error(f"Raw API response: {extracted_info}")
        return None

    logging.info(f"Final output of validate_and_clean_json: {extracted_info_data}")

def process_job_post(extracted_info):
    logger.info(f"Processing extracted info: {extracted_info}")

    try:
        extracted_info_dict = extracted_info

        return {
            "id": extracted_info_dict.get("id", "NA"),
            "company_name": extracted_info_dict.get("Company Name", "NA"),
            "role": extracted_info_dict.get("Role", "NA"),
            "level": extracted_info_dict.get("Level", "NA"),
            "salary": extracted_info_dict.get("Salary", "NA"),
            "salary_median": extracted_info_dict.get("Salary Median", "NA"),
            "location": extracted_info_dict.get("Location", "NA"),
            "state": extracted_info_dict.get("State", "NA"),
            "setting": extracted_info_dict.get("Setting", "NA"),
            "in_state": extracted_info_dict.get("In-State?", "NA"),
            "industry": extracted_info_dict.get("Industry", "NA"),
            "public": extracted_info_dict.get("Public", "NA"),
            "employee_count": extracted_info_dict.get("Employee Count", "NA"),
            "revenue": extracted_info_dict.get("Revenue", "NA"),
            "benefits": extracted_info_dict.get("Benefits", "NA"),
            "relocation": extracted_info_dict.get("Relocation", "NA"),
            "undergraduate": extracted_info_dict.get("Undergraduate", "NA"),
            "postgraduate": extracted_info_dict.get("Postgraduate", "NA"),
            "experience": extracted_info_dict.get("Experience", "NA"),
            "fields": extracted_info_dict.get("Field(s)", "NA"),
            "cpa": extracted_info_dict.get("CPA", "NA"),
            "certifications": extracted_info_dict.get("Certifications", "NA"),
            "strategic_responsibilities": extracted_info_dict.get("Strategic Responsibilities", "NA"),
            "operational_responsibilities": extracted_info_dict.get("Operational Responsibilities", "NA"),
            "team_management": extracted_info_dict.get("Team Management", "NA"),
            "budgetary_control": extracted_info_dict.get("Budgetary Control", "NA"),
            "decision_making_authority": extracted_info_dict.get("Decision-Making Authority", "NA"),
            "reporting_structure": extracted_info_dict.get("Reporting Structure", "NA"),
            "cross_functional_interaction": extracted_info_dict.get("Cross-Functional Interaction", "NA"),
            "company_culture": extracted_info_dict.get("Company Culture", "NA"),
            "technology_proficiency": extracted_info_dict.get("Technology Proficiency", "NA"),
            "stakeholder_engagement": extracted_info_dict.get("Stakeholder Engagement", "NA"),
            "travel_requirements": extracted_info_dict.get("Travel Requirements", "NA"),
            "succession_planning": extracted_info_dict.get("Succession Planning", "NA"),
            "crisis_management": extracted_info_dict.get("Crisis Management", "NA"),
            "leadership_style": extracted_info_dict.get("Leadership Style", "NA"),
            "change_management": extracted_info_dict.get("Change Management", "NA"),
            "risk_management": extracted_info_dict.get("Risk Management", "NA"),
            "job_posting_source": extracted_info_dict.get("Job Posting Source", "NA"),
            "date_job_posted": extracted_info_dict.get("Date Job Posted", "NA"),
            "date_job_tracked": extracted_info_dict.get("Date Job Tracked", "NA"),
            "works_with_recruiters": extracted_info_dict.get("Works With Recruiters", "NA"),
            "company_profile": extracted_info_dict.get("Company Profile", "NA"),
            "soft_skills": extracted_info_dict.get("Soft Skills", "NA"),
            "hard_skills": extracted_info_dict.get("Hard Skills", "NA"),
            "job_description_summary": extracted_info_dict.get("Job Description Summary", "NA"),
            "other_requirements": extracted_info_dict.get("Other Requirements", "NA")
        }
    except Exception as e:
        logger.error(f"Error processing extracted info: {e}")
        return {}

def process_candidate_profile(submission_text):
    logging.info(f"Processing candidate profile: {submission_text[:100]}...")

    try:
        logging.info("Calling extract_data_from_submission")
        extracted_info_list = extract_data_from_submission(submission_text, process_candidate_profile)
        logging.info(f"extract_data_from_submission returned: {extracted_info_list}")

        if not extracted_info_list:
            logging.error("No data extracted")
            return None

        candidate_data = []
        for extracted_info_dict in extracted_info_list:
            logging.info(f"Processing item: {extracted_info_dict}, Type: {type(extracted_info_dict)}")
            if isinstance(extracted_info_dict, dict):
                candidate = {
                    "id": extracted_info_dict.get("id", "NA"),
                    "first_name": extracted_info_dict.get("First Name", "NA"),
                    "last_name": extracted_info_dict.get("Last Name", "NA"),
                    "current_title": extracted_info_dict.get("Current Title", "NA"),
                    "current_level": extracted_info_dict.get("Current Level", "NA"),
                    "current_company": extracted_info_dict.get("Current Company", "NA"),
                    "location": extracted_info_dict.get("Location", "NA"),
                    "current_job": extracted_info_dict.get("Current Job", "NA"),
                    "time_at_current_job": extracted_info_dict.get("Time at Current Job", "NA"),
                    "previous_positions": extracted_info_dict.get("Previous Positions", "NA"),
                    "current_operational_responsibilities": extracted_info_dict.get("Current Operational Responsibilities", "NA"),
                    "current_strategic_responsibilities": extracted_info_dict.get("Current Strategic Responsibilities", "NA"),
                    "operational_responsibilities": extracted_info_dict.get("Operational Responsibilities", "NA"),
                    "strategic_responsibilities": extracted_info_dict.get("Strategic Responsibilities", "NA"),
                    "undergraduate": extracted_info_dict.get("Undergraduate", "NA"),
                    "postgraduate": extracted_info_dict.get("Postgraduate", "NA"),
                    "skills": extracted_info_dict.get("Skills", "NA"),
                    "key_skills_tax_finance": extracted_info_dict.get("Key Skills Related to Tax/Finance", "NA"),
                    "projects": extracted_info_dict.get("Projects", "NA"),
                    "achievements": extracted_info_dict.get("Achievements", "NA"),
                    "awards_honors": extracted_info_dict.get("Awards and Honors", "NA"),
                    "group_memberships": extracted_info_dict.get("Group Memberships", "NA"),
                    "causes": extracted_info_dict.get("Causes", "NA"),
                    "newsletters": extracted_info_dict.get("Newsletters", "NA"),
                    "interests": extracted_info_dict.get("Interests", "NA"),
                    "tax_specialization": extracted_info_dict.get("Tax Specialization", "NA"),
                    "links_to_blog_posts": extracted_info_dict.get("Links to Blog Posts", "NA"),
                    "articles": extracted_info_dict.get("Articles", "NA"),
                    "cpa": extracted_info_dict.get("CPA", "NA"),
                    "certifications": extracted_info_dict.get("Certifications", "NA"),
                    "professional_associations": extracted_info_dict.get("Professional Associations", "NA"),
                    "tax_software_experience": extracted_info_dict.get("Tax Software Experience", "NA"),
                    "industry_experience": extracted_info_dict.get("Industry Experience", "NA"),
                    "languages": extracted_info_dict.get("Languages", "NA"),
                    "experience": extracted_info_dict.get("Experience", "NA")
                }
                candidate_data.append(candidate)
            else:
                logging.error(f"Expected dictionary but got {type(extracted_info_dict)}")

        logging.info(f"Processed candidate data: {candidate_data}")
        return candidate_data
    except Exception as e:
        logging.error(f"Error processing candidate profile: {e}")
        return None

@main.route('/')
def index():
    logger.info("Rendering index page")
    return render_template('index.html')

@main.route('/schema', methods=['GET'])
def schema():
    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(job_posts)")
    job_posts_schema = cursor.fetchall()
    cursor.execute("PRAGMA table_info(candidate_profiles)")
    candidate_profiles_schema = cursor.fetchall()

    conn.close()

    return jsonify({
        "job_posts_schema": job_posts_schema,
        "candidate_profiles_schema": candidate_profiles_schema
    })

@main.route('/debug_data', methods=['POST'])
def debug_data():
    data = request.json
    logger.info(f"Received data for debugging: {data}")
    return jsonify({"status": "success"})

@main.route('/submit', methods=['POST'])
def submit():
    logger.info("Submit data endpoint hit")
    
    try:
        data = request.get_json()
        logger.info("Received data: %s", data)

        submission_type = data.get('type')
        submission_text = data.get('text')

        if submission_type == 'job':
            submission_type = 'jobPost'
        elif submission_type == 'candidate':
            submission_type = 'candidateProfile'

        if not submission_text:
            logger.error("No text provided")
            return jsonify({"error": "No text provided"}), 400

        extracted_info = None

        try:
            if submission_type == 'jobPost':
                extracted_info = extract_info('jobPost', submission_text)
                if extracted_info:
                    save_job_posts_to_db(extracted_info)
            elif submission_type == 'oldJob':
                extracted_info = extract_info('oldJob', submission_text)
                if extracted_info:
                    save_job_posts_to_db(extracted_info)
            elif submission_type == 'candidateProfile':
                extracted_info = extract_info('candidateProfile', submission_text)
                print(f"Type of extracted_info: {type(extracted_info)}")  # Add this line
                if isinstance(extracted_info, list):
                    print("extracted_info is a list.")
                elif isinstance(extracted_info, dict):
                    print("extracted_info is a dictionary.")
                else:
                    print("extracted_info is neither a list nor a dictionary.")
                if extracted_info:
                    save_candidate_profiles_to_db(extracted_info)
            else:
                logger.error("Invalid submission type: %s", submission_type)
                return jsonify({"error": "Invalid submission type"}), 400

            logger.info("Submission processed successfully")
            return jsonify({"status": "success", "data": extracted_info}), 200
        except Exception as e:
            logger.exception("Exception during extraction and saving")
            return jsonify({"error": "An error occurred during submission processing"}), 500
    except Exception as e:
        logger.exception("Exception during request handling")
        return jsonify({"error": "Internal server error"}), 500

@main.route('/job_posts', methods=['GET'])
def job_posts():
    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM job_posts")
    job_posts = cursor.fetchall()

    conn.close()

    return jsonify(job_posts)

@main.route('/candidate_profiles', methods=['GET'])
def candidate_profiles():
    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidate_profiles")
    candidate_profiles = cursor.fetchall()

    conn.close()

    return jsonify(candidate_profiles)

@main.route('/dashboard/job_posts')
def job_posts_dashboard():
    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM job_posts")
    job_posts = cursor.fetchall()

    conn.close()

    return render_template('job_posts.html', jobs=job_posts)

@main.route('/dashboard/candidate_profiles')
def candidate_profiles_dashboard():
    logger.info("Fetching candidate profiles from database.")
    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidate_profiles")
    candidate_profiles = cursor.fetchall()
    logger.info(f"Fetched candidate profiles: {candidate_profiles}")

    conn.close()

    return render_template('candidate_profiles.html', candidates=candidate_profiles)

@main.route('/filtered_job_posts', methods=['POST'])
def filtered_job_posts():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    category = data.get('category')

    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    query = "SELECT * FROM job_posts WHERE date_job_tracked BETWEEN ? AND ?"
    params = [start_date, end_date]

    if category == "old":
        query += " AND id LIKE 'OLD%'"
    elif category == "new":
        query += " AND id NOT LIKE 'OLD%'"

    cursor.execute(query, params)
    filtered_posts = cursor.fetchall()

    conn.close()

    return jsonify(filtered_posts)

def save_job_posts_to_db(job_posts):
    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    for job in job_posts:
        cursor.execute("""
            INSERT INTO job_posts (
                id, company_name, role, level, salary, salary_median, location, state, setting, in_state, industry, public, 
                employee_count, revenue, benefits, relocation, undergraduate, postgraduate, experience, fields, cpa, 
                certifications, strategic_responsibilities, operational_responsibilities, team_management, budgetary_control, 
                decision_making_authority, reporting_structure, cross_functional_interaction, company_culture, technology_proficiency, 
                stakeholder_engagement, travel_requirements, succession_planning, crisis_management, leadership_style, change_management, 
                risk_management, job_posting_source, date_job_posted, date_job_tracked, works_with_recruiters, company_profile, 
                soft_skills, hard_skills, job_description_summary, other_requirements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job['id'], job['company_name'], job['role'], job['level'], job['salary'], job['salary_median'], job['location'], job['state'], 
            job['setting'], job['in_state'], job['industry'], job['public'], job['employee_count'], job['revenue'], job['benefits'], 
            job['relocation'], job['undergraduate'], job['postgraduate'], job['experience'], job['fields'], job['cpa'], job['certifications'], 
            job['strategic_responsibilities'], job['operational_responsibilities'], job['team_management'], job['budgetary_control'], 
            job['decision_making_authority'], job['reporting_structure'], job['cross_functional_interaction'], job['company_culture'], 
            job['technology_proficiency'], job['stakeholder_engagement'], job['travel_requirements'], job['succession_planning'], 
            job['crisis_management'], job['leadership_style'], job['change_management'], job['risk_management'], job['job_posting_source'], 
            job['date_job_posted'], job['date_job_tracked'], job['works_with_recruiters'], job['company_profile'],
            job['soft_skills'], job['hard_skills'], job['job_description_summary'], job['other_requirements']
        ))

    conn.commit()
    conn.close()

def save_candidate_profiles_to_db(candidate_profiles):
    print(f"Type of candidate_profiles in save_candidate_profiles_to_db: {type(candidate_profiles)}")
    if isinstance(candidate_profiles, list):
        print("candidate_profiles is a list in save_candidate_profiles_to_db.")
    elif isinstance(candidate_profiles, dict):
        print("candidate_profiles is a dictionary in save_candidate_profiles_to_db.")
    else:
        print("candidate_profiles is neither a list nor a dictionary in save_candidate_profiles_to_db.")

    conn = None
    cursor = None

    try:
        conn = sqlite3.connect('job_candidate_manager.db', timeout=10)
        cursor = conn.cursor()

        for candidate_dict in candidate_profiles:
            logging.info(f"Saving candidate to DB: {candidate_dict}")
            if isinstance(candidate_dict, dict):
                candidate_id = candidate_dict.get('id', 'NA')
                
                cursor.execute("""
                    INSERT INTO candidate_profiles (
                        id, first_name, last_name, current_title, current_level, current_company, location, current_job, time_at_current_job, 
                        previous_positions, current_operational_responsibilities, current_strategic_responsibilities, operational_responsibilities, 
                        strategic_responsibilities, undergraduate, postgraduate, skills, key_skills_tax_finance, projects, achievements, awards_honors, 
                        group_memberships, causes, newsletters, interests, tax_specialization, links_to_blog_posts, articles, cpa, certifications, 
                        professional_associations, tax_software_experience, industry_experience, languages, experience
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    json.dumps(candidate_id), 
                    json.dumps(candidate_dict.get('first_name', 'NA')), 
                    json.dumps(candidate_dict.get('last_name', 'NA')), 
                    json.dumps(candidate_dict.get('current_title', 'NA')),
                    json.dumps(candidate_dict.get('current_level', 'NA')), 
                    json.dumps(candidate_dict.get('current_company', 'NA')), 
                    json.dumps(candidate_dict.get('location', 'NA')),
                    json.dumps(candidate_dict.get('current_job', 'NA')), 
                    json.dumps(candidate_dict.get('time_at_current_job', 'NA')), 
                    json.dumps(candidate_dict.get('previous_positions', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('current_operational_responsibilities', 'NA')), 
                    json.dumps(candidate_dict.get('current_strategic_responsibilities', 'NA')),
                    json.dumps(candidate_dict.get('operational_responsibilities', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('strategic_responsibilities', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('undergraduate', 'NA')),  # Convert dict to string
                    json.dumps(candidate_dict.get('postgraduate', 'NA')),  # Convert dict to string
                    json.dumps(candidate_dict.get('skills', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('key_skills_tax_finance', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('projects', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('achievements', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('awards_honors', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('group_memberships', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('causes', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('newsletters', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('interests', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('tax_specialization', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('links_to_blog_posts', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('articles', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('cpa', 'NA')), 
                    json.dumps(candidate_dict.get('certifications', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('professional_associations', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('tax_software_experience', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('industry_experience', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('languages', 'NA')),  # Convert list to string
                    json.dumps(candidate_dict.get('experience', 'NA'))
                ))
            else:
                logging.error(f"Expected dictionary but got {type(candidate_dict)}")
        conn.commit()
        logging.info("Candidate profiles saved successfully")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


