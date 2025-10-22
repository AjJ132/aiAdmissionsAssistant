"""
Test data fixtures - Sample HTML and JSON data for testing
"""


SAMPLE_DEGREE_LIST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Graduate Programs</title>
</head>
<body>
    <div class="container">
        <h1>Graduate Degree Programs</h1>
        <ul class="degree-list">
            <li><a href="https://example.com/mba">Master of Business Administration (MBA)</a></li>
            <li><a href="https://example.com/mcs">Master of Computer Science (MCS)</a></li>
            <li><a href="https://example.com/med">Master of Education (M.Ed.)</a></li>
            <li><a href="https://example.com/meng">Master of Engineering (M.Eng.)</a></li>
            <li><a href="https://example.com/msn">Master of Science in Nursing (MSN)</a></li>
        </ul>
    </div>
</body>
</html>
"""


SAMPLE_DEGREE_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Master of Computer Science | University</title>
    <meta name="description" content="Advanced graduate program in computer science">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/programs">Programs</a>
        </nav>
    </header>
    
    <main>
        <div class="banner_message">
            <h1>Master of Computer Science</h1>
        </div>
        
        <div class="content">
            <section class="overview">
                <p>The Master of Computer Science program prepares students for advanced careers in software development, 
                artificial intelligence, machine learning, and data science. This comprehensive program combines 
                rigorous theoretical foundations with practical applications in modern computing technologies.</p>
            </section>
            
            <section class="snapshot">
                <h3 id="snapshot">Program Snapshot</h3>
                <div class="info-grid">
                    <p>Credit Hours: 36</p>
                    <p>Format: Online and On-Campus</p>
                    <p>Duration: 2 years full-time</p>
                    <p>Start Terms: Fall, Spring, Summer</p>
                </div>
            </section>
            
            <section class="requirements">
                <h3>Admission Requirements</h3>
                <div class="two-column">
                    <ul>
                        <li><div>Bachelor's degree in Computer Science or related field from an accredited institution</div></li>
                        <li><div>Minimum cumulative GPA of 3.0 on a 4.0 scale</div></li>
                        <li><div>GRE General Test scores (optional for applicants with 3.5+ GPA)</div></li>
                        <li><div>Three letters of recommendation from academic or professional references</div></li>
                        <li><div>Statement of purpose (500-1000 words)</div></li>
                        <li><div>Resume or curriculum vitae</div></li>
                        <li><div>Official transcripts from all previous institutions</div></li>
                        <li><div>TOEFL or IELTS scores for international applicants</div></li>
                    </ul>
                </div>
            </section>
            
            <section class="benefits">
                <h3>Program Benefits and Outcomes</h3>
                <ul>
                    <li>Gain expertise in machine learning and artificial intelligence technologies</li>
                    <li>Work on real-world industry projects with partner companies</li>
                    <li>Network with industry professionals and alumni</li>
                    <li>Access to cutting-edge research facilities and labs</li>
                    <li>Opportunities for research assistantships and teaching assistantships</li>
                    <li>Career placement assistance and professional development workshops</li>
                </ul>
            </section>
            
            <section class="curriculum">
                <h3>Core Curriculum</h3>
                <p>Students complete coursework in algorithms, software engineering, databases, 
                and specialized electives in areas such as cybersecurity, cloud computing, and AI.</p>
            </section>
            
            <section class="contact">
                <h3>Contact Information</h3>
                <div class="contact-details">
                    <p>Graduate Admissions Office</p>
                    <p>Phone: <a href="tel:555-123-4567">(555) 123-4567</a></p>
                    <p>Email: <a href="mailto:cs-grad@example.com">cs-grad@example.com</a></p>
                    <p>Campus: 1234 University Drive, Anytown, ST 12345</p>
                </div>
            </section>
            
            <section class="related">
                <h3>Related Programs</h3>
                <ul>
                    <li><a href="https://example.com/degree/data-science">Master of Data Science</a></li>
                    <li><a href="https://example.com/degree/cyber-security">Master of Cybersecurity</a></li>
                    <li><a href="https://example.com/degree/software-engineering">Master of Software Engineering</a></li>
                </ul>
            </section>
        </div>
    </main>
    
    <footer>
        <p>&copy; 2024 University. All rights reserved.</p>
    </footer>
</body>
</html>
"""


SAMPLE_MINIMAL_HTML = """
<html>
<body>
    <h1>Simple Program</h1>
    <p>This is a minimal degree page with limited information.</p>
</body>
</html>
"""


SAMPLE_HTML_WITH_UNICODE = """
<!DOCTYPE html>
<html>
<head>
    <title>Master's Program</title>
</head>
<body>
    <h1>Master\u2019s Degree in Business Administration</h1>
    <p>The university\u2019s MBA program offers state\u2014of\u2014the\u2014art facilities 
    and prepares students for leadership roles in various industries\u2026</p>
    <p>Contact: email\u00a0us\u00a0at\u00a0mba@example.com for more information.</p>
    <p>Program highlights include \u201cGlobal Business Strategy\u201d and \u201cFinancial Management\u201d courses.</p>
</body>
</html>
"""


SAMPLE_MALFORMED_HTML = """
<html>
<body>
    <h1>Degree Program
    <p>Missing closing tags
    <div>Unclosed div
    <ul>
        <li>Item 1
        <li>Item 2
</body>
"""


SAMPLE_SCRAPING_CONFIG = {
    "grad_admissions_list_url": "https://example.com/graduate-programs",
    "grad_admissions_list_xpath": "//ul[@class='degree-list']",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1
}


SAMPLE_DEGREE_DATA = [
    {
        "name": "Master of Business Administration",
        "url": "https://example.com/mba"
    },
    {
        "name": "Master of Computer Science",
        "url": "https://example.com/mcs"
    },
    {
        "name": "Master of Education",
        "url": "https://example.com/med"
    }
]


SAMPLE_EXTRACTED_CONTENT = {
    'title': 'Master of Computer Science',
    'description': 'The Master of Computer Science program prepares students for advanced careers in software development.',
    'program_snapshot': {
        'Credit Hours': '36',
        'Format': 'Online and On-Campus',
        'Duration': '2 years full-time',
        'Start Terms': 'Fall, Spring, Summer'
    },
    'admission_requirements': [
        "Bachelor's degree in Computer Science or related field from an accredited institution",
        'Minimum cumulative GPA of 3.0 on a 4.0 scale',
        'GRE General Test scores (optional for applicants with 3.5+ GPA)',
        'Three letters of recommendation from academic or professional references',
        'Statement of purpose (500-1000 words)'
    ],
    'program_benefits': [
        'Gain expertise in machine learning and artificial intelligence technologies',
        'Work on real-world industry projects with partner companies',
        'Network with industry professionals and alumni',
        'Access to cutting-edge research facilities and labs'
    ],
    'contact_info': {
        'phone': '(555) 123-4567',
        'email': 'cs-grad@example.com'
    },
    'related_programs': [
        {'name': 'Master of Data Science', 'url': 'https://example.com/degree/data-science'},
        {'name': 'Master of Cybersecurity', 'url': 'https://example.com/degree/cyber-security'}
    ],
    'key_sections': {
        'Core Curriculum': 'Students complete coursework in algorithms, software engineering...'
    },
    'all_text': 'Master of Computer Science The Master of Computer Science program...'
}
