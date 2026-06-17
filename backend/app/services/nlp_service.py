"""
nlp_service.py  —  Intelligent CV Analysis Engine
====================================================
Layers of intelligence (no external AI API needed):

  1. Semantic skill grouping     — understands that "ReactJS" == "React.js"
                                   and "ML" relates to "machine learning"
  2. Word embedding similarity   — PMI-based co-occurrence vectors built from
                                   the CV+JD corpus itself (no model download)
  3. Experience level detector   — Junior / Mid / Senior from language cues
  4. Achievement quality scorer  — rewards metrics, action verbs, impact words
  5. Section-aware analysis      — scores experience / education / skills
                                   sections separately
  6. Career-path suggestion engine — recommends specific courses, platforms,
                                   project ideas, and internship paths per
                                   missing skill cluster
"""

import re
import math
from collections import Counter, defaultdict


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  SKILL ONTOLOGY  (semantic groups — variants map to a canonical name)
# ═══════════════════════════════════════════════════════════════════════════════

SKILL_ONTOLOGY = {
    # ── Frontend ────────────────────────────────────────────────────────────
    "React":          ["react", "reactjs", "react.js", "react js"],
    "Vue":            ["vue", "vuejs", "vue.js", "vue js", "nuxt"],
    "Angular":        ["angular", "angularjs", "angular.js"],
    "Next.js":        ["next.js", "nextjs", "next js"],
    "TypeScript":     ["typescript", "ts"],
    "JavaScript":     ["javascript", "js", "es6", "es2015"],
    "HTML/CSS":       ["html", "css", "html5", "css3"],
    "Tailwind":       ["tailwind", "tailwindcss"],
    "Redux":          ["redux", "redux toolkit", "zustand", "recoil"],
    "Webpack/Vite":   ["webpack", "vite", "parcel", "bundler"],

    # ── Backend ─────────────────────────────────────────────────────────────
    "Python":         ["python", "py"],
    "Node.js":        ["node.js", "nodejs", "node js"],
    "FastAPI":        ["fastapi", "fast api"],
    "Django":         ["django"],
    "Flask":          ["flask"],
    "Express":        ["express", "express.js", "expressjs"],
    "Java":           ["java"],
    "Spring Boot":    ["spring", "spring boot", "springboot"],
    "C#/.NET":        ["c#", ".net", "asp.net", "dotnet"],
    "Go":             ["go", "golang"],
    "PHP/Laravel":    ["php", "laravel"],
    "GraphQL":        ["graphql", "graph ql"],
    "REST APIs":      ["rest", "restful", "rest api", "api design"],

    # ── Mobile ──────────────────────────────────────────────────────────────
    "React Native":   ["react native", "react-native"],
    "Flutter":        ["flutter", "dart"],
    "Android":        ["android", "kotlin", "android studio"],
    "iOS/Swift":      ["ios", "swift", "xcode"],

    # ── Databases ───────────────────────────────────────────────────────────
    "SQL":            ["sql", "mysql", "postgresql", "postgres", "sqlite", "mariadb"],
    "MongoDB":        ["mongodb", "mongo", "mongoose"],
    "Redis":          ["redis"],
    "Firebase":       ["firebase", "firestore"],
    "Elasticsearch":  ["elasticsearch", "elastic search", "opensearch"],
    "NoSQL":          ["nosql", "dynamodb", "cassandra", "couchdb"],

    # ── Cloud / DevOps ──────────────────────────────────────────────────────
    "AWS":            ["aws", "amazon web services", "ec2", "s3", "lambda", "rds"],
    "Azure":          ["azure", "microsoft azure"],
    "GCP":            ["gcp", "google cloud", "google cloud platform"],
    "Docker":         ["docker", "dockerfile", "containerization", "containers"],
    "Kubernetes":     ["kubernetes", "k8s", "kubectl", "helm"],
    "CI/CD":          ["ci/cd", "cicd", "jenkins", "github actions", "gitlab ci",
                       "travis", "circle ci", "continuous integration"],
    "Terraform":      ["terraform", "infrastructure as code", "iac"],
    "Linux":          ["linux", "ubuntu", "bash", "shell scripting", "unix"],

    # ── AI / Data Science ───────────────────────────────────────────────────
    "Machine Learning": ["machine learning", "ml", "supervised learning",
                         "unsupervised learning", "scikit-learn", "sklearn"],
    "Deep Learning":  ["deep learning", "dl", "neural network", "cnn", "rnn",
                       "lstm", "transformer"],
    "TensorFlow":     ["tensorflow", "tf", "keras"],
    "PyTorch":        ["pytorch", "torch"],
    "Data Analysis":  ["data analysis", "data analytics", "pandas", "numpy",
                       "matplotlib", "seaborn", "data visualization"],
    "NLP":            ["nlp", "natural language processing", "text analysis",
                       "spacy", "nltk", "huggingface"],
    "Computer Vision":["computer vision", "opencv", "cv2", "image processing"],
    "LLM/GenAI":      ["llm", "generative ai", "genai", "langchain", "openai",
                       "chatgpt", "prompt engineering"],
    "SQL Analytics":  ["sql", "bigquery", "redshift", "snowflake", "dbt"],

    # ── Tools & Practices ───────────────────────────────────────────────────
    "Git":            ["git", "github", "gitlab", "bitbucket", "version control"],
    "Agile/Scrum":    ["agile", "scrum", "kanban", "sprint", "jira", "confluence"],
    "Testing":        ["testing", "unit test", "jest", "pytest", "selenium",
                       "cypress", "tdd", "test driven"],
    "Figma/UI":       ["figma", "adobe xd", "sketch", "ui design", "ux design",
                       "wireframing", "prototyping"],
    "Microservices":  ["microservices", "micro services", "service mesh",
                       "event driven", "message queue", "kafka", "rabbitmq"],

    # ── Soft Skills ─────────────────────────────────────────────────────────
    "Leadership":     ["leadership", "led", "managed team", "team lead",
                       "mentoring", "mentored"],
    "Communication":  ["communication", "presentation", "stakeholder",
                       "client facing", "technical writing"],
    "Problem Solving":["problem solving", "analytical", "critical thinking",
                       "debugging", "troubleshooting"],
    "Project Mgmt":   ["project management", "project manager", "pmp",
                       "roadmap", "planning", "delivery"],
    "Collaboration":  ["teamwork", "collaboration", "cross functional",
                       "cross-functional", "team player"],
}

# Build reverse lookup: variant → canonical
VARIANT_TO_CANONICAL = {}
for canonical, variants in SKILL_ONTOLOGY.items():
    VARIANT_TO_CANONICAL[canonical.lower()] = canonical
    for v in variants:
        VARIANT_TO_CANONICAL[v.lower()] = canonical


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  CAREER GUIDANCE DATABASE
#     For each skill cluster → courses, projects, internship paths
# ═══════════════════════════════════════════════════════════════════════════════

