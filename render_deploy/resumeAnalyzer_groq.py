from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import json, re, os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY").strip()
)

class State(TypedDict):
    resume_text: str
    job_description: str
    parsed_resume: dict
    parsed_jd: dict
    matching_skills: list
    missing_skills: list
    match_score: int
    final_output: dict

def extract_json(text):
    """Extract JSON from LLM response, handling various formats"""
    try:
        # Try direct JSON parse first
        return json.loads(text)
    except:
        pass

    try:
        # Extract JSON from markdown code blocks
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except:
        pass

    try:
        # Extract any JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"JSON extraction failed: {e}")
        print(f"Text was: {text[:200]}...")

    return {}

def normalize(s):
    """Normalize skill names for better matching."""
    s = s.lower().strip()
    # Remove common punctuation and standardize spacing
    s = s.replace(".", "").replace("/", " ").replace("-", " ")
    # Collapse multiple spaces
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# =========================
# FIX 1: Bidirectional synonym groups
# Instead of key→values, use flat synonym GROUPS.
# If ANY skill in a group matches ANY other, they're considered equivalent.
# =========================
SKILL_GROUPS = [
    {"git", "github", "gitlab", "version control", "source control", "vcs"},
    {"sql", "postgresql", "postgressql", "mysql", "sql queries", "database",
     "oracle", "oracle database", "mssql", "sql server"},
    {"aws", "aws lambda", "lambda", "ec2", "aws ec2", "s3", "aws s3",
     "emr", "aws emr", "amazon web services", "sqs", "aws sqs", "sns", "aws sns"},
    {"spark", "pyspark", "sparksql", "apache spark"},
    {"etl", "etl pipeline", "etl tools", "informatica", "data pipeline"},
    {"cloud", "aws", "azure", "gcp", "google cloud"},
    {"rest api", "rest apis", "restful api", "api", "rest", "restful",
     "api development", "api design", "web api", "web apis"},
    {"soap api", "soap apis", "soap", "api development", "web services"},
    {"bulk api", "bulk apis"},
    {"ci cd", "ci cd pipelines", "cicd", "devops", "jenkins", "github actions"},
    {"python", "python3", "python 3"},
    {"nodejs", "node js", "node"},
    {"expressjs", "express js", "express"},
    {"javascript", "js", "ecmascript"},
    {"typescript", "ts"},
    {"react", "reactjs"},
    {"angular", "angularjs"},
    {"vue", "vuejs"},
    {"microservices", "microservices architecture", "microservice",
     "distributed systems", "service oriented architecture", "soa"},
    {"event driven", "event driven architecture", "event driven systems",
     "messaging", "async messaging", "pub sub", "publish subscribe"},
    {"message queues", "message queue", "messaging", "kafka", "rabbitmq",
     "activemq", "sqs", "aws sqs", "azure service bus"},
    {"automation", "automation frameworks", "test automation", "automated testing",
     "automation tools", "process automation"},
    {"rpa", "rpa tools", "robotic process automation", "uipath", "automation anywhere",
     "blue prism", "power automate"},
    {"workflow", "workflow engines", "workflow automation", "orchestration",
     "apache airflow", "airflow", "node red"},
    {"erp", "erp systems", "enterprise resource planning", "sap", "oracle erp"},
    {"sap", "sap erp", "sap systems"},
    {"billing", "billing systems", "payment systems", "payment processing",
     "invoice", "invoicing"},
    {"fintech", "financial services", "banking", "financial process automation",
     "banking automation", "digital banking"},
    {"databricks", "delta lake"},
    {"data modeling", "entity relationships", "object model", "er diagrams"},
    {"automated testing", "unit testing", "pytest", "test automation",
     "static code scan tools"},
    {"infrastructure as code", "iac", "terraform", "cloudformation",
     "aws cloudformation"},
    {"salesforce", "sfdc", "salesforce crm"},
    {"gdpr", "ccpa", "data protection regulations", "data governance",
     "metadata management"},
    {"docker", "containerization", "containers"},
    {"kubernetes", "k8s"},
    {"mongodb", "mongo"},
    {"redis", "caching"},
]

