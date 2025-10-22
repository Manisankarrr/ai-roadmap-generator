import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from prometheus_flask_exporter import PrometheusMetrics  # <-- 1. ADDED IMPORT

from modules.github_analyzer import analyze_github_profile
from modules.knowledge_base import setup_knowledge_base, get_market_context

# --- INITIALIZATION & CONFIGURATION ---
load_dotenv()
app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)  # <-- 2. INITIALIZED METRICS

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env file.")
    exit()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- SETUP KNOWLEDGE BASE ON STARTUP ---
with app.app_context():
    setup_knowledge_base()


def generate_openrouter_completion(prompt):
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3.1:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content

# --- API ENDPOINT ---
@app.route('/generate_roadmap', methods=['POST'])
def generate_roadmap_endpoint():
    print("Received request for a V10 strategic roadmap.")
    data = request.get_json()
    if not data or 'github_url' not in data or 'career_goal' not in data:
        return jsonify({'error': 'Missing required fields: github_url and career_goal'}), 400

    github_url = data['github_url']
    career_goal = data['career_goal']
    preferred_stack = data.get('preferred_stack', '')

    try:
        # --- RAG PIPELINE ---
        github_data = analyze_github_profile(github_url)
        market_context = get_market_context(career_goal)

        # --- NEW, V10 "DYNAMIC MENTOR" PROMPT ---
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

        response_text = generate_openrouter_completion(prompt)

        print("Strategic roadmap generated successfully.")
        return jsonify({'roadmap': response_text})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

# --- METRICS & HEALTHCHECK ---

@app.route('/health')  # <-- 4. ADDED HEALTH ENDPOINT
def health():
    return "OK", 200

# --- RUN THE APP ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)