from langchain_community.text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Load the environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def process_text(text):
    # Initiate text splitter 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 200
    )
    
    # Divide the text into chunks
    chunks = text_splitter.split_documents(text)
    
    # Load the embedding function
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",  # sentence-transformers/all-MiniLM-l6-v2
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}

    )
    
    
    # Convert the txt into embedding for storing knowledge
    knowledge = FAISS(chunks,
        embeddings        
    )
    
    return knowledge


class ChatModel:
    def __init__(self, groq_api_key, model_name):
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        
        self.llm = ChatGroq(self.groq_api_key,
                            model_name=self.model_name)
        
        prompt_template = """
                Use the following piece of context to answer the question asked.
                Please try to provide the answer only based on the context

                {context}
                Question:{question}

                Helpful Answers:
                 """
    
        self.prompt = PromptTemplate(template=prompt_template, 
                                     input_variables=["context", "question"])