CAREER_GUIDANCE = {
    "AWS": {
        "courses": [
            "AWS Certified Cloud Practitioner (free prep on AWS Skill Builder)",
            "freeCodeCamp — AWS Certified Cloud Practitioner on YouTube (free)",
            "Stephane Maarek's AWS course on Udemy",
        ],
        "projects": [
            "Deploy a static website on S3 with CloudFront CDN",
            "Build a serverless REST API using AWS Lambda + API Gateway",
            "Set up an EC2 instance with RDS database and auto-scaling",
        ],
        "internships": [
            "Apply for AWS re/Start program (free, leads to cloud roles)",
            "Look for 'Cloud Engineer Intern' or 'DevOps Intern' on LinkedIn",
            "Contribute to open-source cloud projects on GitHub to build portfolio",
        ],
        "timeline": "2–3 months to get AWS Cloud Practitioner certified",
    },
    "Docker": {
        "courses": [
            "Docker's official 'Getting Started' guide at docs.docker.com (free)",
            "TechWorld with Nana — Docker tutorial on YouTube (free)",
            "KodeKloud Docker course (has free tier)",
        ],
        "projects": [
            "Dockerize your existing React + FastAPI project",
            "Create a docker-compose setup with frontend, backend, and database",
            "Build and push a custom Docker image to Docker Hub",
        ],
        "internships": [
            "Target 'Backend Intern' or 'DevOps Intern' roles that mention containers",
            "Freelance on Upwork — many clients need Docker setup help",
        ],
        "timeline": "2–4 weeks to become comfortable with Docker",
    },
    "Kubernetes": {
        "courses": [
            "Kubernetes Official Interactive Tutorial at kubernetes.io (free)",
            "TechWorld with Nana — Kubernetes full course on YouTube (free)",
            "Certified Kubernetes Application Developer (CKAD) — target after basics",
        ],
        "projects": [
            "Deploy your Dockerized app to a local Kubernetes cluster using Minikube",
            "Set up Kubernetes with Helm charts for multi-service deployment",
            "Implement auto-scaling and rolling updates in Kubernetes",
        ],
        "internships": [
            "Target 'Platform Engineer Intern' or 'Site Reliability Engineer Intern'",
            "Kubernetes is senior-level — focus on Docker first, then K8s",
        ],
        "timeline": "1–2 months after mastering Docker",
    },
    "Machine Learning": {
        "courses": [
            "Andrew Ng's Machine Learning Specialization on Coursera (audit free)",
            "fast.ai Practical Deep Learning course (completely free)",
            "Kaggle Learn — ML mini-courses (free, hands-on)",
        ],
        "projects": [
            "Build a sentiment analysis model on Twitter/product reviews dataset",
            "Create a house price predictor using scikit-learn",
            "Participate in a Kaggle competition — even finishing is portfolio gold",
        ],
        "internships": [
            "Apply for 'ML Research Intern' at startups via LinkedIn and AngelList",
            "Contribute to open-source ML projects like scikit-learn or Hugging Face",
            "Pakistani companies like Systems Ltd, Arbisoft, and 10Pearls hire ML interns",
        ],
        "timeline": "3–6 months to build solid ML foundations",
    },
    "Deep Learning": {
        "courses": [
            "fast.ai — Practical Deep Learning for Coders (free)",
            "DeepLearning.AI Deep Learning Specialization on Coursera (audit free)",
            "PyTorch official tutorials at pytorch.org (free)",
        ],
        "projects": [
            "Build an image classifier using CNN (cats vs dogs dataset)",
            "Create a text generation model using LSTM",
            "Fine-tune a pre-trained model from Hugging Face on custom data",
        ],
        "internships": [
            "Look for 'AI/ML Intern' at tech companies in Lahore/Karachi/Islamabad",
            "Remote internships on Internshala for AI roles",
            "Research assistant positions at NUST, LUMS, or FAST universities",
        ],
        "timeline": "4–6 months after covering ML basics",
    },
    "CI/CD": {
        "courses": [
            "GitHub Actions official documentation and quickstart (free)",
            "DevOps with GitLab CI — YouTube tutorials by TechWorld with Nana (free)",
            "The DevOps Handbook — book for understanding the concepts",
        ],
        "projects": [
            "Set up GitHub Actions to auto-test and deploy your React app to Vercel",
            "Create a full CI/CD pipeline: lint → test → build → deploy",
            "Add automated testing with coverage reports to an existing project",
        ],
        "internships": [
            "Any 'DevOps Intern' or 'Backend Intern' role will involve CI/CD",
            "Offer to set up CI/CD for open-source projects as contribution",
        ],
        "timeline": "1–2 weeks to set up your first pipeline",
    },
    "React": {
        "courses": [
            "React official docs new tutorial at react.dev (free — best starting point)",
            "Scrimba React course (free tier available, interactive)",
            "Jonas Schmedtmann's React course on Udemy",
        ],
        "projects": [
            "Build a full CRUD app with React + a REST API backend",
            "Create an e-commerce frontend with cart, auth, and product filtering",
            "Build a real-time chat app using React + WebSockets",
        ],
        "internships": [
            "Apply for 'Frontend Intern' roles on LinkedIn, Rozee.pk, and Internshala",
            "Agencies in Pakistan (Arbisoft, Tintash, Invozone) frequently hire React interns",
            "Build 2–3 polished React projects and put them on GitHub before applying",
        ],
        "timeline": "2–3 months to build job-ready React skills",
    },
    "React Native": {
        "courses": [
            "React Native official docs at reactnative.dev (free)",
            "Expo documentation and tutorials (free — easiest way to start)",
            "Stephen Grider's React Native course on Udemy",
        ],
        "projects": [
            "Build a cross-platform todo/habit tracker app",
            "Create a weather app using a free weather API",
            "Build a simple e-commerce mobile app with cart and checkout",
        ],
        "internships": [
            "Search 'Mobile Developer Intern' on LinkedIn and Rozee.pk",
            "Many startups in Pakistan need React Native developers urgently",
            "Freelancing on Upwork — mobile app projects are high-paying",
        ],
        "timeline": "2–3 months if you already know React",
    },
    "Flutter": {
        "courses": [
            "Flutter official docs and codelabs at flutter.dev (free)",
            "Angela Yu's Flutter Bootcamp on Udemy",
            "Vandad Nahavandipoor's Flutter course on YouTube (free)",
        ],
        "projects": [
            "Build a cross-platform task manager app with local storage",
            "Create a news reader app using a public API",
            "Build a Firebase-backed social app with auth and real-time data",
        ],
        "internships": [
            "Flutter is highly in-demand in Pakistan — search 'Flutter Intern' on Rozee.pk",
            "Many local software houses prefer Flutter over React Native now",
        ],
        "timeline": "2–3 months to build production-ready Flutter apps",
    },
    "SQL": {
        "courses": [
            "SQLZoo — interactive SQL tutorial (completely free)",
            "Khan Academy SQL course (free)",
            "Mode Analytics SQL Tutorial (free, business-focused)",
        ],
        "projects": [
            "Build a student management system with complex SQL queries",
            "Analyze a public dataset from Kaggle using SQL",
            "Create a database schema for an e-commerce system with joins, indexes",
        ],
        "internships": [
            "Almost every data or backend internship requires SQL",
            "Look for 'Data Analyst Intern' roles — SQL is the core skill",
        ],
        "timeline": "2–4 weeks to learn SQL basics, months to master it",
    },
    "Git": {
        "courses": [
            "GitHub's official 'Git Handbook' at guides.github.com (free)",
            "Atlassian Git tutorial at atlassian.com/git (free, excellent)",
            "Oh My Git! — interactive game to learn Git (free)",
        ],
        "projects": [
            "Contribute to any open-source project on GitHub",
            "Set up a proper Git workflow for your existing projects",
            "Practice rebasing, cherry-picking, and resolving merge conflicts",
        ],
        "internships": [
            "Git is required for every software internship — learn it before applying",
            "Your GitHub profile with green contribution graph matters a lot",
        ],
        "timeline": "1–2 weeks for basics, ongoing practice",
    },
    "Testing": {
        "courses": [
            "Testing JavaScript by Kent C. Dodds at testingjavascript.com",
            "pytest official documentation (free)",
            "Cypress real-world app testing tutorial (free)",
        ],
        "projects": [
            "Add 80%+ test coverage to one of your existing projects",
            "Write end-to-end tests for a web app using Cypress",
            "Practice TDD by building a feature test-first",
        ],
        "internships": [
            "QA Automation Intern roles need testing skills",
            "Adding tests to your projects shows maturity — impresses interviewers",
        ],
        "timeline": "2–3 weeks to get comfortable with testing",
    },
    "TypeScript": {
        "courses": [
            "TypeScript official handbook at typescriptlang.org (free)",
            "Matt Pocock's TypeScript tutorials on YouTube (free, excellent)",
            "Execute Program TypeScript course (some free content)",
        ],
        "projects": [
            "Migrate one of your JavaScript projects to TypeScript",
            "Build a typed REST API client with TypeScript",
            "Create a TypeScript library with proper type definitions",
        ],
        "internships": [
            "Most modern frontend roles prefer TypeScript over plain JavaScript",
            "It's a quick upgrade if you already know JavaScript",
        ],
        "timeline": "2–3 weeks if you know JavaScript",
    },
    "GraphQL": {
        "courses": [
            "GraphQL official tutorial at graphql.org/learn (free)",
            "How to GraphQL at howtographql.com (free, excellent)",
            "Apollo GraphQL official docs and tutorials (free)",
        ],
        "projects": [
            "Build a GraphQL API for an existing REST project",
            "Create a full-stack app with React + Apollo Client + GraphQL backend",
            "Build a GitHub GraphQL API explorer using their public API",
        ],
        "internships": [
            "Target 'Full Stack Intern' roles at startups using modern stacks",
        ],
        "timeline": "2–3 weeks to understand basics",
    },
    "Linux": {
        "courses": [
            "Linux Journey at linuxjourney.com (free, beginner friendly)",
            "The Linux Command Line — free book at linuxcommand.org",
            "OverTheWire Bandit — learn Linux through security challenges (free, fun)",
        ],
        "projects": [
            "Set up a Linux server on a free Oracle Cloud instance",
            "Write shell scripts to automate repetitive dev tasks",
            "Host your project on a Linux VPS using Nginx",
        ],
        "internships": [
            "All DevOps and backend roles require Linux knowledge",
            "Get comfortable before any technical interview",
        ],
        "timeline": "2–4 weeks for practical proficiency",
    },
    "Agile/Scrum": {
        "courses": [
            "Scrum.org free Scrum guide and learning path (free)",
            "Coursera — Agile with Atlassian Jira (free to audit)",
            "LinkedIn Learning — Agile Foundations (free with student access)",
        ],
        "projects": [
            "Apply Scrum to your own projects — use GitHub Projects as Kanban board",
            "Join a hackathon and practice agile sprint planning with your team",
        ],
        "internships": [
            "Every software team uses Agile — knowing the terminology helps interviews",
            "Mention specific Agile experiences in your CV (sprints, stand-ups, retrospectives)",
        ],
        "timeline": "1 week to understand concepts",
    },
    "LLM/GenAI": {
        "courses": [
            "DeepLearning.AI short courses at learn.deeplearning.ai (free, excellent)",
            "Hugging Face NLP course at huggingface.co/learn (free)",
            "Andrej Karpathy's Neural Networks Zero to Hero on YouTube (free)",
        ],
        "projects": [
            "Build a RAG (Retrieval Augmented Generation) chatbot",
            "Create a document summarizer using a free LLM API",
            "Fine-tune a small language model on a custom dataset",
        ],
        "internships": [
            "AI startups globally are hiring aggressively — search 'AI Engineer Intern'",
            "Hugging Face, Replicate, and similar platforms accept contributors",
            "Pakistani AI companies like Axact, Folio3, and Netsol hiring AI interns",
        ],
        "timeline": "1–2 months to build real LLM applications",
    },
    "Data Analysis": {
        "courses": [
            "Kaggle Learn — Pandas and Data Visualization (free, hands-on)",
            "Google Data Analytics Certificate on Coursera (can audit free)",
            "Python for Data Analysis — book by Wes McKinney (pandas creator)",
        ],
        "projects": [
            "Analyze Pakistan's economic or education dataset from data.gov.pk",
            "Build an interactive dashboard using Plotly or Streamlit",
            "Complete 3 Kaggle datasets analysis projects end-to-end",
        ],
        "internships": [
            "Search 'Data Analyst Intern' on LinkedIn — huge demand",
            "E-commerce companies in Pakistan (Daraz etc.) hire data interns",
        ],
        "timeline": "1–2 months to become job-ready",
    },
    "Microservices": {
        "courses": [
            "Sam Newman's 'Building Microservices' — industry standard book",
            "Udemy — Microservices with Node.js and React by Stephen Grider",
            "Martin Fowler's microservices articles at martinfowler.com (free)",
        ],
        "projects": [
            "Break a monolith project into 3+ microservices communicating via REST",
            "Implement event-driven architecture using RabbitMQ or Kafka",
            "Deploy microservices using Docker Compose",
        ],
        "internships": [
            "Mid to senior level topic — build the foundation first",
            "Target 'Backend Engineer Intern' at scale-ups and product companies",
        ],
        "timeline": "2–3 months after solid backend fundamentals",
    },
}

