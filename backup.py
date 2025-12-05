import gradio as gr
import chromadb
import os
import uuid
import time
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# --- CONFIGURATION ---
load_dotenv()

# 1. Setup Gemini & Check Models
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in .env.")
else:
    genai.configure(api_key=api_key)
    
    print("\n--------- DEBUG: AVAILABLE MODELS ---------")
    try:
        # This will list what your API key can actually see
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Found: {m.name}")
    except Exception as e:
        print(f"⚠️ Error listing models: {e}")
    print("-------------------------------------------\n")

# 2. Setup ChromaDB
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "roadmap_db")
try:
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name="project_roadmaps")
    print(f"✅ ChromaDB initialized at: {db_path}")
except Exception as e:
    print(f"❌ ChromaDB Init Error: {e}")

# --- REAL ANALYSIS FUNCTIONS ---

def analyze_github_profile(url):
    """
    Fetches real repository data using the provided GITHUB_TOKEN.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not url or "github.com" not in url:
        return "No valid GitHub URL provided."
    
    if not token:
        return "⚠️ GITHUB_TOKEN missing in .env file. Cannot fetch real data."

    try:
        username = url.rstrip("/").split("/")[-1]
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        api_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            repos = response.json()
            repo_summaries = []
            languages = set()
            
            for repo in repos:
                lang = repo.get('language', 'Unknown')
                if lang: languages.add(lang)
                repo_summaries.append(f"- {repo['name']} ({lang}): {repo.get('description', 'No description')}")
            
            return f"User: {username}\nTop Languages: {', '.join(languages)}\nRecent Repos:\n" + "\n".join(repo_summaries)
        else:
            return f"Failed to fetch GitHub data. Status: {response.status_code}"
            
    except Exception as e:
        return f"Error analyzing GitHub: {str(e)}"

def get_market_context(goal):
    """
    Mock logic for market context.
    """
    return f"Current market analysis for '{goal}' indicates high demand for scalable architecture, cloud-native deployments (AWS/Azure), and integration with AI/LLM services."

# --- MAIN LOGIC ---

def generate_roadmap_endpoint(github_url, career_goal, preferred_stack):
    print("Received request for a V10 strategic roadmap.")
    
    if not github_url or not career_goal:
        return "⚠️ Error: Missing required fields: GitHub URL and Career Goal"

    # 1. Check ChromaDB Cache
    search_query = f"{career_goal} | {preferred_stack}"
    try:
        results = collection.query(query_texts=[search_query], n_results=1)
        if results['documents'] and results['documents'][0]:
            distance = results['distances'][0][0]
            if distance < 0.2:
                print(f"✅ Cache Hit! Distance: {distance}")
                return f"**[Loaded from Database Cache]**\n\n{results['documents'][0][0]}"
    except Exception as e:
        print(f"DB Read Error: {e}")

    # 2. RAG Pipeline
    github_data = analyze_github_profile(github_url)
    market_context = get_market_context(career_goal)

    # 3. V10 DYNAMIC MENTOR PROMPT
    prompt = f"""
    **Situation:**
    You are an expert AI Tech Mentor and Career Analyst. Your primary task is to generate a project roadmap that is precisely tailored to any specific career goal a user provides.

    **CRITICAL INSTRUCTIONS (Follow this logic precisely):**
    1.  **Dynamically Analyze the Career Goal to Define Project Scope:** This is your most important task. Do not rely on a fixed list of jobs. Instead, deconstruct the user's stated career goal into its core technical components and propose a project that logically combines them.
        - **Example 1:** If the goal is 'Cloud Security Engineer', you should identify 'Cloud' and 'Security' as the core components. The project scope must therefore be about 'Cloud Security Automation', like building a tool to audit AWS security policies.
        - **Example 2:** If the goal is 'Game Developer with a focus on Physics Engines', you identify 'Game Development' and 'Physics'. The project scope must be 'Game Physics Simulation', not a full-stack web app.
        - **Example 3:** If the goal is just 'Backend Developer', the project scope should be 'Backend-focused API'.
        - You MUST state the determined scope in the 'Project Scope' field.
    2.  **PRIORITY #1 - Career Goal:** The final project idea MUST be directly relevant to the user's stated '[Stated Career Goal]'.
    3.  **PRIORITY #2 - Preferred Tech Stack:** The 'Tech Stack' section MUST be primarily based on the user's '[Preferred Tech Stack]'. Synthesize it intelligently with their GitHub skills.
    4.  **PRIORITY #3 - GitHub Analysis:** Use the '[GitHub Analysis]' for supplementary insights. For example, if they have used 'Docker', suggest containerizing the application.
    5.  **NEGATIVE CONSTRAINT:** You MUST NOT suggest a project related to 'roadmap generation' or 'career coaching'. Propose a completely new, unrelated idea.
    6.  **FORMATTING:** The entire output MUST be in plain text and follow the specified `Output Format` exactly.

    --- DEVELOPER PROFILE ---
    [GitHub Analysis of Existing Projects]:
    {github_data}

    [Stated Career Goal]:
    {career_goal}

    [Preferred Tech Stack (MUST BE PRIORITIZED)]:
    {preferred_stack if preferred_stack else "Not provided."}

    [Current Market Context for this Goal]:
    {market_context}
    --- END PROFILE ---

    **Task:**
    Synthesize all the above information according to the priority rules and generate a comprehensive project proposal using the following exact format.

    **Output Format:**
    Title: [Innovative Project Name Aligned With The Career Goal]

    Project Scope: [e.g., Cloud Security Automation, Game Physics Simulation, Backend-focused API]

    Existing Methodology:
    - Current Approach: [Description of a relevant existing system]
    - Limitations: [Challenges or inefficiencies in the current method]

    Tech Stack:
    - [Category 1 e.g., Core Logic]: [Technology based on scope and preferences]
    - [Category 2 e.g., Infrastructure]: [Technology based on scope and preferences]
    - [Category 3 e.g., Testing/Deployment]: [Technology based on scope and preferences]

    Innovative Enhancements:
    - Technological Improvement: [Clear explanation of how this project is an upgrade]
    - Unique Value Proposition: [What makes this project stand out]

    Learning Roadmap:
    - Step 1: [Initial setup relevant to the project scope]
    - Step 2: [Core functionality implementation]
    - Step 3: [Advanced feature development]
    - Step 4: [Testing and deployment relevant to the project scope]

    Enhancements Over Existing Methodology:
    - [Specific upgrade #1]
    - [Specific upgrade #2]
    - [Specific upgrade #3 showing unique innovation]
    """

    try:
        # UPDATED: Changed from gemini-1.5-flash to gemini-2.0-flash as per your debug list
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("🤖 Generating roadmap via Google Gemini (2.0 Flash)...")
        response = model.generate_content(prompt)
        result_text = response.text

        # 4. Save to ChromaDB
        collection.add(
            documents=[result_text],
            metadatas=[{
                "career_goal": career_goal, 
                "stack": preferred_stack,
                "timestamp": str(time.time())
            }],
            ids=[str(uuid.uuid4())]
        )
        
        print("Strategic roadmap generated successfully.")
        return result_text

    except Exception as e:
        print(f"Generation Error: {e}")
        return f"An error occurred: {str(e)}"

# --- GRADIO UI ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="cyan"), title="AI Project Roadmap Generator") as demo:
    
    gr.Markdown(
        """
        # 🚀 AI Project Roadmap Generator
        ### Turn your skills and goals into a tangible, high-impact portfolio project.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            github_input = gr.Textbox(
                label="GitHub Profile URL", 
                placeholder="https://github.com/username",
                info="We'll analyze your top 5 repos using your GitHub Token."
            )
            career_input = gr.Textbox(
                label="Your Career Goal", 
                placeholder="e.g. AI Engineer, Full Stack Developer",
            )
            stack_input = gr.Textbox(
                label="Preferred Tech Stack (Optional)", 
                placeholder="e.g. Python, React, AWS",
            )
            
            submit_btn = gr.Button("Generate My Roadmap", variant="primary", size="lg")
    
    with gr.Row():
        output_area = gr.Markdown(label="Strategic Roadmap Output")

    submit_btn.click(
        fn=generate_roadmap_endpoint,
        inputs=[github_input, career_input, stack_input],
        outputs=[output_area]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)