"""
Mock Data Generator for TalentRadar
Generates 200+ realistic Indian candidate profiles for demo/testing.
Called when real scrapers fail or for initial seeding.
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Optional

# --- Indian Name Data ---

FIRST_NAMES_MALE = [
    "Aarav", "Arjun", "Rohit", "Rahul", "Vikram", "Suresh", "Rajesh", "Amit",
    "Ankur", "Deepak", "Manish", "Sanjay", "Nikhil", "Kiran", "Aditya",
    "Prateek", "Vikas", "Sumit", "Gaurav", "Naveen", "Akash", "Ravi", "Harsh",
    "Pankaj", "Dinesh", "Manoj", "Alok", "Vivek", "Santosh", "Ajay", "Varun",
    "Shubham", "Mohit", "Tushar", "Rishabh", "Kunal", "Yash", "Abhinav",
    "Pranav", "Siddharth", "Kartik", "Neeraj", "Ashish", "Dev", "Ankit",
    "Tarun", "Abhishek", "Manas", "Sachin", "Lokesh", "Balaji", "Suraj",
    "Harish", "Ramesh", "Chetan", "Vinay", "Girish", "Mahesh", "Sunil",
    "Anand", "Vinod", "Rakesh", "Rajiv", "Sanjeev", "Kamal", "Satish",
    "Naresh", "Hemant", "Umesh", "Arvind", "Saurabh", "Jitendra", "Lalit",
    "Rajan", "Ajit", "Mohan", "Nandan", "Prakash", "Tanmay", "Dhruv",
]

FIRST_NAMES_FEMALE = [
    "Priya", "Anjali", "Sneha", "Pooja", "Neha", "Kavya", "Ananya", "Divya",
    "Ishita", "Riya", "Simran", "Pallavi", "Shruti", "Swati", "Meena",
    "Rekha", "Sunita", "Lakshmi", "Sarita", "Geeta", "Nisha", "Vandana",
    "Rashmi", "Seema", "Asha", "Deepa", "Usha", "Savita", "Preeti",
    "Sonal", "Komal", "Manisha", "Shweta", "Garima", "Sakshi", "Ritu",
    "Megha", "Roshni", "Kalpana", "Anita", "Sudha", "Vidya", "Mona",
    "Lata", "Manju", "Hema", "Archana", "Madhuri", "Bhavna", "Chitra",
    "Tanvi", "Kritika", "Aditi", "Nandita", "Surbhi", "Ankita", "Nidhi",
    "Monika", "Sapna", "Sunaina", "Richa", "Neelam", "Kavita", "Poonam",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Mishra", "Pandey", "Tiwari",
    "Joshi", "Patel", "Shah", "Mehta", "Desai", "Nair", "Menon", "Pillai",
    "Reddy", "Rao", "Naidu", "Iyer", "Iyengar", "Krishnamurthy", "Subramaniam",
    "Chatterjee", "Banerjee", "Mukherjee", "Das", "Bose", "Sen", "Roy",
    "Ghosh", "Bhat", "Shetty", "Kamath", "Hegde", "Pai", "Gowda", "Naik",
    "Kulkarni", "Jain", "Agarwal", "Mittal", "Garg", "Bajaj", "Khanna",
    "Malhotra", "Kapoor", "Chopra", "Taneja", "Bhatia", "Arora", "Anand",
    "Saxena", "Srivastava", "Dwivedi", "Tripathi", "Upadhyay", "Chaudhary",
    "Yadav", "Dubey", "Shukla", "Chauhan", "Rawat", "Bisht", "Negi",
    "Raghunathan", "Venkataraman", "Gopalakrishnan", "Ramachandran",
]

CITIES = [
    "Bangalore", "Mumbai", "Delhi", "Pune", "Hyderabad", "Chennai",
    "Kolkata", "Noida", "Gurgaon", "Ahmedabad", "Jaipur", "Kochi",
    "Bengaluru", "New Delhi", "NCR", "Chandigarh", "Coimbatore",
    "Indore", "Nagpur", "Bhubaneswar", "Mysore", "Surat",
]

COMPANIES = {
    "tier1_it": [
        "TCS", "Infosys", "Wipro", "HCL Technologies", "Tech Mahindra",
        "Cognizant", "Capgemini", "Accenture", "IBM India", "Oracle India",
    ],
    "product": [
        "Razorpay", "Swiggy", "Zomato", "Flipkart", "Paytm", "CRED",
        "Groww", "Meesho", "Urban Company", "Nykaa", "PhonePe", "Ola",
        "OYO", "BYJU'S", "Unacademy", "Zepto", "Blinkit", "upGrad",
        "Freshworks", "Zoho", "Mphasis", "LTIMindtree", "Persistent Systems",
        "Hexaware", "Coforge", "Browserstack", "Postman", "Chargebee",
        "Druva", "InMobi", "MakeMyTrip", "PolicyBazaar", "Lenskart",
        "Dream11", "ShareChat", "Glance", "Vedantu", "WhiteHat Jr",
    ],
    "mnc": [
        "Google India", "Microsoft India", "Amazon India", "Adobe India",
        "Salesforce India", "SAP India", "Cisco India", "Dell India",
        "HP India", "Intel India", "Qualcomm India", "Samsung R&D India",
        "Goldman Sachs India", "Morgan Stanley India", "JP Morgan India",
        "Deutsche Bank India", "Barclays India",
    ],
    "mid_size": [
        "Zensar", "Mphasis", "Sonata Software", "KPIT Technologies",
        "Cyient", "Mastech Digital", "Nagarro", "Birlasoft",
        "L&T Technology Services", "Tata Elxsi", "Sasken Technologies",
    ],
    "startup": [
        "Slice", "Open Financial", "Fi Money", "Jupiter Money",
        "Jar App", "Stashfin", "KreditBee", "MoneyTap", "Navi",
        "Dunzo", "Rapido", "Porter", "Zypp Electric", "Bounce",
        "Doubtnut", "Classplus", "PW (Physics Wallah)", "Apna Jobs",
    ],
}

ALL_COMPANIES = [c for companies in COMPANIES.values() for c in companies]

# --- Skill Profiles ---

SKILL_PROFILES = {
    "fullstack": {
        "skills": ["React", "Node.js", "TypeScript", "JavaScript", "MongoDB", "PostgreSQL",
                   "Docker", "AWS", "REST API", "Git", "Agile", "Redux", "Express.js",
                   "HTML5", "CSS3", "Tailwind CSS", "Jest", "Webpack"],
        "roles": ["Full Stack Developer", "Software Engineer", "MEAN Stack Developer",
                  "MERN Stack Developer", "Frontend Developer", "Backend Developer"],
    },
    "backend_java": {
        "skills": ["Java", "Spring Boot", "Microservices", "REST API", "MySQL",
                   "PostgreSQL", "Redis", "Kafka", "Docker", "Kubernetes", "AWS",
                   "JUnit", "Maven", "Hibernate", "JPA", "Git", "CI/CD"],
        "roles": ["Java Developer", "Backend Engineer", "Software Engineer",
                  "Senior Java Developer", "Java Tech Lead"],
    },
    "backend_python": {
        "skills": ["Python", "FastAPI", "Django", "Flask", "PostgreSQL", "MySQL",
                   "Redis", "Celery", "Docker", "AWS", "REST API", "SQLAlchemy",
                   "Pytest", "Pandas", "NumPy", "Git", "Linux"],
        "roles": ["Python Developer", "Backend Engineer", "Django Developer",
                  "Software Engineer", "API Developer"],
    },
    "data_science": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
                   "Scikit-learn", "Pandas", "NumPy", "SQL", "Matplotlib", "Seaborn",
                   "Jupyter", "Git", "Docker", "AWS SageMaker", "NLP", "Computer Vision",
                   "Statistical Analysis", "A/B Testing"],
        "roles": ["Data Scientist", "ML Engineer", "AI Engineer",
                  "Data Analyst", "Research Scientist", "NLP Engineer"],
    },
    "devops": {
        "skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
                   "Ansible", "Jenkins", "CI/CD", "Linux", "Bash", "Python",
                   "Prometheus", "Grafana", "ELK Stack", "Helm", "ArgoCD",
                   "GitHub Actions", "Security", "Networking"],
        "roles": ["DevOps Engineer", "SRE", "Cloud Engineer", "Platform Engineer",
                  "Infrastructure Engineer", "Cloud Architect"],
    },
    "mobile": {
        "skills": ["React Native", "Flutter", "iOS", "Android", "Swift",
                   "Kotlin", "Dart", "Firebase", "REST API", "Redux",
                   "Git", "App Store Optimization", "Fastlane", "Xcode"],
        "roles": ["Mobile Developer", "iOS Developer", "Android Developer",
                  "React Native Developer", "Flutter Developer"],
    },
    "product": {
        "skills": ["Product Management", "Agile", "Scrum", "Roadmapping", "SQL",
                   "JIRA", "Confluence", "Figma", "User Research", "Analytics",
                   "Stakeholder Management", "A/B Testing", "Google Analytics",
                   "Excel", "Tableau", "User Stories", "OKRs"],
        "roles": ["Product Manager", "Senior Product Manager", "Associate PM",
                  "Director of Product", "Head of Product"],
    },
    "design": {
        "skills": ["Figma", "Adobe XD", "Sketch", "UI/UX Design", "Prototyping",
                   "User Research", "Wireframing", "Adobe Photoshop", "Illustrator",
                   "Design Systems", "Accessibility", "HTML", "CSS", "Framer"],
        "roles": ["UI/UX Designer", "Product Designer", "Visual Designer",
                  "Interaction Designer", "UX Researcher"],
    },
    "data_analyst": {
        "skills": ["SQL", "Python", "Excel", "Power BI", "Tableau", "Google Analytics",
                   "Data Visualization", "Statistical Analysis", "Pandas",
                   "Business Intelligence", "ETL", "Dashboard", "JIRA"],
        "roles": ["Data Analyst", "Business Analyst", "BI Developer",
                  "Analytics Engineer", "Reporting Analyst"],
    },
    "dotnet": {
        "skills": ["C#", ".NET", "ASP.NET Core", "SQL Server", "Entity Framework",
                   "Azure", "Microservices", "REST API", "WCF", "SignalR",
                   "Git", "Docker", "Unit Testing", "LINQ", "Visual Studio"],
        "roles": [".NET Developer", "C# Developer", "Full Stack .NET Developer",
                  "Senior .NET Developer"],
    },
    "qa": {
        "skills": ["Manual Testing", "Selenium", "Cypress", "Jest", "JUnit",
                   "JIRA", "Postman", "API Testing", "SQL", "Agile",
                   "Test Planning", "Bug Tracking", "Performance Testing",
                   "Mobile Testing", "Automation Testing"],
        "roles": ["QA Engineer", "Test Engineer", "SDET", "QA Lead",
                  "Automation Engineer", "Quality Analyst"],
    },
    "sales": {
        "skills": ["B2B Sales", "CRM", "Salesforce", "Lead Generation",
                   "Account Management", "Negotiation", "SaaS Sales",
                   "Cold Calling", "Pipeline Management", "Excel",
                   "Communication", "Presentation Skills"],
        "roles": ["Sales Executive", "Account Manager", "Business Development Manager",
                  "Sales Manager", "Enterprise Sales", "Inside Sales"],
    },
}

EDUCATION_UNIVERSITIES = [
    {"name": "IIT Bombay", "tier": "tier1"},
    {"name": "IIT Delhi", "tier": "tier1"},
    {"name": "IIT Madras", "tier": "tier1"},
    {"name": "IIT Bangalore (IIMB)", "tier": "tier1"},
    {"name": "BITS Pilani", "tier": "tier1"},
    {"name": "NIT Trichy", "tier": "tier2"},
    {"name": "NIT Warangal", "tier": "tier2"},
    {"name": "NIT Surathkal", "tier": "tier2"},
    {"name": "VIT Vellore", "tier": "tier2"},
    {"name": "SRM University", "tier": "tier2"},
    {"name": "Manipal Institute of Technology", "tier": "tier2"},
    {"name": "Pune University", "tier": "tier3"},
    {"name": "Bangalore University", "tier": "tier3"},
    {"name": "Anna University", "tier": "tier3"},
    {"name": "Mumbai University", "tier": "tier3"},
    {"name": "Delhi University", "tier": "tier3"},
    {"name": "Osmania University", "tier": "tier3"},
    {"name": "Amity University", "tier": "tier3"},
]

DEGREES = ["B.Tech", "BE", "MCA", "M.Tech", "BSc Computer Science", "BCA", "MBA"]
NOTICE_PERIODS = [0, 15, 30, 60, 90]
SOURCES = ["naukri", "linkedin", "github", "instahyre", "cutshort", "iimjobs", "angellist"]


def _random_name(gender: Optional[str] = None) -> tuple[str, str]:
    if gender is None:
        gender = random.choice(["male", "female"])
    if gender == "female":
        first = random.choice(FIRST_NAMES_FEMALE)
    else:
        first = random.choice(FIRST_NAMES_MALE)
    last = random.choice(LAST_NAMES)
    return first, last


def _generate_email(first: str, last: str, idx: int) -> str:
    domains = ["gmail.com", "yahoo.co.in", "hotmail.com", "outlook.com"]
    patterns = [
        f"{first.lower()}.{last.lower()}@{random.choice(domains)}",
        f"{first.lower()}{last.lower()}{random.randint(1, 99)}@{random.choice(domains)}",
        f"{first.lower()[0]}{last.lower()}@{random.choice(domains)}",
    ]
    return random.choice(patterns).replace(" ", "")


def _generate_phone() -> str:
    prefixes = ["98", "97", "96", "95", "94", "93", "89", "88", "87", "86", "76", "70"]
    return f"+91 {random.choice(prefixes)}{random.randint(10000000, 99999999)}"


def _salary_by_experience(exp_years: float) -> tuple[float, float]:
    """Return (current_salary, expected_salary) in LPA based on experience."""
    if exp_years < 1:
        current = round(random.uniform(3.0, 5.0), 1)
    elif exp_years < 3:
        current = round(random.uniform(5.0, 9.0), 1)
    elif exp_years < 5:
        current = round(random.uniform(8.0, 14.0), 1)
    elif exp_years < 8:
        current = round(random.uniform(12.0, 22.0), 1)
    elif exp_years < 12:
        current = round(random.uniform(18.0, 35.0), 1)
    else:
        current = round(random.uniform(28.0, 60.0), 1)
    expected = round(current * random.uniform(1.15, 1.35), 1)
    return current, expected


def _generate_work_history(current_role: str, current_company: str, exp_years: float) -> list:
    """Generate realistic work history."""
    history = [{
        "role": current_role,
        "company": current_company,
        "duration": f"{random.randint(1, min(int(exp_years), 4))} years",
        "current": True,
    }]

    remaining_exp = exp_years - random.uniform(1, 3)
    prev_companies = random.sample(ALL_COMPANIES, min(3, len(ALL_COMPANIES)))
    prev_companies = [c for c in prev_companies if c != current_company]

    for i, company in enumerate(prev_companies[:2]):
        if remaining_exp <= 0:
            break
        duration = random.uniform(1, min(3, remaining_exp))
        history.append({
            "role": f"Software Developer" if i == 0 else "Junior Developer",
            "company": company,
            "duration": f"{duration:.0f} years",
            "current": False,
        })
        remaining_exp -= duration

    return history


def _generate_education(exp_years: float) -> list:
    uni = random.choice(EDUCATION_UNIVERSITIES)
    degree = random.choice(DEGREES)
    grad_year = datetime.now().year - int(exp_years) - random.randint(0, 1)
    edu = [{
        "degree": degree,
        "institution": uni["name"],
        "year": str(grad_year),
        "tier": uni["tier"],
    }]
    return edu


def generate_candidate(idx: int, profile_type: Optional[str] = None, seed_skills: Optional[list] = None) -> dict:
    """Generate a single realistic Indian candidate profile."""
    if profile_type is None:
        profile_types = list(SKILL_PROFILES.keys())
        weights = [15, 12, 12, 10, 8, 6, 8, 6, 8, 5, 5, 5]
        profile_type = random.choices(profile_types, weights=weights[:len(profile_types)], k=1)[0]

    profile = SKILL_PROFILES[profile_type]
    gender = random.choice(["male", "female", "male", "male"])  # ~75% male (realistic for India IT)
    first_name, last_name = _random_name(gender)
    full_name = f"{first_name} {last_name}"

    exp_years = round(random.choices(
        [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15],
        weights=[3, 8, 12, 15, 15, 12, 10, 8, 7, 5, 3, 2],
        k=1
    )[0], 1)

    current_role = random.choice(profile["roles"])
    if exp_years >= 8:
        seniority_prefix = random.choice(["Senior ", "Principal ", "Lead "])
        current_role = seniority_prefix + current_role
    elif exp_years >= 5:
        current_role = random.choice(["Senior ", "Sr. "]) + current_role if random.random() > 0.5 else current_role

    current_company = random.choice(ALL_COMPANIES)
    city = random.choice(CITIES)
    email = _generate_email(first_name, last_name, idx)
    phone = _generate_phone()
    salary_current, salary_expected = _salary_by_experience(exp_years)
    notice_period = random.choice(NOTICE_PERIODS)

    # Skills: take profile skills + optional seed skills
    num_skills = random.randint(5, 12)
    skills = random.sample(profile["skills"], min(num_skills, len(profile["skills"])))
    if seed_skills:
        for s in seed_skills[:3]:
            if s not in skills:
                skills.insert(0, s)
    skills = list(dict.fromkeys(skills))[:12]  # deduplicate

    # Sources
    num_sources = random.randint(1, 3)
    sources = random.sample(SOURCES, num_sources)

    # Last active
    days_ago = random.choices(
        [1, 3, 7, 14, 30, 60, 90, 180],
        weights=[15, 20, 20, 15, 10, 8, 7, 5],
        k=1
    )[0]
    last_active = datetime.utcnow() - timedelta(days=days_ago)
    freshness_score = max(0.1, 1.0 - (days_ago / 365))

    # GitHub + LinkedIn URLs (fake but realistic)
    username_base = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 99)}"
    github_url = f"https://github.com/{username_base}" if "github" in sources or profile_type in ["fullstack", "backend_python", "backend_java", "devops", "data_science"] else None
    linkedin_url = f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(100, 999)}" if "linkedin" in sources else None
    naukri_url = f"https://www.naukri.com/mnjuser/profile/{username_base}" if "naukri" in sources else None

    # Summary
    summary = (
        f"{current_role} with {exp_years} years of experience in {', '.join(skills[:3])}. "
        f"Currently working at {current_company} in {city}. "
        f"Open to {'remote and ' if random.random() > 0.5 else ''}{'on-site'} opportunities."
    )

    work_history = _generate_work_history(current_role, current_company, exp_years)
    education = _generate_education(exp_years)

    return {
        "name": full_name,
        "email": email,
        "phone": phone,
        "current_role": current_role,
        "current_company": current_company,
        "experience_years": exp_years,
        "skills": skills,
        "location": city,
        "linkedin_url": linkedin_url,
        "github_url": github_url,
        "naukri_url": naukri_url,
        "sources": sources,
        "salary_current": salary_current,
        "salary_expected": salary_expected,
        "notice_period": notice_period,
        "summary": summary,
        "last_active": last_active,
        "freshness_score": freshness_score,
        "work_history": work_history,
        "education": education,
        "profile_type": profile_type,
    }


def generate_all_candidates(count: int = 220) -> list:
    """Generate a diverse set of Indian candidates."""
    candidates = []

    # Ensure good distribution of profile types
    distribution = {
        "fullstack": int(count * 0.18),
        "backend_java": int(count * 0.12),
        "backend_python": int(count * 0.12),
        "data_science": int(count * 0.12),
        "devops": int(count * 0.08),
        "mobile": int(count * 0.07),
        "product": int(count * 0.08),
        "design": int(count * 0.05),
        "data_analyst": int(count * 0.07),
        "dotnet": int(count * 0.05),
        "qa": int(count * 0.04),
        "sales": int(count * 0.02),
    }

    idx = 0
    for profile_type, num in distribution.items():
        for _ in range(num):
            candidates.append(generate_candidate(idx, profile_type=profile_type))
            idx += 1

    # Fill remaining with random
    while len(candidates) < count:
        candidates.append(generate_candidate(idx))
        idx += 1

    # Shuffle for realism
    random.shuffle(candidates)
    return candidates


class MockDataScraper(BaseScraper):
    SOURCE_NAME = "mock"

    async def scrape(self, keywords: str, location: str = "India", limit: int = 50) -> list:
        """Generate mock candidates matching the search query."""
        # Parse keywords to determine profile type
        kw_lower = keywords.lower()
        profile_type = None

        keyword_profile_map = {
            "react": "fullstack",
            "node": "fullstack",
            "javascript": "fullstack",
            "java": "backend_java",
            "spring": "backend_java",
            "python": "backend_python",
            "django": "backend_python",
            "fastapi": "backend_python",
            "machine learning": "data_science",
            "ml": "data_science",
            "data science": "data_science",
            "ai": "data_science",
            "nlp": "data_science",
            "devops": "devops",
            "kubernetes": "devops",
            "aws": "devops",
            "terraform": "devops",
            "flutter": "mobile",
            "react native": "mobile",
            "android": "mobile",
            "ios": "mobile",
            "product manager": "product",
            "product management": "product",
            "ui/ux": "design",
            "figma": "design",
            "data analyst": "data_analyst",
            "power bi": "data_analyst",
            "tableau": "data_analyst",
            ".net": "dotnet",
            "c#": "dotnet",
            "selenium": "qa",
            "testing": "qa",
            "sales": "sales",
        }

        for keyword, ptype in keyword_profile_map.items():
            if keyword in kw_lower:
                profile_type = ptype
                break

        seed_skills = [k.strip() for k in keywords.split(",")][:5]
        candidates = []
        for i in range(min(limit, 100)):
            cand = generate_candidate(i, profile_type=profile_type, seed_skills=seed_skills)
            # Filter by location if specified
            if location and location.lower() != "india":
                cand["location"] = location
            candidates.append(cand)

        return candidates
