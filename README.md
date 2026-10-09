# Cellula Technologies - Introduction to RAG and LangChain (Demo Task)

Author: **Dalah Alhashlamon**

This repository has the two parts of the demo task:

| Task | What it is | Where |
|------|------------|-------|
| Task 0 | Research about the BigBird model | Overleaf link (below) |
| Task 1 | My first RAG application (personal knowledge base) | `Task1/` folder |

---

## Task 0 : Research about the BigBird model

The full research report is in the following Overleaf link:

**[PUT-YOUR-OVERLEAF-LINK-HERE]**

The references are in the [https://www.overleaf.com/read/qntyshcgbgkr#a8c9d2](#references) part at the end of this file.

---

## Task 1 : My first RAG application

A personal Retrieval-Augmented Generation (RAG) system. It builds a knowledge base from my professional information (CV, projects, GitHub READMEs, introduction, capstone files) and answers questions about me using only those sources. Every answer shows the sources it used, and if the answer is not in the sources, the app says it could not find it (so it does not make things up).

### How it works

```
files + links  ->  chunks  ->  embeddings  ->  FAISS vector database
                                                      |
user question  ->  search the closest chunks  <-------+
                          |
          prompt (chunks + previous conversation + question)
                          |
                         LLM  ->  answer + sources
```

1. **Loading:** PDF, txt and md files from the `data` folder, plus GitHub links. Each file name or link is saved as the `source`.
2. **Chunking:** the text is cut into small pieces (200 tokens, overlap 20).
3. **Embedding:** each chunk becomes a vector with `sentence-transformers/all-MiniLM-L6-v2`.
4. **Vector store:** the vectors are saved in FAISS (folder `faiss_index`).
5. **Retrieval:** the question is searched in FAISS. Only chunks that are close enough are kept (the distance must be smaller than `1.4`).
6. **Generation:** the chunks, the previous conversation and the question go into a prompt, and the LLM answers using only that context.

### Features of the app
- Ask a question and the answer appears with its sources
- Suggested questions (buttons) for the user
- Previous questions in the sidebar (click one to ask it again)
- Memory buffer (`ConversationBufferMemory`), so follow-up questions like "where did she study?" work
- "Clear conversation" button
- Every question is saved in `questions_log.csv` (with the time and if an answer was found)
- Light blue buttons

### Project structure

```
Task1/
├── RAG_personal_knowledge_base.ipynb   # notebook: builds the vector database and tests the RAG
├── app.py                              # the Streamlit app
├── requirements.txt                    # packages for the app
├── .gitignore                          # files that must not go to GitHub
├── faiss_index/                        # the saved vector database
│   ├── index.faiss                     #   the vectors
│   └── index.pkl                       #   the chunks text and their sources
├── data/                               # my source files (used by the notebook only)
│   ├── Dalah_Hashlamoon_CE.pdf         #   CV
│   ├── ML & Data Science.pdf           #   course / certificate file
│   ├── intoduction.txt                 #   short introduction about me
│   ├── Capstone-project.md             #   capstone project description
│   └── proposal-of-capstone.md         #   capstone proposal
├── .env                                # my API key (NOT on GitHub)
└── questions_log.csv                   # questions saved by the app (created automatically, NOT on GitHub)
```

What each file is for:

| File / folder | What it does |
|---------------|--------------|
| `RAG_personal_knowledge_base.ipynb` | Loads the files and links, chunks, embeds, saves the FAISS database, and lets me test questions. Run it again whenever I change the data. |
| `app.py` | The Streamlit page. It loads `faiss_index`, searches, builds the prompt, calls the LLM and shows the answer and sources. |
| `requirements.txt` | The packages the app needs (used locally and by Streamlit Cloud). |
| `faiss_index/` | The vector database created by the notebook. The app reads it, so it must be next to `app.py`. |
| `data/` | The documents of the knowledge base. Only the notebook reads them. |
| `.env` | Holds `OPENAI_API_KEY` for local use. Never upload it. |
| `.gitignore` | Keeps `.env`, secrets and `questions_log.csv` out of GitHub. |
| `questions_log.csv` | The saved questions. On Streamlit Cloud it is erased when the app restarts. |

### How to run it

**1. Get the code**
```bash
git clone <PUT-YOUR-REPO-LINK-HERE>
cd <repo-name>/Task1
```

**2. Create the virtual environment (venv)**

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\activate
```

When it works, you see `(.venv)` at the start of the terminal line. Python 3.11 or 3.12 is recommended.

**3. Install the packages**
```bash
pip install -r requirements.txt
```
The first install takes some minutes because `sentence-transformers` is big.

If you want to run the notebook too, install these extra packages:
```bash
pip install pypdf beautifulsoup4 ipykernel
```

**4. Add the API key**

Create a file named `.env` inside `Task1/` with this line (the key is from [OpenRouter](https://openrouter.ai)):
```
OPENAI_API_KEY=your-key-here
```

**5. Build the vector database (notebook)**

Open `RAG_personal_knowledge_base.ipynb`, choose the `.venv` kernel, and run the cells from top to bottom. Put the files in the `data/` folder first. This creates the `faiss_index/` folder.
If you didn't change any data, you can skip this step because `faiss_index/` is already in the repo.

**6. Run the app**
```bash
streamlit run app.py
```
It opens in the browser at `http://localhost:8501`.

### Change the data or the links
1. Add or change files in `data/` (or edit the `links` list in the notebook).
2. Run the notebook again to rebuild `faiss_index/`.
3. Restart the app.

### Deploy on Streamlit Community Cloud

Live app: **[https://cellulatask3-9b3zrsnbh5kgj62sfkc5bd.streamlit.app/]**

### Notes
- LinkedIn does not allow reading a profile from a link, so the LinkedIn information is added from a file exported from my own profile.
- The app uses a free model from OpenRouter. If answers fail, wait a minute because free models have rate limits.
- The `faiss_index/` folder has the text of my files, so don't put private information (phone, address) in the source files if the repo is public.