# Default guidance for skills not in the database
DEFAULT_GUIDANCE = {
    "courses": [
        "Search the skill name on Coursera or edX and audit the top-rated course (free)",
        "YouTube is excellent — search '[skill name] tutorial for beginners'",
        "Official documentation is always the most up-to-date learning resource",
    ],
    "projects": [
        "Build a small project that uses this skill alongside your existing tech stack",
        "Contribute to an open-source project that uses this technology",
        "Recreate a simple version of a popular tool that uses this skill",
    ],
    "internships": [
        "Search '[skill name] Intern' on LinkedIn, Rozee.pk, and Internshala",
        "Pakistani software houses like Arbisoft, Tintash, Systems Ltd hire for most tech roles",
        "Freelancing on Upwork or Fiverr helps build practical experience",
    ],
    "timeline": "2–6 weeks depending on complexity",
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  TEXT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "that", "this", "these", "those",
    "i", "we", "you", "he", "she", "they", "it", "its", "our", "your",
    "their", "my", "his", "her", "us", "as", "by", "from", "up", "about",
    "into", "through", "during", "including", "until", "while", "against",
    "between", "also", "not", "no", "nor", "so", "yet", "both", "either",
    "each", "few", "more", "most", "other", "some", "such", "than", "too",
    "very", "just", "because", "if", "then", "than", "when", "where",
    "who", "which", "what", "how", "all", "any", "been",
}

def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\.\+#/]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text: str) -> list:
    words = re.findall(r"\b[a-z][a-z0-9]*\b", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"[.!?\n]", text) if len(s.strip()) > 15]


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  SEMANTIC SKILL EXTRACTION  (ontology-aware)
# ═══════════════════════════════════════════════════════════════════════════════

def extract_skills(text: str) -> set:
    """
    Extract canonical skill names from text.
    Uses longest-match so 'React Native' beats 'React'.
    """
    ct = clean(text)
    found = set()

    # Sort variants by length desc so longer phrases match first
    sorted_variants = sorted(VARIANT_TO_CANONICAL.keys(), key=len, reverse=True)

    for variant in sorted_variants:
        pattern = r"\b" + re.escape(variant) + r"\b"
        if re.search(pattern, ct):
            found.add(VARIANT_TO_CANONICAL[variant])

    return found


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  PMI-BASED WORD VECTOR SIMILARITY  (our own "embeddings")
# ═══════════════════════════════════════════════════════════════════════════════

def build_cooccurrence(texts: list, window: int = 4) -> dict:
    """Build word co-occurrence counts from a list of text strings."""
    word_count = Counter()
    pair_count = Counter()

    for text in texts:
        tokens = tokenize(text)
        for i, w in enumerate(tokens):
            word_count[w] += 1
            context = tokens[max(0, i - window): i] + tokens[i + 1: i + window + 1]
            for c in context:
                pair = tuple(sorted([w, c]))
                pair_count[pair] += 1

    return word_count, pair_count


