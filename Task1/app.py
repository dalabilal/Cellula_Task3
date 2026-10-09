import os
import csv
import datetime
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_classic.vectorstores import FAISS
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate

load_dotenv()

# the folder where app.py is (so the app finds faiss_index even if it runs from another folder)
app_folder = os.path.dirname(os.path.abspath(__file__))

# api key : from streamlit secrets (when deployed) or from .env (on my laptop)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = os.getenv("OPENAI_API_KEY")


model_name = "openrouter/free"


# load everything one time only (so the app is fast)
@st.cache_resource
def load_everything():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorDB = FAISS.load_local(
        os.path.join(app_folder, "faiss_index"),
        embeddings,
        allow_dangerous_deserialization=True
    )

    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model=model_name,
        temperature=0
    )

    return vectorDB, llm


vectorDB, llm = load_everything()


# prompt template
temp = """
you are assistant that answer questions about one person, Answer the next Question using provided context only,
If the answer is not in the context, just say you don't know.
don't guess and don't use any information outside the context.
use the previous conversation only to understand the question (like "she" or "that project").
answer should be within 200 words or lower only
at the end write the sources you used

## context :
{context}

## Previous conversation :
{history}

## Question :
{Question}
"""

temp = PromptTemplate.from_template(temp)


# questions that we suggest to the user (change them to match your files)
suggested_questions = [
    "What are Dalah's technical skills?",
    "What is Dalah's education?",
    "Did Dalah participate in the AI Hackathon U-TEACH LEAGUE?",
    "What is the toxic content classification project about?",
    "What is Dalah's Olist Delivery Delay Prediction?",
    "Where has Dalah worked or interned?",
]


# save every question in a csv file
def save_question(question, found):
    log_file = os.path.join(app_folder, "questions_log.csv")
    new_file = not os.path.exists(log_file)
    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["time", "question", "found_answer"])
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), question, found])


# when the user click on a question button, put it in the text box
def set_query(question):
    st.session_state.query = question


# clear the conversation (memory + previous questions)
def clear_chat():
    st.session_state.memory = ConversationBufferMemory()
    st.session_state.history = []
    st.session_state.last_saved = ""
    st.session_state.last_response = ""
    st.session_state.last_sources = []
    st.session_state.query = ""


# memory of the page
if "query" not in st.session_state:
    st.session_state.query = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "last_saved" not in st.session_state:
    st.session_state.last_saved = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "last_sources" not in st.session_state:
    st.session_state.last_sources = []
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()


# the sidebar : previous questions
st.sidebar.header("Previous questions")

if len(st.session_state.history) == 0:
    st.sidebar.write("no questions yet")

for n, q in enumerate(reversed(st.session_state.history)):
    st.sidebar.button(q, key="history_" + str(n), on_click=set_query, args=(q,))

st.sidebar.button("Clear conversation", on_click=clear_chat)


# the page
st.title("Ask me about Dalah")
st.write("Type a question and the answer will appear below. You can also ask follow-up questions.")

st.write("Not sure what to ask? Try one of these :")
for n, q in enumerate(suggested_questions):
    st.button(q, key="suggest_" + str(n), on_click=set_query, args=(q,))

query = st.text_input("Your question", key="query")

if query:

    if query != st.session_state.last_saved:
        with st.spinner("thinking..."):

            search_text = query
            if st.session_state.last_saved != "":
                search_text = st.session_state.last_saved + " " + query

            similar_docs = vectorDB.similarity_search_with_score(search_text, k=4)

            context = []
            sources = []

            for i in similar_docs:
                if i[1] < 1.4:
                    context.append("[source: " + i[0].metadata["source"] + "]\n" + i[0].page_content)
                    sources.append(i[0].metadata["source"])

            if len(context) == 0:
                response = "I couldn't find that in my sources"
            else:
                history_text = st.session_state.memory.load_memory_variables({})["history"]

                prompt = temp.format(
                    context="\n\n".join(context),
                    history=history_text,
                    Question=query
                )

                for attempt in range(3):
                    response = llm.invoke(prompt).content
                    if "Safety Categories" not in response and "User Safety" not in response:
                        break
                else:
                    response = "Sorry, the model did not give an answer. Please ask again."

        save_question(query, len(context) > 0)
        st.session_state.memory.save_context({"input": query}, {"output": response})
        st.session_state.last_saved = query
        st.session_state.last_response = response
        st.session_state.last_sources = list(set(sources))
        if query not in st.session_state.history:
            st.session_state.history.append(query)

    st.subheader("Answer")
    st.write(st.session_state.last_response)

    if st.session_state.last_sources:
        st.caption("Sources: " + ", ".join(st.session_state.last_sources))