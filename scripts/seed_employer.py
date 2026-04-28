"""
Creates employer account hirex@gmail.com with full profile + 15 tech job posts.
Run during build or: python scripts/seed_employer.py
"""
import os
import sys
import django
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
django.setup()

from accounts.models import User, Employer
from jobs.models import Job

# ── 1. Create Employer User ───────────────────────────────────────────────────
EMAIL = 'hirex@gmail.com'
PASSWORD = 'hirex2002'

user, created = User.objects.get_or_create(
    email=EMAIL,
    defaults={
        'name': 'HireX Recruiter',
        'role': 'employer',
        'bio': 'Talent acquisition specialist at HireX Technologies. Passionate about connecting top tech talent with innovative companies. 8+ years of experience in technical recruiting across SaaS, FinTech, and AI domains.',
        'location': 'San Francisco, CA',
        'phone': '+1-415-555-0192',
        'linkedin': 'https://linkedin.com/in/hirex-recruiter',
        'github': 'https://github.com/hirex-tech',
        'skills': ['Technical Recruiting', 'Talent Acquisition', 'HR Management', 'Python', 'JavaScript', 'React'],
        'is_approved': True,
        'approval_status': 'approved',
        'is_active': True,
    }
)
if created:
    user.set_password(PASSWORD)
    user.save()
    print(f'✅ User created: {EMAIL}')
else:
    print(f'ℹ️  User already exists: {EMAIL}')

# ── 2. Create / Update Employer Profile ──────────────────────────────────────
employer, emp_created = Employer.objects.get_or_create(
    user=user,
    defaults={
        'company_name': 'HireX Technologies',
        'company_logo': 'https://ui-avatars.com/api/?name=HireX+Technologies&background=6366f1&color=fff&size=200',
        'industry': 'Information Technology',
        'company_size': '201-500 employees',
        'website': 'https://hirex.tech',
        'description': (
            'HireX Technologies is a cutting-edge software company specializing in AI-driven recruitment platforms, '
            'cloud infrastructure, and enterprise SaaS solutions. Founded in 2015, we have grown to serve over 500 '
            'enterprise clients globally. Our engineering teams work on challenging problems at scale — from real-time '
            'data pipelines to machine learning models that power the future of hiring.'
        ),
        'culture': (
            'We believe in a culture of ownership, transparency, and continuous learning. Engineers at HireX have '
            'autonomy over their work, flexible remote-first schedules, and access to a $2,000 annual learning budget. '
            'We host weekly tech talks, open-source Fridays, and quarterly hackathons.'
        ),
        'benefits': (
            'Competitive salary + equity | Health, dental & vision insurance | Remote-first work | '
            '401(k) with 4% match | $2,000 learning budget | Home office stipend | Unlimited PTO | '
            'Parental leave | Annual team retreats'
        ),
        'location': 'San Francisco, CA (Remote-friendly)',
        'founded': '2015',
    }
)
if emp_created:
    print('✅ Employer profile created')
else:
    print('ℹ️  Employer profile already exists')