def pmi_similarity(text_a: str, text_b: str) -> float:
    """
    Compute semantic similarity using PMI-weighted term overlap.
    Words that co-occur together in the combined corpus get higher weight.
    This is our custom word-embedding-inspired similarity.
    """
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)

    if not tokens_a or not tokens_b:
        return 0.0

    word_count, pair_count = build_cooccurrence([text_a, text_b])
    total = sum(word_count.values()) + 1

    set_a = set(tokens_a)
    set_b = set(tokens_b)
    shared = set_a & set_b

    if not shared:
        # Fall back to Jaccard
        return len(shared) / len(set_a | set_b)

    # PMI-weighted overlap
    pmi_score = 0.0
    for w in shared:
        p_w = word_count[w] / total
        # PMI of word with itself = log(p(w) / p(w)^2) simplified
        pmi = max(0, math.log((p_w + 1e-10) / (p_w ** 2 + 1e-10)))
        pmi_score += pmi

    # Normalise
    max_possible = sum(
        max(0, math.log((word_count[w] / total + 1e-10) /
                        ((word_count[w] / total) ** 2 + 1e-10)))
        for w in (set_a | set_b)
    )

    if max_possible == 0:
        return 0.0

    raw = pmi_score / max_possible

    # Blend with tf-idf cosine for robustness
    tfidf = _tfidf_cosine(tokens_a, tokens_b)
    return round((raw * 0.5 + tfidf * 0.5), 4)


def _tfidf_cosine(tokens_a: list, tokens_b: list) -> float:
    vocab = set(tokens_a) | set(tokens_b)
    docs = [tokens_a, tokens_b]
    N = 2

    idf = {}
    for term in vocab:
        df = sum(1 for doc in docs if term in doc)
        idf[term] = math.log((N + 1) / (df + 1)) + 1

    def vec(tokens):
        tf = Counter(tokens)
        total = len(tokens) or 1
        return {t: (tf[t] / total) * idf.get(t, 0) for t in vocab}

    va, vb = vec(tokens_a), vec(tokens_b)
    dot = sum(va[t] * vb[t] for t in vocab)
    ma = math.sqrt(sum(v ** 2 for v in va.values()))
    mb = math.sqrt(sum(v ** 2 for v in vb.values()))

    if ma == 0 or mb == 0:
        return 0.0
    return min(dot / (ma * mb), 1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  EXPERIENCE LEVEL DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

SENIOR_SIGNALS = [
    "led", "managed", "architected", "designed", "mentored", "director",
    "principal", "staff", "head of", "vp", "chief", "founded", "co-founder",
    "scaled", "10+ years", "8+ years", "7+ years", "team of",
    "oversaw", "established", "drove", "owned",
]

MID_SIGNALS = [
    "developed", "implemented", "built", "improved", "optimized", "contributed",
    "collaborated", "integrated", "deployed", "maintained", "3 years", "4 years",
    "5 years", "2+ years", "senior", "mid", "intermediate",
]

JUNIOR_SIGNALS = [
    "intern", "internship", "fresher", "graduate", "entry level", "entry-level",
    "0-1 year", "1 year", "junior", "beginner", "learning", "student",
    "currently studying", "final year", "final-year",
]

def detect_experience_level(cv_text: str) -> tuple:
    """Returns (level_str, score_0_to_100, explanation)"""
    ct = cv_text.lower()

    senior_hits = sum(1 for s in SENIOR_SIGNALS if s in ct)
    mid_hits    = sum(1 for s in MID_SIGNALS    if s in ct)
    junior_hits = sum(1 for s in JUNIOR_SIGNALS if s in ct)

    # Years of experience extractor
    years_mentions = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", ct)
    max_years = max((int(y) for y in years_mentions), default=0)

    if max_years >= 5 or senior_hits >= 3:
        level = "Senior"
        score = min(95, 70 + senior_hits * 5 + max_years * 2)
        explanation = f"Senior-level signals detected ({senior_hits} leadership/architecture cues)"
    elif max_years >= 2 or mid_hits >= 4:
        level = "Mid-level"
        score = min(75, 50 + mid_hits * 3 + max_years * 4)
        explanation = f"Mid-level experience evident ({max_years} years, {mid_hits} development cues)"
    elif junior_hits >= 2 or max_years <= 1:
        level = "Junior / Entry"
        score = min(55, 30 + mid_hits * 3 + junior_hits * 2)
        explanation = f"Early-career profile ({junior_hits} entry-level signals)"
    else:
        level = "Mid-level"
        score = 50
        explanation = "Experience level unclear from CV language"

    return level, score, explanation


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  ACHIEVEMENT QUALITY SCORER
# ═══════════════════════════════════════════════════════════════════════════════

ACTION_VERBS = [
    "built", "developed", "designed", "implemented", "created", "launched",
    "deployed", "optimized", "improved", "reduced", "increased", "automated",
    "led", "managed", "delivered", "shipped", "scaled", "refactored",
    "integrated", "migrated", "architected", "established", "streamlined",
    "pioneered", "spearheaded", "negotiated", "generated", "saved",
]

def score_achievements(cv_text: str) -> tuple:
    """
    Scores the quality of achievement language.
    Returns (score_0_to_100, list_of_findings)
    """
    findings = []
    score = 40.0  # base

    sents = sentences(cv_text)

    # Count action-verb bullets
    action_count = sum(
        1 for s in sents
        if any(s.lower().strip().startswith(v) for v in ACTION_VERBS)
    )
    score += min(action_count * 3, 20)
    if action_count >= 5:
        findings.append(f"Good use of {action_count} strong action verbs")
    elif action_count < 3:
        findings.append("More action verbs needed (Built, Reduced, Launched, etc.)")

    # Count quantified achievements (numbers + context)
    metrics = re.findall(
        r"\b(\d[\d,]*)\s*(%|percent|million|billion|k\b|users|customers|"
        r"projects|clients|hours|days|weeks|x faster|times faster|"
        r"reduction|increase|improvement|revenue|sales|team|engineers|members)",
        cv_text.lower()
    )
    score += min(len(metrics) * 5, 25)
    if len(metrics) >= 4:
        findings.append(f"Excellent — {len(metrics)} quantified achievements found")
    elif len(metrics) >= 1:
        findings.append(f"{len(metrics)} metric(s) found — add more numbers to stand out")
    else:
        findings.append("No metrics detected — add numbers to ALL key achievements")

    # Check for impact words
    impact_words = ["saved", "generated", "reduced", "increased", "improved",
                    "delivered", "revenue", "cost", "efficiency", "performance"]
    impact_hits = sum(1 for w in impact_words if w in cv_text.lower())
    score += min(impact_hits * 2, 10)

    # Length check
    words = len(cv_text.split())
    if 400 <= words <= 1200:
        score += 5
        findings.append("Good CV length")
    elif words < 200:
        score -= 10
        findings.append("CV is very short — expand your experience and project details")
    elif words > 2000:
        findings.append("CV may be too long — aim for 1–2 pages")

    return round(min(max(score, 0), 100), 1), findings


# ═══════════════════════════════════════════════════════════════════════════════
# 8.  SECTION-AWARE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_PATTERNS = {
    "experience": r"(work\s+experience|experience|employment|professional\s+experience|work\s+history)",
    "education":  r"(education|academic|qualification|degree|university|college)",
    "skills":     r"(skills|technical\s+skills|competencies|expertise|technologies|tools)",
    "summary":    r"(summary|objective|profile|about\s+me|professional\s+summary|overview)",
    "projects":   r"(projects?|portfolio|personal\s+projects?|side\s+projects?)",
    "certs":      r"(certifications?|certificates?|licenses?|awards?|achievements?)",
}

def extract_sections(text: str) -> dict:
    sections = defaultdict(list)
    lines = text.split("\n")
    current = "general"

    for line in lines:
        ll = line.strip().lower()
        matched = False
        for sec, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, ll) and len(ll) < 60:
                current = sec
                matched = True
                break
        sections[current].append(line)

    return {k: "\n".join(v) for k, v in sections.items()}