GENERIC_WORDS = {
    "data", "system", "process", "workflow",
    "large-scale", "performance", "tools", "experience",
    "knowledge", "understanding", "ability"
}

def get_group(skill):
    """Return the full synonym group for a skill, or a set with just the skill."""
    skill = normalize(skill)
    for group in SKILL_GROUPS:
        if skill in group:
            return group
    return {skill}

def skills_match(jd_skill, resume_set):
    """
    FIX 2: Bidirectional matching.
    Check if jd_skill (or any synonym) appears in resume_set,
    OR if any resume skill is a synonym of jd_skill.
    """
    jd_group = get_group(jd_skill)

    # Direct group overlap
    if jd_group & resume_set:
        return True

    # FIX 3: Substring matching for compound skills
    # e.g. resume has "aws", jd has "aws ec2" → match
    # e.g. resume has "spark", jd has "pyspark" → match
    for r_skill in resume_set:
        r_group = get_group(r_skill)
        if jd_group & r_group:
            return True
        # substring: "spark" in "pyspark", "aws" in "aws ec2"
        for js in jd_group:
            for rs in r_group:
                if rs in js or js in rs:
                    return True

    return False

# =========================
# NODE 1: PARSE RESUME
# =========================
def parse_resume(state: State):
    prompt = f"""
You are extracting technical skills from a resume. Extract EVERY skill, tool, technology, framework, and platform mentioned.

CRITICAL INSTRUCTIONS:
- Extract skills from EVERY section including: Technical Skills, Experience bullets, Projects
- Include programming languages, frameworks, databases, cloud platforms, tools
- Extract BOTH explicitly listed skills AND technologies mentioned in experience descriptions
- List each technology/tool separately

Examples of what to extract:
- "Node.js/Express.js" → extract: ["Node.js", "Express.js", "JavaScript"]
- "AWS (Lambda, S3, CloudFront)" → extract: ["AWS", "AWS Lambda", "AWS S3", "CloudFront"]
- "LangChain, LangGraph, RAG" → extract: ["LangChain", "LangGraph", "RAG"]
- "REST APIs, SOAP APIs" → extract: ["REST API", "SOAP API", "API"]
- "MongoDB, MySQL, Redis" → extract: ["MongoDB", "MySQL", "Redis"]

Return ONLY valid JSON with this format (no other text):
{{"skills": ["skill1", "skill2", "skill3", ...]}}

Resume:
{state['resume_text'][:4000]}
"""

    try:
        result = llm.invoke(prompt).content
        parsed = extract_json(result)

        skills = parsed.get("skills", [])
        print(f"\n=== RESUME PARSING ===")
        print(f"Extracted {len(skills)} skills from resume")
        print(f"Sample skills: {skills[:10]}")
        print("======================\n")

        # If no skills extracted, try a fallback keyword extraction
        if not skills or len(skills) < 5:
            print("WARNING: LLM extracted too few skills, using fallback keyword extraction")
            skills = fallback_skill_extraction(state['resume_text'])
            print(f"Fallback extracted {len(skills)} skills")

        return {"parsed_resume": {"skills": skills}}
    except Exception as e:
        print(f"ERROR in parse_resume: {e}")
        # Use fallback
        skills = fallback_skill_extraction(state['resume_text'])
        return {"parsed_resume": {"skills": skills}}

def fallback_skill_extraction(text):
    """Fallback: Extract skills using keyword matching"""
    text_lower = text.lower()

    # Common tech keywords to search for
    keywords = [
        "python", "javascript", "java", "typescript", "node.js", "nodejs", "react",
        "angular", "vue", "express.js", "expressjs", "django", "flask",
        "aws", "azure", "gcp", "lambda", "s3", "ec2", "cloudfront", "api gateway",
        "docker", "kubernetes", "k8s", "jenkins", "ci/cd", "cicd", "git", "github", "gitlab",
        "mongodb", "mysql", "postgresql", "redis", "dynamodb", "sql",
        "rest api", "soap api", "graphql", "microservices", "serverless",
        "langchain", "langgraph", "llm", "ai", "machine learning", "ml", "nlp",
        "rag", "vector database", "faiss", "pinecone", "chroma",
        "html", "css", "bootstrap", "tailwind", "jquery",
        "oauth", "jwt", "authentication", "security",
        "agile", "scrum", "jira", "confluence",
        "linux", "bash", "shell", "powershell",
        "terraform", "cloudformation", "iac",
        "elasticsearch", "kafka", "rabbitmq", "message queue",
        "prometheus", "grafana", "monitoring", "logging",
        "swagger", "openapi", "postman"
    ]

    found_skills = []
    for keyword in keywords:
        # Check for exact word match or partial match
        pattern = r'\b' + re.escape(keyword.replace('.', r'\.?')) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            found_skills.append(keyword)

    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in found_skills:
        skill_normalized = normalize(skill)
        if skill_normalized not in seen:
            seen.add(skill_normalized)
            unique_skills.append(skill)

    return unique_skills