# ── 3. Seed 15 Tech Job Posts ─────────────────────────────────────────────────
JOBS = [
    {
        'title': 'Senior Full Stack Engineer',
        'description': (
            'We are looking for a Senior Full Stack Engineer to join our core product team. '
            'You will design and build scalable web applications, mentor junior engineers, '
            'and collaborate closely with product and design teams. You will own features end-to-end '
            'from architecture to deployment on AWS.'
        ),
        'requirements': [
            '5+ years of full stack development experience',
            'Strong proficiency in React and Node.js or Python/Django',
            'Experience with PostgreSQL and Redis',
            'Familiarity with AWS (EC2, S3, RDS, Lambda)',
            'Experience with CI/CD pipelines (GitHub Actions, Jenkins)',
            'Strong understanding of REST APIs and GraphQL',
        ],
        'location': 'San Francisco, CA (Hybrid)',
        'type': 'Full-time',
        'salary': '$130,000 - $170,000',
        'experience': '5+ years',
        'skills': ['React', 'Node.js', 'Python', 'PostgreSQL', 'AWS', 'Docker'],
        'category': 'Engineering',
        'is_skill_based': True,
        'required_skills': ['React', 'Node.js', 'PostgreSQL'],
        'min_match_threshold': 70,
        'is_hot': True,
        'tier': 'promoted',
        'health_score': 90,
    },
    {
        'title': 'Machine Learning Engineer',
        'description': (
            'Join our AI team to build and deploy machine learning models that power our intelligent '
            'recruitment platform. You will work on NLP models for resume parsing, candidate ranking '
            'algorithms, and real-time recommendation systems serving millions of users.'
        ),
        'requirements': [
            '3+ years of ML engineering experience',
            'Strong Python skills (PyTorch or TensorFlow)',
            'Experience with NLP and transformer models (BERT, GPT)',
            'Familiarity with MLOps tools (MLflow, Kubeflow)',
            'Experience deploying models to production at scale',
            'MS or PhD in Computer Science, Statistics, or related field preferred',
        ],
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$140,000 - $190,000',
        'experience': '3+ years',
        'skills': ['Python', 'PyTorch', 'TensorFlow', 'NLP', 'MLOps', 'Kubernetes'],
        'category': 'AI/ML',
        'is_skill_based': True,
        'required_skills': ['Python', 'PyTorch', 'NLP'],
        'min_match_threshold': 75,
        'is_hot': True,
        'tier': 'promoted',
        'health_score': 95,
    },
    {
        'title': 'Frontend Engineer (React)',
        'description': (
            'We are hiring a Frontend Engineer to craft beautiful, performant user interfaces for our '
            'recruitment platform. You will work with our design system, implement complex UI components, '
            'and ensure a seamless experience across devices. You care deeply about accessibility and performance.'
        ),
        'requirements': [
            '3+ years of frontend development experience',
            'Expert-level React and TypeScript skills',
            'Experience with state management (Redux, Zustand, or Jotai)',
            'Strong CSS skills and experience with Tailwind CSS',
            'Knowledge of web performance optimization',
            'Experience with testing (Jest, React Testing Library)',
        ],
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$110,000 - $150,000',
        'experience': '3+ years',
        'skills': ['React', 'TypeScript', 'Tailwind CSS', 'Redux', 'Jest', 'GraphQL'],
        'category': 'Engineering',
        'is_skill_based': True,
        'required_skills': ['React', 'TypeScript', 'Tailwind CSS'],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 85,
    },
    {
        'title': 'DevOps / Platform Engineer',
        'description': (
            'We are looking for a DevOps Engineer to build and maintain our cloud infrastructure. '
            'You will manage Kubernetes clusters, design CI/CD pipelines, implement observability solutions, '
            'and ensure 99.9% uptime for our platform serving 2M+ users.'
        ),
        'requirements': [
            '4+ years of DevOps or platform engineering experience',
            'Strong Kubernetes and Docker expertise',
            'Experience with Terraform or Pulumi for IaC',
            'Proficiency with AWS or GCP',
            'Experience with monitoring tools (Prometheus, Grafana, Datadog)',
            'Strong scripting skills (Bash, Python)',
        ],
        'location': 'San Francisco, CA (Hybrid)',
        'type': 'Full-time',
        'salary': '$125,000 - $165,000',
        'experience': '4+ years',
        'skills': ['Kubernetes', 'Docker', 'Terraform', 'AWS', 'Prometheus', 'Python'],
        'category': 'DevOps',
        'is_skill_based': True,
        'required_skills': ['Kubernetes', 'Terraform', 'AWS'],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 80,
    },
    {
        'title': 'Backend Engineer (Python/Django)',
        'description': (
            'We need a Backend Engineer to build robust APIs and microservices for our platform. '
            'You will design RESTful and GraphQL APIs, optimize database queries, implement caching strategies, '
            'and ensure our backend scales to handle millions of requests per day.'
        ),
        'requirements': [
            '3+ years of backend development with Python',
            'Strong Django and Django REST Framework experience',
            'Proficiency with PostgreSQL and query optimization',
            'Experience with Redis for caching and queuing',
            'Knowledge of microservices architecture',
            'Familiarity with Celery for async task processing',
        ],
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$115,000 - $155,000',
        'experience': '3+ years',
        'skills': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Celery', 'Docker'],
        'category': 'Engineering',
        'is_skill_based': True,
        'required_skills': ['Python', 'Django', 'PostgreSQL'],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 82,
    },
    {
        'title': 'Data Engineer',
        'description': (
            'Join our data team to build the pipelines and infrastructure that power our analytics and ML platform. '
            'You will design ETL pipelines, build data warehouses, and work closely with data scientists '
            'to ensure clean, reliable data at scale.'
        ),
        'requirements': [
            '3+ years of data engineering experience',
            'Strong SQL and Python skills',
            'Experience with Apache Spark or Flink',
            'Familiarity with dbt for data transformation',
            'Experience with cloud data warehouses (Snowflake, BigQuery, or Redshift)',
            'Knowledge of Airflow for pipeline orchestration',
        ],
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$120,000 - $160,000',
        'experience': '3+ years',
        'skills': ['Python', 'SQL', 'Apache Spark', 'dbt', 'Airflow', 'Snowflake'],
        'category': 'Data',
        'is_skill_based': True,
        'required_skills': ['Python', 'SQL', 'Apache Spark'],
        'min_match_threshold': 65,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 78,
    },
    {
        'title': 'iOS Engineer (Swift)',
        'description': (
            'We are building a world-class mobile experience and need an iOS Engineer to lead development '
            'of our iPhone and iPad apps. You will work on a greenfield iOS app, implement complex UI animations, '
            'integrate with our REST APIs, and ship features used by hundreds of thousands of job seekers.'
        ),
        'requirements': [
            '3+ years of iOS development experience',
            'Expert Swift and UIKit/SwiftUI skills',
            'Experience with Combine or async/await concurrency',
            'Knowledge of Core Data and local persistence',
            'Experience publishing apps to the App Store',
            'Familiarity with XCTest for unit and UI testing',
        ],
        'location': 'San Francisco, CA (Hybrid)',
        'type': 'Full-time',
        'salary': '$120,000 - $160,000',
        'experience': '3+ years',
        'skills': ['Swift', 'SwiftUI', 'UIKit', 'Combine', 'Core Data', 'Xcode'],
        'category': 'Mobile',
        'is_skill_based': True,
        'required_skills': ['Swift', 'SwiftUI', 'UIKit'],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 75,
    },
    {
        'title': 'Android Engineer (Kotlin)',
        'description': (
            'We are looking for an Android Engineer to build and maintain our Android application. '
            'You will implement new features using Jetpack Compose, integrate with backend APIs, '
            'optimize app performance, and ensure a smooth experience across a wide range of Android devices.'
        ),
        'requirements': [
            '3+ years of Android development experience',
            'Strong Kotlin skills',
            'Experience with Jetpack Compose',
            'Knowledge of MVVM architecture and Android Jetpack libraries',
            'Experience with Retrofit and OkHttp for networking',
            'Familiarity with Coroutines and Flow',
        ],
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$115,000 - $155,000',
        'experience': '3+ years',
        'skills': ['Kotlin', 'Jetpack Compose', 'Android', 'Coroutines', 'MVVM', 'Retrofit'],
        'category': 'Mobile',
        'is_skill_based': True,
        'required_skills': ['Kotlin', 'Jetpack Compose', 'Android'],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 74,
    },
    {
        'title': 'Cloud Security Engineer',
        'description': (
            'We are hiring a Cloud Security Engineer to protect our infrastructure and customer data. '
            'You will conduct security audits, implement zero-trust architecture, manage IAM policies, '
            'respond to security incidents, and ensure compliance with SOC 2 and ISO 27001 standards.'
        ),
        'requirements': [
            '4+ years of cloud security experience',
            'Deep knowledge of AWS security services (IAM, GuardDuty, Security Hub)',
            'Experience with SIEM tools and incident response',
            'Knowledge of zero-trust network architecture',
            'Familiarity with compliance frameworks (SOC 2, ISO 27001, GDPR)',
            'Security certifications preferred (CISSP, AWS Security Specialty)',
        ],
        'location': 'San Francisco, CA (Hybrid)',
        'type': 'Full-time',
        'salary': '$135,000 - $175,000',
        'experience': '4+ years',
        'skills': ['AWS', 'IAM', 'Security', 'Zero Trust', 'SIEM', 'Compliance'],
        'category': 'Security',
        'is_skill_based': False,
        'required_skills': [],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 80,
    },
    {
        'title': 'Product Manager – Developer Tools',
        'description': (
            'We are looking for a Product Manager to own our developer tools and API platform. '
            'You will define the product roadmap, work closely with engineering teams, gather customer feedback, '
            'and drive adoption of our developer ecosystem. You have a technical background and understand '
            'what developers need.'
        ),
        'requirements': [
            '4+ years of product management experience',
            'Technical background (CS degree or prior engineering experience)',
            'Experience managing developer-facing products or APIs',
            'Strong data analysis skills (SQL, Mixpanel, or Amplitude)',
            'Excellent communication and stakeholder management skills',
            'Experience with agile development methodologies',
        ],
        'location': 'San Francisco, CA (Hybrid)',
        'type': 'Full-time',
        'salary': '$130,000 - $170,000',
        'experience': '4+ years',
        'skills': ['Product Management', 'SQL', 'Agile', 'API Design', 'Data Analysis', 'Roadmapping'],
        'category': 'Product',
        'is_skill_based': False,
        'required_skills': [],
        'min_match_threshold': 60,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 77,
    },
    {
        'title': 'Site Reliability Engineer (SRE)',
        'description': (
            'As an SRE at HireX, you will ensure the reliability, scalability, and performance of our platform. '
            'You will define SLOs, build runbooks, automate toil, conduct blameless post-mortems, '
            'and work with engineering teams to improve system resilience.'
        ),
        'requirements': [
            '4+ years of SRE or infrastructure engineering experience',
            'Strong Linux systems knowledge',
            'Experience with Kubernetes and container orchestration',
            'Proficiency with observability tools (Prometheus, Grafana, Jaeger)',
            'Strong scripting skills (Python, Go, or Bash)',
            'Experience with chaos engineering tools (Chaos Monkey, Gremlin)',
        ],
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$130,000 - $170,000',
        'experience': '4+ years',
        'skills': ['Kubernetes', 'Linux', 'Prometheus', 'Grafana', 'Python', 'Go'],
        'category': 'DevOps',
        'is_skill_based': True,
        'required_skills': ['Kubernetes', 'Prometheus', 'Python'],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 83,
    },
    {
        'title': 'Software Engineer Intern (Summer 2025)',
        'description': (
            'HireX is offering a 12-week paid summer internship for software engineering students. '
            'You will be embedded in a product team, work on real features shipped to production, '
            'receive mentorship from senior engineers, and participate in our intern speaker series '
            'with leaders from top tech companies.'
        ),
        'requirements': [
            'Currently pursuing a BS/MS in Computer Science or related field',
            'Proficiency in at least one programming language (Python, JavaScript, Java, or C++)',
            'Familiarity with data structures and algorithms',
            'Strong problem-solving skills',
            'Ability to work collaboratively in a team environment',
        ],
        'location': 'San Francisco, CA',
        'type': 'Internship',
        'salary': '$45/hour',
        'experience': '0-1 years',
        'skills': ['Python', 'JavaScript', 'Data Structures', 'Algorithms', 'Git'],
        'category': 'Engineering',
        'is_skill_based': False,
        'required_skills': [],
        'min_match_threshold': 50,
        'is_hot': True,
        'tier': 'promoted',
        'health_score': 88,
    },
    {
        'title': 'QA / Automation Engineer',
        'description': (
            'We are looking for a QA Automation Engineer to build and maintain our test infrastructure. '
            'You will design end-to-end test suites, implement API testing frameworks, integrate tests into CI/CD, '
            'and work with developers to shift quality left in our development process.'
        ),
        'requirements': [
            '3+ years of QA automation experience',
            'Strong experience with Selenium, Playwright, or Cypress',
            'Proficiency in Python or JavaScript for test scripting',
            'Experience with API testing (Postman, pytest)',
            'Knowledge of CI/CD integration for automated testing',
            'Understanding of performance testing (k6, JMeter)',
        ],
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$100,000 - $135,000',
        'experience': '3+ years',
        'skills': ['Playwright', 'Selenium', 'Python', 'Pytest', 'CI/CD', 'API Testing'],
        'category': 'Engineering',
        'is_skill_based': True,
        'required_skills': ['Playwright', 'Python', 'Pytest'],
        'min_match_threshold': 65,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 72,
    },
    {
        'title': 'Technical Lead – AI Platform',
        'description': (
            'We are hiring a Technical Lead to drive the architecture and delivery of our AI platform. '
            'You will lead a team of 6 engineers, define technical standards, make key architectural decisions, '
            'and collaborate with the CTO on our long-term AI strategy. This is a high-impact role '
            'at the intersection of engineering leadership and hands-on development.'
        ),
        'requirements': [
            '7+ years of software engineering experience',
            '2+ years of technical leadership experience',
            'Deep expertise in Python and ML frameworks (PyTorch, TensorFlow)',
            'Experience designing distributed systems at scale',
            'Strong communication and mentoring skills',
            'Track record of delivering complex technical projects on time',
        ],
        'location': 'San Francisco, CA (Hybrid)',
        'type': 'Full-time',
        'salary': '$170,000 - $220,000',
        'experience': '7+ years',
        'skills': ['Python', 'PyTorch', 'System Design', 'Technical Leadership', 'Distributed Systems', 'AWS'],
        'category': 'AI/ML',
        'is_skill_based': True,
        'required_skills': ['Python', 'PyTorch', 'System Design'],
        'min_match_threshold': 75,
        'is_hot': True,
        'tier': 'promoted',
        'health_score': 92,
    },
    {
        'title': 'Blockchain Developer',
        'description': (
            'HireX is exploring decentralized credential verification and we need a Blockchain Developer '
            'to prototype and build smart contracts for on-chain resume verification. '
            'You will work with Solidity, integrate with our existing platform via Web3.js, '
            'and research the best L2 solutions for our use case.'
        ),
        'requirements': [
            '2+ years of blockchain development experience',
            'Strong Solidity skills and experience with EVM-compatible chains',
            'Experience with Hardhat or Foundry for smart contract development',
            'Knowledge of Web3.js or Ethers.js',
            'Understanding of DeFi protocols and token standards (ERC-20, ERC-721)',
            'Familiarity with IPFS for decentralized storage',
        ],
        'location': 'Remote',
        'type': 'Contract',
        'salary': '$100 - $150/hour',
        'experience': '2+ years',
        'skills': ['Solidity', 'Ethereum', 'Web3.js', 'Hardhat', 'IPFS', 'Smart Contracts'],
        'category': 'Blockchain',
        'is_skill_based': True,
        'required_skills': ['Solidity', 'Web3.js', 'Hardhat'],
        'min_match_threshold': 70,
        'is_hot': False,
        'tier': 'standard',
        'health_score': 70,
    },
]

deadline = datetime.now(timezone.utc) + timedelta(days=60)
created_count = 0

for job_data in JOBS:
    exists = Job.objects.filter(employer=user, title=job_data['title']).exists()
    if not exists:
        Job.objects.create(
            employer=user,
            company_name=employer.company_name,
            company_logo=employer.company_logo,
            deadline=deadline,
            is_active=True,
            **job_data
        )
        created_count += 1
        print(f'  ✅ Job created: {job_data["title"]}')
    else:
        print(f'  ℹ️  Job exists: {job_data["title"]}')

print(f'\n🎉 Done. {created_count} new jobs created for {employer.company_name}.')