def score_education_section(edu_text: str, jd_text: str) -> tuple:
    """Returns (score, notes)"""
    score = 40.0
    notes = []

    degree_patterns = {
        "phd": 100, "doctorate": 100, "ph.d": 100,
        "master": 85, "m.sc": 85, "msc": 85, "m.s": 85, "m.tech": 85,
        "bachelor": 70, "b.sc": 70, "bsc": 70, "b.s": 70, "b.tech": 70,
        "b.e": 70, "associate": 55, "diploma": 50,
    }

    edu_lower = edu_text.lower()
    found_degree = None
    for deg, val in degree_patterns.items():
        if deg in edu_lower:
            found_degree = (deg, val)
            break

    if found_degree:
        score = found_degree[1]
        notes.append(f"Degree detected: {found_degree[0].title()}")
    else:
        notes.append("No formal degree detected in education section")

    # CGPA / GPA bonus
    gpa_match = re.search(r"(cgpa|gpa|grade)[:\s]*([0-9.]+)", edu_lower)
    if gpa_match:
        try:
            gpa = float(gpa_match.group(2))
            if gpa >= 3.5 or gpa >= 85:  # 4.0 scale or 100 scale
                score = min(score + 10, 100)
                notes.append(f"Strong academic record (GPA: {gpa})")
        except ValueError:
            pass

    # Relevant field check
    cs_fields = ["computer science", "software", "engineering", "information technology",
                 "it", "data science", "mathematics", "physics"]
    if any(f in edu_lower for f in cs_fields):
        score = min(score + 5, 100)
        notes.append("Relevant field of study")

    return round(score), notes


# ═══════════════════════════════════════════════════════════════════════════════
# 9.  ATS INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════

def smart_ats_score(cv_text: str, jd_text: str) -> tuple:
    """
    Smarter ATS scoring:
    - Weights keywords by frequency in JD (more mentions = more important)
    - Handles semantic variants (e.g., 'JS' matches 'JavaScript' cluster)
    - Returns (score, missing_keywords, matched_keywords)
    """
    jd_tokens = tokenize(jd_text)
    cv_skills  = extract_skills(cv_text)
    jd_skills  = extract_skills(jd_text)

    # Frequency-weighted JD keywords
    freq = Counter(jd_tokens)
    important_words = {t: c for t, c in freq.items() if len(t) > 3 and c >= 2}

    if not important_words:
        important_words = {t: 1 for t in jd_tokens if len(t) > 3}

    cv_token_set = set(tokenize(cv_text))

    # Score each important keyword
    total_weight = sum(important_words.values())
    matched_weight = sum(
        w for t, w in important_words.items() if t in cv_token_set
    )

    raw_ats = (matched_weight / total_weight * 100) if total_weight else 50

    # Skill-level ATS (canonical skill matching)
    skill_match_ratio = len(cv_skills & jd_skills) / max(len(jd_skills), 1)
    skill_ats = skill_match_ratio * 100

    # Blend
    final_ats = round(raw_ats * 0.5 + skill_ats * 0.5)

    # Find specifically missing JD phrases that should be in CV
    missing_phrases = []
    for t, count in sorted(important_words.items(), key=lambda x: -x[1]):
        if t not in cv_token_set and count >= 3:
            missing_phrases.append(t)

    return min(100, max(15, final_ats)), missing_phrases[:5]


# ═══════════════════════════════════════════════════════════════════════════════
# 10.  INTELLIGENT SUGGESTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
# 10a.  DYNAMIC ACHIEVEMENT EXAMPLE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

# Maps skill clusters → (weak_bullet, strong_bullet_template)
_ACHIEVEMENT_EXAMPLES = {
    # Frontend
    "React": (
        "Worked on React components for the frontend",
        "Built {n} reusable React components, reducing UI development time by {pct}% across {proj} projects"
    ),
    "Vue": (
        "Developed pages using Vue.js",
        "Built a Vue.js dashboard with {n} dynamic modules, improving data load speed by {pct}%"
    ),
    "Angular": (
        "Used Angular for web development",
        "Developed {n} Angular modules serving {users}+ users, cutting bundle size by {pct}%"
    ),
    "Next.js": (
        "Made a Next.js website",
        "Built a Next.js SSR application that improved SEO score from {low} to {high} and cut load time by {pct}%"
    ),
    "TypeScript": (
        "Wrote code in TypeScript",
        "Migrated {n} JavaScript modules to TypeScript, eliminating {bugs} runtime errors and improving maintainability"
    ),

    # Backend
    "Python": (
        "Did backend work using Python",
        "Developed Python scripts that automated {task}, saving {hrs} hours of manual work per week"
    ),
    "FastAPI": (
        "Built APIs using FastAPI",
        "Designed {n} REST endpoints using FastAPI, reducing average response time from {slow}ms to {fast}ms"
    ),
    "Django": (
        "Used Django for web development",
        "Built a Django web app serving {users}+ users with {n} modules, achieving {pct}% uptime"
    ),
    "Node.js": (
        "Made a backend with Node.js",
        "Built a Node.js backend handling {req}+ concurrent requests, reducing server latency by {pct}%"
    ),
    "Flask": (
        "Created a Flask API",
        "Developed a Flask REST API with {n} endpoints integrated with {db}, serving {users}+ requests daily"
    ),
    "Spring Boot": (
        "Worked on a Spring Boot project",
        "Built {n} Spring Boot microservices handling {req}K+ daily transactions with {pct}% uptime"
    ),
    "GraphQL": (
        "Used GraphQL in the project",
        "Replaced {n} REST endpoints with a GraphQL API, reducing data over-fetching by {pct}% and improving client performance"
    ),

    # Mobile
    "React Native": (
        "Developed a mobile app using React Native",
        "Built a cross-platform React Native app with {n} screens, achieving {rating}/5 rating with {users}+ downloads"
    ),
    "Flutter": (
        "Made a Flutter application",
        "Developed a Flutter app for both iOS and Android with {n} features, reducing crash rate to under {pct}%"
    ),
    "Android": (
        "Worked on Android development",
        "Built an Android app with {n} activities, {users}+ installs, and {rating}/5 Play Store rating"
    ),

    # AI / ML
    "Machine Learning": (
        "Implemented machine learning models",
        "Trained a {model_type} model achieving {pct}% accuracy on {dataset_size}+ samples, outperforming baseline by {gain}%"
    ),
    "Deep Learning": (
        "Used deep learning in the project",
        "Built a CNN model for {task} achieving {pct}% accuracy on {n}K image dataset, {gain}x faster than previous approach"
    ),
    "NLP": (
        "Did NLP work",
        "Developed an NLP pipeline processing {n}K+ documents with {pct}% classification accuracy"
    ),
    "Computer Vision": (
        "Used computer vision techniques",
        "Built a Computer Vision system achieving {pct}% detection accuracy processing {fps} frames per second"
    ),
    "Data Analysis": (
        "Analyzed data using Python",
        "Analyzed dataset of {n}K+ records using Pandas, uncovering {insights} key insights that improved business decisions by {pct}%"
    ),
    "LLM/GenAI": (
        "Used LLMs in the project",
        "Built a RAG pipeline using LLMs that reduced manual document processing time by {pct}% across {n} workflows"
    ),

    # DevOps / Cloud
    "Docker": (
        "Used Docker for deployment",
        "Containerized {n} services using Docker, reducing deployment time from {slow} minutes to {fast} minutes"
    ),
    "AWS": (
        "Deployed application on AWS",
        "Architected AWS infrastructure for {users}K+ users, reducing cloud costs by {pct}% through optimized auto-scaling"
    ),
    "Kubernetes": (
        "Used Kubernetes in deployment",
        "Managed Kubernetes cluster of {n} nodes, achieving {pct}% uptime and cutting incident response time by {gain}%"
    ),
    "CI/CD": (
        "Set up CI/CD pipeline",
        "Built a CI/CD pipeline that reduced deployment time from {slow} hours to {fast} minutes, enabling {n} releases per week"
    ),
    "Linux": (
        "Used Linux for server management",
        "Automated {n} server maintenance tasks using Bash scripts, saving {hrs} hours of DevOps work monthly"
    ),

    # Databases
    "SQL": (
        "Used SQL for database queries",
        "Optimized {n} complex SQL queries, reducing report generation time from {slow} seconds to {fast} seconds"
    ),
    "MongoDB": (
        "Used MongoDB as database",
        "Designed MongoDB schema for {n} collections handling {users}K+ documents with {pct}% faster query performance"
    ),

    # General fallback (role-based)
    "testing": (
        "Wrote tests for the application",
        "Increased test coverage from {low}% to {high}%, catching {bugs} critical bugs before production"
    ),
    "agile": (
        "Worked in an Agile team",
        "Delivered {n} features across {sprints} sprints on time, contributing to {pct}% on-time delivery rate"
    ),
}