# =========================
# NODE 2: PARSE JD
# =========================
def parse_jd(state: State):
    prompt = f"""
Extract ONLY individual technical skills from this job description.

RULES:
- No sentences or phrases
- Split combined skills: "Python/SQL/AWS" → ["python", "sql", "aws"]
- Keep exact tool names (e.g. "aws s3", "pyspark")
- No generic words like "experience", "knowledge", "understanding"

Return ONLY valid JSON, no extra text:
{{"required_skills": ["python", "sql", "aws s3", ...]}}

Job Description:
{state['job_description']}
"""
    result = llm.invoke(prompt).content
    return {"parsed_jd": extract_json(result)}

# =========================
# NODE 3: MATCH SKILLS (fixed)
# =========================
def match_skills(state: State):
    resume_raw = [normalize(s) for s in state["parsed_resume"].get("skills", [])]
    jd_raw = [normalize(s) for s in state["parsed_jd"].get("required_skills", [])]

    print(f"\n=== SKILL MATCHING ===")
    print(f"Resume skills ({len(resume_raw)}): {resume_raw[:20]}")
    print(f"JD skills ({len(jd_raw)}): {jd_raw[:20]}")

    # Remove noise from JD
    jd_cleaned = [s for s in jd_raw if s not in GENERIC_WORDS and len(s) > 1]
    print(f"JD cleaned ({len(jd_cleaned)}): {jd_cleaned[:20]}")

    resume_set = set(resume_raw)

    matching, missing = [], []

    for skill in jd_cleaned:
        if skills_match(skill, resume_set):
            matching.append(skill)
        else:
            missing.append(skill)

    matching = sorted(set(matching))
    missing = sorted(set(missing))

    print(f"Matching skills: {len(matching)}")
    print(f"Missing skills: {len(missing)}")
    print("======================\n")

    # Scoring: weighted by core skills
    CORE = {"python", "sql", "aws", "api", "spark", "etl", "git",
            "version control", "ci/cd", "databricks", "node", "react"}

    core_match = [s for s in matching if any(c in s for c in CORE)]
    total = len(jd_cleaned) if jd_cleaned else 1

    # Weighted formula: core skills count double
    score = int(
        (len(core_match) * 2 + len(matching)) / (total + 1) * 100
    )
    score = min(score, 95)

    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "match_score": score
    }

# =========================
# NODE 4: FINAL OUTPUT
# =========================
def generate_output(state: State):
    missing_skills = state['missing_skills']

    # If no missing skills, return empty suggestions
    if not missing_skills or len(missing_skills) == 0:
        return {"final_output": {"suggestions": []}}

    prompt = f"""
You are a career advisor helping candidates improve their job applications.

Match Score: {state['match_score']}%

Matched Skills: {', '.join(state['matching_skills'])}
Missing Skills: {', '.join(missing_skills)}

For EACH missing skill, provide:
1. The skill name
2. A specific, actionable suggestion to acquire it (online course, project, certification, etc.)
3. Selection impact: "high", "medium", or "low"

You MUST return valid JSON with this EXACT format (no extra text):
{{
  "suggestions": [
    {{"skill": "kubernetes", "action": "Complete the Kubernetes official tutorial or a Udemy course", "selection_chance": "high"}},
    {{"skill": "docker", "action": "Practice containerizing your Node.js projects", "selection_chance": "high"}}
  ]
}}

Return suggestions for ALL {len(missing_skills)} missing skills.
"""
    try:
        result = llm.invoke(prompt).content
        parsed = extract_json(result)

        # Validate suggestions exist
        if not parsed or "suggestions" not in parsed:
            print(f"WARNING: LLM did not return suggestions. Raw output: {result}")
            # Fallback: create basic suggestions
            parsed = {
                "suggestions": [
                    {
                        "skill": skill,
                        "action": f"Consider taking online courses or working on projects to learn {skill}",
                        "selection_chance": "medium"
                    }
                    for skill in missing_skills[:10]  # Limit to top 10
                ]
            }

        print(f"Generated {len(parsed.get('suggestions', []))} suggestions")
        return {"final_output": parsed}
    except Exception as e:
        print(f"ERROR in generate_output: {e}")
        # Fallback suggestions
        return {
            "final_output": {
                "suggestions": [
                    {
                        "skill": skill,
                        "action": f"Gain experience with {skill} through online courses or hands-on projects",
                        "selection_chance": "medium"
                    }
                    for skill in missing_skills[:10]
                ]
            }
        }

