# NLQ2Mongo

- This project leverages Meta's llama-3.1-8b to generate mongodb queries based on natural language inputs provided 
by user. It does this using langgraph and an Agentic workflow by detecting contexts and also stores the generated queries in the database for future usage.
---

## Libraries and Frameworks

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Generative AI Framework**: [Langgraph](https://www.langchain.com/langgraph)
- **Database**: [MongoDB](https://www.mongodb.com/)

---
## Prerequisites

1. **Python 3.9+**
2. **MongoDB Instance** Use MongoDB Compass to access your instance.
3. **API Keys** for LLM services (e.g., OpenAI, Hugging Face).
4. **Guardrails** for validations. 

## Setup

1. Clone the repository:
```bash
git clone https://github.com/walkingtree/xops-nlp-search.git
cd xops-nlp-search
```

2. Create and activate the environment:
```bash
python3 -m venv env
source env/bin/activate # For Linux
./env/Scripts/activate # For Windows
```

3. Install all required dependencies:
```bash 
pip install -r requirements.txt
```

4. Setup Guardrails:
    - Get your API Key here: [Guardrails-AI](https://hub.guardrailsai.com/keys)
    - Run the below in the terminal: 
    ```bash 
        guardrails configure
      ```
    - Set remote inferencing to Yes and diagnostics to No

5. Create .env
- Use the .env.example to create your own .env file
- Add all the keys needed in .env

6. Run the Project 
```bash
python run.py
```