# Role keyword → which example key to prefer
_ROLE_TO_EXAMPLE_KEY = {
    "frontend":          "React",
    "react":             "React",
    "vue":               "Vue",
    "angular":           "Angular",
    "backend":           "Node.js",
    "full stack":        "FastAPI",
    "fullstack":         "FastAPI",
    "python":            "Python",
    "node":              "Node.js",
    "mobile":            "React Native",
    "flutter":           "Flutter",
    "android":           "Android",
    "machine learning":  "Machine Learning",
    "ml":                "Machine Learning",
    "ai":                "Machine Learning",
    "data":              "Data Analysis",
    "nlp":               "NLP",
    "devops":            "Docker",
    "cloud":             "AWS",
    "database":          "SQL",
}

import random

def _dynamic_achievement_examples(cv_text: str, jd_text: str, missing_skills: list):
    """
    Pick the most relevant achievement example based on:
    1. Skills found in CV
    2. Role from JD
    Returns (weak_example, strong_example) as strings.
    """
    combined = (cv_text + " " + jd_text).lower()

    # Try to find the best matching example key
    chosen_key = None

    cv_skills = extract_skills(cv_text)
    jd_skills = extract_skills(jd_text)
    cv_and_jd = cv_skills & jd_skills

    # Priority order: most commonly searched roles first
    PRIORITY_ORDER = [
        "React", "Vue", "Angular", "Next.js", "TypeScript", "JavaScript",
        "Node.js", "FastAPI", "Django", "Flask", "Python", "Spring Boot",
        "Machine Learning", "Deep Learning", "NLP", "Data Analysis",
        "React Native", "Flutter", "Android", "iOS/Swift",
        "Docker", "AWS", "Kubernetes", "CI/CD",
        "SQL", "MongoDB", "GraphQL",
    ]

    # First: skills in BOTH cv and jd — most relevant
    for skill in PRIORITY_ORDER:
        if skill in cv_and_jd and skill in _ACHIEVEMENT_EXAMPLES:
            chosen_key = skill
            break

    # Second: role keywords from JD text
    if not chosen_key:
        for role_kw, example_key in _ROLE_TO_EXAMPLE_KEY.items():
            if role_kw in combined and example_key in _ACHIEVEMENT_EXAMPLES:
                chosen_key = example_key
                break

    # Third: any CV skill that has an example
    if not chosen_key:
        for skill in PRIORITY_ORDER:
            if skill in cv_skills and skill in _ACHIEVEMENT_EXAMPLES:
                chosen_key = skill
                break

    # Fallback
    if not chosen_key or chosen_key not in _ACHIEVEMENT_EXAMPLES:
        chosen_key = random.choice(list(_ACHIEVEMENT_EXAMPLES.keys()))

    weak, strong_template = _ACHIEVEMENT_EXAMPLES[chosen_key]

    # Fill in realistic placeholder values
    strong = (strong_template
        .replace("{n}",          str(random.choice([5, 8, 10, 12, 15, 20])))
        .replace("{pct}",        str(random.choice([30, 40, 50, 60, 70])))
        .replace("{users}",      str(random.choice([100, 500, 1000, 5000])))
        .replace("{proj}",       str(random.choice([2, 3, 4, 5])))
        .replace("{hrs}",        str(random.choice([5, 8, 10, 15, 20])))
        .replace("{req}",        str(random.choice([100, 500, 1000, 5000])))
        .replace("{slow}",       str(random.choice([800, 1000, 2000, 5])))
        .replace("{fast}",       str(random.choice([80, 120, 200, 1])))
        .replace("{low}",        str(random.choice([20, 30, 40, 50])))
        .replace("{high}",       str(random.choice([80, 90, 95, 98])))
        .replace("{bugs}",       str(random.choice([10, 15, 20, 30])))
        .replace("{gain}",       str(random.choice([2, 3, 5, 10])))
        .replace("{sprints}",    str(random.choice([3, 4, 5, 6])))
        .replace("{fps}",        str(random.choice([15, 24, 30, 60])))
        .replace("{rating}",     str(round(random.uniform(4.2, 4.9), 1)))
        .replace("{insights}",   str(random.choice([3, 5, 7])))
        .replace("{task}",       "classification")
        .replace("{model_type}", random.choice(["Random Forest", "XGBoost", "SVM", "LSTM"]))
        .replace("{dataset_size}", str(random.choice([5000, 10000, 50000])))
        .replace("{db}",         random.choice(["PostgreSQL", "MongoDB", "MySQL"]))
    )

    return f"'{weak}'", f"'{strong}'"


def _metric_tips_for_role(cv_text: str, jd_text: str) -> list:
    """
    Return role-specific metric tips — what numbers to add for this person's field.
    """
    combined = (cv_text + " " + jd_text).lower()
    cv_skills = extract_skills(cv_text)

    tips = []

    if any(s in cv_skills for s in ["React", "Vue", "Angular", "Next.js", "HTML/CSS"]):
        tips += [
            "Number of components / pages built",
            "Page load time improvement (use Lighthouse score)",
            "Number of users or daily visits to your project",
        ]
    if any(s in cv_skills for s in ["Node.js", "FastAPI", "Django", "Flask", "Python"]):
        tips += [
            "API response time before and after your optimization",
            "Number of endpoints built or requests handled per second",
            "Reduction in server errors or downtime percentage",
        ]
    if any(s in cv_skills for s in ["Machine Learning", "Deep Learning", "NLP", "Computer Vision"]):
        tips += [
            "Model accuracy percentage on test dataset",
            "Dataset size you trained or processed",
            "Improvement over baseline model (e.g. +15% accuracy)",
        ]
    if any(s in cv_skills for s in ["React Native", "Flutter", "Android", "iOS/Swift"]):
        tips += [
            "Number of app downloads or active users",
            "App store rating you achieved",
            "Number of screens or features implemented",
        ]
    if any(s in cv_skills for s in ["Docker", "AWS", "Kubernetes", "CI/CD"]):
        tips += [
            "Deployment time before vs after your pipeline",
            "Infrastructure cost savings percentage",
            "Number of services containerized or automated",
        ]
    if any(s in cv_skills for s in ["SQL", "MongoDB"]):
        tips += [
            "Query performance improvement (e.g. from 5s to 0.3s)",
            "Database size or number of records managed",
        ]

    # Generic fallback tips
    if not tips:
        tips = [
            "Number of projects or features you delivered",
            "Team size you worked with",
            "Time saved through your work (hours per week)",
            "Any performance improvements in percentage",
        ]

    return tips[:4]


# ═══════════════════════════════════════════════════════════════════════════════