# =========================
# GRAPH
# =========================
graph = StateGraph(State)
graph.add_node("parse_resume", parse_resume)
graph.add_node("parse_jd", parse_jd)
graph.add_node("match_skills", match_skills)
graph.add_node("generate_output", generate_output)

graph.add_edge(START, "parse_resume")
graph.add_edge("parse_resume", "parse_jd")
graph.add_edge("parse_jd", "match_skills")
graph.add_edge("match_skills", "generate_output")
graph.add_edge("generate_output", END)

app_graph = graph.compile()

# =========================
# FASTAPI
# =========================
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import tempfile
import shutil

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving the frontend
from pathlib import Path
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class RequestBody(BaseModel):
    resume_text: str
    job_description: str

def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF or DOCX file"""
    if file_path.lower().endswith('.pdf'):
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return "\n".join([doc.page_content for doc in documents])
    elif file_path.lower().endswith('.docx'):
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        return "\n".join([doc.page_content for doc in documents])
    else:
        raise ValueError("Unsupported file format. Please upload PDF or DOCX.")

@app.post("/analyze")
async def analyze_with_upload(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Analyze resume against job description - Resume file required"""

    # Validate file is provided
    if not resume or not resume.filename:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Resume file is required. Please upload a PDF or DOCX file.")

    # Validate file type
    if not (resume.filename.lower().endswith('.pdf') or resume.filename.lower().endswith('.docx')):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF or DOCX file.")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{resume.filename}") as tmp:
        shutil.copyfileobj(resume.file, tmp)
        tmp_path = tmp.name

    try:
        resume_text = extract_text_from_file(tmp_path)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Failed to process resume file: {str(e)}")
    finally:
        # Clean up temp file
        import os
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Run analysis
    result = app_graph.invoke({
        "resume_text": resume_text,
        "job_description": job_description
    })

    # Debug logging
    print("\n=== ANALYSIS RESULT ===")
    print(f"Match Score: {result['match_score']}")
    print(f"Matching Skills ({len(result['matching_skills'])}): {result['matching_skills']}")
    print(f"Missing Skills ({len(result['missing_skills'])}): {result['missing_skills']}")
    print(f"Analysis: {result['final_output']}")
    print("======================\n")

    return {
        "match_score": result["match_score"],
        "matching_skills": result["matching_skills"],
        "missing_skills": result["missing_skills"],
        "analysis": result["final_output"]
    }

@app.post("/analyze-text")
def analyze_text(data: RequestBody):
    """Text-based analysis - Resume text required"""
    resume_text = data.resume_text.strip()

    # Validate resume text is provided
    if not resume_text:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Resume text is required. Please provide resume content.")

    result = app_graph.invoke({
        "resume_text": resume_text,
        "job_description": data.job_description
    })
    return {
        "match_score": result["match_score"],
        "matching_skills": result["matching_skills"],
        "missing_skills": result["missing_skills"],
        "analysis": result["final_output"]
    }

@app.get("/")
def root():
    """Serve the frontend HTML"""
    from fastapi.responses import FileResponse
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Resume Analyzer API running 🚀", "docs": "/docs"}