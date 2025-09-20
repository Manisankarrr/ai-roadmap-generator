import chromadb
import chromadb.utils.embedding_functions

# This dictionary is our expert knowledge. It's the "A" in RAG.
JOB_ROLES_KNOWLEDGE = {
    "backend": "For backend roles, employers seek skills in cloud services (AWS, GCP), containerization (Docker, Kubernetes), database management (SQL, NoSQL), and building scalable RESTful APIs.",
    "frontend": "For frontend roles, demand is high for modern JavaScript frameworks (React, Vue), state management tools (Redux), and experience with build tools like Vite or Webpack.",
    "ai_ml": "For AI/ML roles, key skills include Python, frameworks like PyTorch or TensorFlow, understanding of MLOps, and deploying models as APIs.",
    "data_science": "For Data Science roles, skills in data analysis, statistical modeling, data visualization, and libraries like Pandas and Scikit-learn are essential.",
    "devops": "For DevOps, skills in CI/CD (Jenkins, GitHub Actions), infrastructure as code (Terraform), and container orchestration (Kubernetes) are critical.",
    "fullstack": "For Fullstack roles, a mix of frontend and backend skills is required, including a primary web framework, database skills, and deployment knowledge."
}

# Setup the vector database client
client = chromadb.Client()
sentence_transformer_ef = chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
collection = client.create_collection(
    name="job_roles_knowledge",
    embedding_function=sentence_transformer_ef
)

def setup_knowledge_base():
    """Loads our expert knowledge into the ChromaDB collection."""
    print("Setting up the knowledge base with ChromaDB...")
    ids = list(JOB_ROLES_KNOWLEDGE.keys())
    documents = list(JOB_ROLES_KNOWLEDGE.values())
    collection.add(documents=documents, ids=ids)
    print("Knowledge base setup complete.")

def get_market_context(career_goal: str) -> str:
    """Performs a semantic search to find the most relevant job role info."""
    results = collection.query(query_texts=[career_goal], n_results=1)
    if not results['documents'][0]:
        # Fallback if no results are found
        return "General software engineering principles are always in demand."
    return results['documents'][0][0]