def build_smart_suggestions(
    missing_skills: list,
    scores: dict,
    cv_text: str,
    jd_text: str,
    experience_level: str,
    achievement_findings: list,
    missing_ats_phrases: list,
) -> list:
    """
    Generates rich, career-path-aware suggestions with:
    - Specific course recommendations
    - Project ideas
    - Internship guidance
    - Context-aware advice based on experience level
    """
    suggestions = []

    # ── 1. Top missing skill with full career guidance ───────────────────────
    high_skills = [s for s in missing_skills if s.get("priority") == "High"]
    if high_skills:
        top_skill = high_skills[0]["name"]
        guidance = CAREER_GUIDANCE.get(top_skill, DEFAULT_GUIDANCE)

        suggestions.append({
            "title":  f"🎯 Learn {top_skill} — High Priority Skill",
            "impact": "High",
            "desc": (
                f"**{top_skill}** appears as a core requirement in this job. Here's your action plan:\n\n"
                f"📚 **Recommended Courses:**\n"
                + "\n".join(f"  • {c}" for c in guidance["courses"][:2]) +
                f"\n\n💻 **Project Ideas to Build:**\n"
                + "\n".join(f"  • {p}" for p in guidance["projects"][:2]) +
                f"\n\n⏱ **Timeline:** {guidance['timeline']}"
            ),
        })

    # ── 2. Second missing skill (if any) ────────────────────────────────────
    if len(high_skills) >= 2:
        skill2 = high_skills[1]["name"]
        guidance2 = CAREER_GUIDANCE.get(skill2, DEFAULT_GUIDANCE)
        suggestions.append({
            "title":  f"📌 Also Learn {skill2}",
            "impact": "High",
            "desc": (
                f"**{skill2}** is also required. Start after {high_skills[0]['name']}.\n\n"
                f"📚 **Best Resource:** {guidance2['courses'][0]}\n\n"
                f"💻 **Quick Project:** {guidance2['projects'][0]}\n\n"
                f"⏱ **Timeline:** {guidance2['timeline']}"
            ),
        })

    # ── 3. Internship / career path advice ──────────────────────────────────
    if high_skills:
        top_skill = high_skills[0]["name"]
        guidance = CAREER_GUIDANCE.get(top_skill, DEFAULT_GUIDANCE)
        internship_tips = guidance.get("internships", DEFAULT_GUIDANCE["internships"])

        suggestions.append({
            "title":  "🚀 Internship & Career Path Strategy",
            "impact": "High",
            "desc": (
                f"To land a role requiring **{top_skill}** at your {experience_level} level:\n\n"
                f"🎓 **Internship Paths:**\n"
                + "\n".join(f"  • {tip}" for tip in internship_tips[:3]) +
                f"\n\n💡 **Pro Tip:** Build 2–3 projects using {top_skill}, "
                f"push them to GitHub with a good README, then apply. "
                f"Recruiters check GitHub before interviews."
            ),
        })

    # ── 4. Achievement quality — dynamic, field-specific examples ───────────
    no_metrics         = any("no metric" in f.lower() for f in achievement_findings)
    sparse_metrics     = any("1 metric" in f.lower() or "2 metric" in f.lower() for f in achievement_findings)
    achievement_score_val = scores.get("achievements", 70)

    if no_metrics or (sparse_metrics and achievement_score_val < 60):
        bad, good = _dynamic_achievement_examples(cv_text, jd_text, missing_skills)
        severity  = "No Metrics Found" if no_metrics else "Add More Metrics"
        intro     = (
            "Your CV has no measurable achievements. Numbers are what make recruiters stop scanning."
            if no_metrics else
            "You have some numbers — good start! But every bullet needs a metric, not just a few."
        )
        metric_tips = _metric_tips_for_role(cv_text, jd_text)
        suggestions.append({
            "title":  f"📊 Quantify Your Achievements — {severity}",
            "impact": "Medium",
            "desc": (
                f"{intro}\n\n"
                f"**Based on your field, transform your bullets like this:**\n"
                f"  ❌ {bad}\n"
                f"  ✅ {good}\n\n"
                f"**What to measure in your specific role:**\n"
                + "\n".join(f"  • {tip}" for tip in metric_tips) +
                f"\n\n**Formula:** Action Verb + What + How Much Impact"
            ),
        })

    # ── 5. ATS keyword alignment ─────────────────────────────────────────────
    if scores.get("ats", 100) < 60 and missing_ats_phrases:
        phrase_list = ", ".join(f'"{p}"' for p in missing_ats_phrases[:4])
        suggestions.append({
            "title":  "🤖 Improve ATS Keyword Match",
            "impact": "Medium",
            "desc": (
                f"ATS bots filter CVs before a human sees them. Your CV is missing "
                f"key phrases from this job description:\n\n"
                f"  Missing keywords: {phrase_list}\n\n"
                f"**How to fix:**\n"
                f"  • Use the exact same words as the JD (not synonyms)\n"
                f"  • Add a 'Technical Skills' section listing keywords explicitly\n"
                f"  • Mirror the JD language in your experience bullet points\n\n"
                f"  ⚠️ Don't keyword-stuff — only add skills you actually have"
            ),
        })

    # ── 6. Experience-level specific advice ─────────────────────────────────
    if experience_level == "Junior / Entry":
        suggestions.append({
            "title":  "🌱 Entry-Level Strategy: Build Before You Apply",
            "impact": "Medium",
            "desc": (
                "As an entry-level candidate, your GitHub and projects ARE your experience.\n\n"
                "**Your 90-day action plan:**\n"
                "  📅 Month 1: Build 1 complete full-stack project (frontend + backend + DB)\n"
                "  📅 Month 2: Learn the top missing skill from this JD (see above)\n"
                "  📅 Month 3: Apply to 10+ internships daily, do mock interviews weekly\n\n"
                "**Best internship platforms for Pakistan:**\n"
                "  • Rozee.pk → search 'internship software'\n"
                "  • Internshala.com → tech internships\n"
                "  • LinkedIn Easy Apply → filter by 'Internship'\n"
                "  • Local software houses: Arbisoft, Tintash, Systems Ltd, Folio3\n\n"
                "  💡 A strong internship beats a degree on your first CV"
            ),
        })
    elif experience_level == "Mid-level":
        suggestions.append({
            "title":  "⚡ Mid-Level Strategy: Demonstrate Ownership",
            "impact": "Medium",
            "desc": (
                "At mid-level, companies want evidence you can own a feature end-to-end.\n\n"
                "**What to highlight:**\n"
                "  • Features/systems you built independently\n"
                "  • Times you made technical decisions (not just followed them)\n"
                "  • Cross-team collaboration and communication\n"
                "  • Any mentoring of junior developers\n\n"
                "**Certifications that help mid-level developers:**\n"
                "  • AWS Certified Developer Associate\n"
                "  • Google Cloud Professional Developer\n"
                "  • Microsoft Azure Developer Associate"
            ),
        })

    # ── 7. Medium missing skills — study path ───────────────────────────────
    med_skills = [s for s in missing_skills if s.get("priority") == "Medium"]
    if med_skills:
        skill_names = [s["name"] for s in med_skills[:3]]
        resources = []
        for sn in skill_names:
            g = CAREER_GUIDANCE.get(sn, DEFAULT_GUIDANCE)
            resources.append(f"**{sn}:** {g['courses'][0]}")

        suggestions.append({
            "title":  f"📚 Study Plan for Medium-Priority Skills",
            "impact": "Medium",
            "desc": (
                f"These skills ({', '.join(skill_names)}) are mentioned in the JD "
                f"but less critical than the core requirements. Learn them after the high-priority ones.\n\n"
                f"**Quick-start resources:**\n"
                + "\n".join(f"  • {r}" for r in resources)
            ),
        })

    # ── 8. Professional summary coaching ────────────────────────────────────
    sections = extract_sections(cv_text)
    summary_text = sections.get("summary", "")
    if len(summary_text.split()) < 30:
        suggestions.append({
            "title":  "✍️ Write a Powerful Professional Summary",
            "impact": "Medium",
            "desc": (
                "A 3-line summary at the top of your CV is the first thing recruiters read.\n\n"
                "**Formula:**\n"
                "  [Your role] with [X years / fresh graduate] experience in "
                "[your top 2–3 skills]. Passionate about [domain]. "
                "Built [your best project] that [brief impact].\n\n"
                "**Example for a CS student:**\n"
                "  'Computer Science student at University of Mianwali with hands-on "
                "experience in React and FastAPI. Built an AI-powered CV evaluator "
                "processing PDF resumes with NLP. Seeking a frontend/full-stack "
                "internship to contribute to production systems.'"
            ),
        })

    # Sort: High impact first, then Medium — keeps job-specific advice at top
    suggestions.sort(key=lambda s: 0 if s["impact"] == "High" else 1)

    return suggestions[:6]  # Return max 6 rich suggestions


