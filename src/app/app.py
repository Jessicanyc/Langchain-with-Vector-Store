import faiss
import numpy as np
from langchain.chains import OpenAIChain, SequentialChain
from langchain.schema import LangChainConfig
from langchain.skills import LocalSearchSkill, LangChainSkill
from langchain.prompts import LocalSearchPrompt

# Setup OpenAI API
openai_api_key = 'your-openai-api-key'
openai_chain = OpenAIChain(api_key=openai_api_key)

# Load your pre-built FAISS index
faiss_index = faiss.IndexFlatL2(768)  # Assuming 768-dimensional vectors, adjust as needed
# Dummy load function (replace with actual data loading logic)
def load_faiss_index():
    # Here you would load your index and associated data
    pass

# Load data into FAISS (for example purposes)
load_faiss_index()

# Assuming you have a way to retrieve documents from their IDs
documents = {
    0: "What is AI?",
    1: "The history of neural networks",
    2: "Understanding deep learning"
}
# Function to fetch document by FAISS index
def fetch_document_by_index(index):
    return documents.get(index, "Document not found")

# LangChain setup with local vector store search skill
local_search_prompt = LocalSearchPrompt()
local_search_skill = LocalSearchSkill(prompt=local_search_prompt, max_tokens=300)

# Define a custom skill to further process with OpenAI if needed
class OpenAIRefinementSkill(LangChainSkill):
    def run(self, context):
        response = openai_chain.run(
            prompt=f"Question: {context['question']}\nRelated Info: {context['related_info']}\nAnswer:",
            max_tokens=150
        )
        return response

# Combining skills into a sequential chain
#SequentialChain here handles the process in two steps: first, it attempts to fetch the most relevant document from FAISS. 
#It then passes the context (including the question and the related document) to the OpenAIRefinementSkill, which can refine 
# the answer or generate additional content if needed.
sequential_chain = SequentialChain(skills=[local_search_skill, OpenAIRefinementSkill()])

@app.post("/ask/")
async def ask_question(question: str):
    # Convert question to embedding (dummy function, replace with actual model)
    question_embedding = np.random.rand(768).astype('float32')
    
    # Search in FAISS for the closest vector
    D, I = faiss_index.search(np.array([question_embedding]), 1)  # Top 1 nearest neighbor
    closest_doc_index = I[0][0]
    
    # Retrieve the document
    relevant_document = fetch_document_by_index(closest_doc_index)
    
    # Setup context for LangChain
    context = {"question": question, "related_info": relevant_document}

    # Process through the SequentialChain
    final_response = sequential_chain.run(context)

    return {"question": question, "response": final_response, "related_info": relevant_document}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
