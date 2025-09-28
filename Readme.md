# 🗺️ AI-Roadmap-Generator

**AI-Roadmap-Generator** is an intelligent tool that generates personalized AI learning roadmaps by analyzing GitHub profiles and leveraging state-of-the-art AI models. This project is designed to help developers, students, and professionals identify skill gaps, explore market trends, and plan their learning journey efficiently.

---
## Live Preview
https://ai-project-roadmap-generator.vercel.app/

---

## ✨ Features

- **🔍 GitHub Profile Analysis:**  
  Analyze any GitHub profile to extract skills, project experience, and coding activity.

- **🧠 Personalized AI Learning Paths:**  
  Generate tailored AI learning roadmaps based on user profiles and current AI industry trends.

- **🌐 Market Context Awareness:**  
  Integrate up-to-date market context to ensure roadmaps are relevant and future-proof.

- **🤖 Multiple Model Support:**  
  Easily switch between different LLM providers (OpenAI, Google Generative AI).

- **🚀 Simple API:**  
  RESTful endpoints for seamless integration with frontends or other services.

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/manisankarrr/ai-roadmap-generator.git
   cd ai-roadmap-generator
   ```

2. **Set up a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   - Create a `.env` file in the root directory and add your API keys and configuration.  
   - Example:
     ```
     OPENAI_API_KEY=your_openai_api_key
     GOOGLE_API_KEY=your_google_api_key
     ```

---

## 🚦 Usage

1. **Start the backend server**

   ```bash
   cd backend
   python app.py
   ```

2. **Send a request to generate a roadmap**

   - Use Postman, curl, or connect via a frontend.
   - Example `curl` request:
     ```bash
     curl -X POST http://localhost:5000/generate-roadmap \
          -H "Content-Type: application/json" \
          -d '{"github_username": "octocat"}'
     ```

3. **Receive a personalized AI roadmap in the response!**

---
## Docker

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```

2.  **Build the Docker image:**
    ```bash
    docker build -t ai-roadmap-generator .
    ```
    (This command tells Docker to build an image, name (`-t`) it `ai-roadmap-generator`, and use the `Dockerfile` in the current directory (`.`))

3.  **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 -v .:/app ai-roadmap-generator
    


## 🤝 Contributing

Contributions are welcome!  
To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

**Happy learning! 🚀**

## License
This project is licensed under the **MIT** License.

---
🔗 GitHub Repo: https://github.com/Manisankarrr/ai-roadmap-generator