# ═══════════════════════════════════════════════════════════════════════════════
# 11.  STRENGTHS & WEAKNESSES  (context-aware)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_strengths(cv_text, matched_skills, scores, experience_level, achievement_findings):
    strengths = []

    if len(matched_skills) >= 8:
        strengths.append(f"Excellent skill alignment — {len(matched_skills)} skills match the job requirements")
    elif len(matched_skills) >= 4:
        strengths.append(f"Solid skill coverage with {len(matched_skills)} matching skills")

    for f in achievement_findings:
        if "good" in f.lower() or "excellent" in f.lower() or "strong" in f.lower():
            strengths.append(f)

    if scores.get("education", 0) >= 75:
        strengths.append("Educational background aligns well with the role")

    if scores.get("ats", 0) >= 65:
        strengths.append("Good ATS keyword density — your CV should pass automated screening")

    if experience_level == "Senior":
        strengths.append("Senior-level experience signals detected — leadership and ownership cues present")

    sections = extract_sections(cv_text)
    if "projects" in sections and len(sections["projects"].split()) > 50:
        strengths.append("Projects section demonstrates practical, hands-on experience")

    if "certs" in sections and len(sections["certs"].split()) > 10:
        strengths.append("Certifications present — shows commitment to continuous learning")

    return strengths[:5] or ["Resume is present — add more specific details for a stronger profile"]


def generate_weaknesses(missing_skills, scores, cv_text, achievement_findings, missing_ats_phrases):
    weaknesses = []

    high_missing = [s for s in missing_skills if s.get("priority") == "High"]
    if high_missing:
        names = ", ".join(s["name"] for s in high_missing[:3])
        weaknesses.append(f"Missing high-priority skills required by this role: {names}")

    for f in achievement_findings:
        if "no metric" in f.lower() or "needed" in f.lower() or "very short" in f.lower():
            weaknesses.append(f)

    if scores.get("ats", 100) < 55:
        phrases = ", ".join(f'"{p}"' for p in missing_ats_phrases[:3])
        weaknesses.append(f"Low ATS keyword match — JD phrases not found in CV: {phrases}")

    sections = extract_sections(cv_text)
    if len(sections.get("summary", "").split()) < 20:
        weaknesses.append("Professional summary is missing or too brief — add a 2–3 line summary")

    if scores.get("experience", 0) < 55:
        weaknesses.append("Work experience content doesn't closely match the job description language")

    return weaknesses[:5] or ["No critical weaknesses detected — focus on the suggestions to improve your score"]


# ═══════════════════════════════════════════════════════════════════════════════
# 12.  MAIN ANALYSIS FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_cv(cv_text: str, job_role: str, job_description: str) -> dict:
    """
    Full intelligent analysis pipeline.
    Returns structured JSON matching the frontend schema.
    """

    # — Skill extraction (ontology-aware) —
    cv_skills  = extract_skills(cv_text)
    jd_skills  = extract_skills(job_description)
    role_skills = extract_skills(job_role)
    all_target = jd_skills | role_skills

    matched = sorted(cv_skills & all_target)
    raw_missing = sorted(all_target - cv_skills)

    # Prioritise missing by JD mention frequency
    jd_lower = job_description.lower()
    def priority(skill):
        # Check all variants of the skill
        variants = SKILL_ONTOLOGY.get(skill, [skill.lower()])
        mentions = sum(
            len(re.findall(r"\b" + re.escape(v) + r"\b", jd_lower))
            for v in variants
        )
        if mentions >= 3: return "High"
        if mentions >= 1: return "Medium"
        return "Low"

    missing_skills = sorted(
        [{"name": s, "priority": priority(s)} for s in raw_missing],
        key=lambda x: {"High": 0, "Medium": 1, "Low": 2}[x["priority"]]
    )

    # Pad matched if too sparse
    if len(matched) < 3:
        extra = sorted(cv_skills - all_target)[:5]
        matched = matched + extra

    # — Section-level analysis —
    sections = extract_sections(cv_text)
    edu_score, edu_notes = score_education_section(
        sections.get("education", cv_text), job_description
    )

    # — Experience level —
    exp_level, exp_score, exp_explanation = detect_experience_level(cv_text)

    # — Achievement quality —
    achievement_score, achievement_findings = score_achievements(cv_text)

    # — Semantic similarity (PMI + TF-IDF blend) —
    similarity = pmi_similarity(cv_text, job_description)
    experience_score_computed = round(40 + similarity * 55)
    experience_score_final = round((experience_score_computed + exp_score) / 2)
    experience_score_final = min(100, max(20, experience_score_final))

    # — Smart ATS —
    ats_raw, missing_ats_phrases = smart_ats_score(cv_text, job_description)

    # — Skills match score —
    if all_target:
        skills_score = round((len(cv_skills & all_target) / len(all_target)) * 100)
        skills_score = min(100, max(30, skills_score))
    else:
        skills_score = 60

    # — Format score —
    fmt_score = round(achievement_score * 0.6 + (
        min(100, 50 + len(sections) * 8)  # section richness
    ) * 0.4)

    scores = {
        "skills":       skills_score,
        "experience":   experience_score_final,
        "education":    edu_score,
        "ats":          ats_raw,
        "format":       fmt_score,
        "achievements": achievement_score,
    }

    # — Weighted overall score —
    weights = {
        "skills": 0.28, "experience": 0.25, "education": 0.12,
        "ats": 0.20, "format": 0.15,
    }
    overall = round(sum(scores[k] * w for k, w in weights.items()))

    # — Strengths & weaknesses —
    strengths = generate_strengths(
        cv_text, matched, scores, exp_level, achievement_findings
    )
    weaknesses = generate_weaknesses(
        missing_skills, scores, cv_text, achievement_findings, missing_ats_phrases
    )

    # — Smart suggestions with career guidance —
    suggestions = build_smart_suggestions(
        missing_skills=missing_skills,
        scores=scores,
        cv_text=cv_text,
        jd_text=job_description,
        experience_level=exp_level,
        achievement_findings=achievement_findings,
        missing_ats_phrases=missing_ats_phrases,
    )

    return {
        "overallScore":    overall,
        "jobRole":         job_role,
        "experienceLevel": exp_level,
        "categories": [
            {"name": "Skills Match",     "score": scores["skills"],     "color": "#2563EB"},
            {"name": "Experience",       "score": scores["experience"],  "color": "#7C3AED"},
            {"name": "Education",        "score": scores["education"],   "color": "#10B981"},
            {"name": "ATS Keywords",     "score": scores["ats"],         "color": "#F59E0B"},
            {"name": "Format & Clarity", "score": scores["format"],      "color": "#EF4444"},
        ],
        "matchedSkills":  matched[:15],
        "missingSkills":  missing_skills[:8],
        "strengths":      strengths,
        "weaknesses":     weaknesses,
        "suggestions":    suggestions,
    }
