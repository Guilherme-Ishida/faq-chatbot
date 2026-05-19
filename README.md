# A-Complete-Medical-Chatbot-with-LLMs-LangChain-Pinecone-Flask-AWS

## Project Overview

This project is an end-to-end Medical Chatbot built using Large Language Models, designed to answer health-related questions in a conversational way. The system leverages a Retrieval-Augmented Generation approach, combining semantic search with generative AI to provide accurate and context-aware responses.

The chatbot integrates multiple technologies: LangChain is used to orchestrate the LLM pipeline, Pinecone serves as a vector database for  similarity search over medical knowledge, and Flask provides a web interface for user interaction. The application is designed to be scalable and production-ready, with support for deployment on AWS using containerization and CI/CD workflows.

Users can ask medical questions in natural language, and the chatbot retrieves relevant information from a knowledge base before generating responses, improving reliability compared to purely generative models. This project demonstrates how to build a full-stack AI application, combining machine learning, backend development, and cloud deployment in a healthcare-focused use case.

# How to run?
### STEPS:

Clone the repository

```bash
git clone https://github.com/KiriaNakahati/A-Complete-Medical-Chatbot-with-LLMs-LangChain-Pinecone-Flask-AWS.git
```
### STEP 01- Create a conda environment after opening the repository

```bash
conda create -n medibot python=3.10 -y
```

```bash
conda activate medibot
```


### STEP 02- install the requirements
```bash
pip install -r requirements.txt
```


### Create a `.env` file in the root directory and add your Pinecone & groq credentials as follows:

```ini
PINECONE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GROQ_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```


```bash
# run the following command to store embeddings to pinecone
python store_index.py
```

```bash
# Finally run the following command
python app.py
```

Now,
```bash
open up localhost:
```


### Techstack Used:

- Python
- LangChain
- Flask
- Groq
- Pinecone
