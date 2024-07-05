import sqlite3

def init_db():
    conn = sqlite3.connect('job_candidate_manager.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_posts (
            id TEXT PRIMARY KEY,
            company_name TEXT,
            role TEXT,
            level TEXT,
            salary TEXT,
            salary_median TEXT,
            location TEXT,
            state TEXT,
            setting TEXT,
            in_state TEXT,
            industry TEXT,
            public TEXT,
            employee_count TEXT,
            revenue TEXT,
            benefits TEXT,
            relocation TEXT,
            undergraduate TEXT,
            postgraduate TEXT,
            experience TEXT,
            fields TEXT,
            cpa TEXT,
            certifications TEXT,
            strategic_responsibilities TEXT,
            operational_responsibilities TEXT,
            team_management TEXT,
            budgetary_control TEXT,
            decision_making_authority TEXT,
            reporting_structure TEXT,
            cross_functional_interaction TEXT,
            company_culture TEXT,
            technology_proficiency TEXT,
            stakeholder_engagement TEXT,
            travel_requirements TEXT,
            succession_planning TEXT,
            crisis_management TEXT,
            leadership_style TEXT,
            change_management TEXT,
            risk_management TEXT,
            job_posting_source TEXT,
            date_job_posted TEXT,
            date_job_tracked TEXT,
            works_with_recruiters TEXT,
            company_profile TEXT,
            cross_functional_teams TEXT,
            soft_skills TEXT,
            hard_skills TEXT,
            job_description_summary TEXT,
            other_requirements TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_profiles (
            id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            current_title TEXT,
            current_level TEXT,
            current_company TEXT,
            location TEXT,
            current_job TEXT,
            time_at_current_job TEXT,
            previous_positions TEXT,
            current_operational_responsibilities TEXT,
            current_strategic_responsibilities TEXT,
            operational_responsibilities TEXT,
            strategic_responsibilities TEXT,
            undergraduate TEXT,
            postgraduate TEXT,
            skills TEXT,
            key_skills_tax_finance TEXT,
            projects TEXT,
            achievements TEXT,
            awards_honors TEXT,
            group_memberships TEXT,
            causes TEXT,
            newsletters TEXT,
            interests TEXT,
            tax_specialization TEXT,
            links_to_blog_posts TEXT,
            articles TEXT,
            cpa TEXT,
            certifications TEXT,
            professional_associations TEXT,
            tax_software_experience TEXT,
            industry_experience TEXT,
            languages TEXT,
            experience TEXT
        )
    """)

    conn.commit()
    conn.close()
