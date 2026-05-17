# Document Intelligence Assistant
**Category:** AI & Agents  
**Tech Stack:** Python, Streamlit, Docling, LangGraph, Gemini, ChromaDB, pypdf  
**Status:** Complete  
**Thumbnail:** assets/thumbnail.png
## Overview
A powerful Streamlit application that transforms your documents into an intelligent chatbot using Docling for document processing and LangGraph for conversational AI.

![Document Intelligence](./images/document-intelligence.png)

Upload various document formats (PDF, Word, PowerPoint, HTML) and interact with them through a conversational AI interface. It combines IBM's Docling library for advanced document understanding with LangGraph for building sophisticated AI agents.
## Features
### 📄 Multi-Format Document Support
- **PDF documents** — Full text extraction with OCR support
- **Word documents (.docx)** — Complete text and structure preservation
- **PowerPoint presentations (.pptx)** — Slide content extraction
- **HTML files** — Web content processing
### 💬 Intelligent Chat Interface
Ask questions about your documents and get accurate, context-aware answers powered by Gemini's language models.

![Chat Interface](./images/chatting.png)

### 📊 Document Structure Visualization
Explore your documents in detail with multiple visualization tabs:

![Document Structure](./images/final-tabs.png)

- **Summary** — Overview of pages, tables, images, and content types
- **Hierarchy** — Document outline and heading structure
- **Tables** — Interactive table extraction and display
- **Images** — Picture extraction with captions and positioning
- 
![Docling Visualization](./images/docling-visualized.png)

### 🔍 Advanced Document Processing
- **Batched Memory Management** — Automatically slices large files (via `pypdf`) into memory-safe batches to prevent crashes.
- **Context-Aware Overlap** — Implements "Look-back" logic to preserve semantic meaning across page boundaries.
- **Precise Page Citations** — Tracks and preserves exact page numbers across batches for accurate source referencing.
- **Aggregated Visualization** — Stitches batched data back together for a unified view of document structure, tables, and images.
### 🤖 LangGraph AI Agent
- **StateGraph Architecture** — Built on LangGraph's Core API (`StateGraph`) for robust, explicit control flow.
- **Persistent Memory** — Uses `MemorySaver` checkpoints to maintain deep context across long conversations.
- **Gemini 2.5 Integration** — Optimized for `gemini-2.5-flash` with native handling of structured responses.
- **Streaming Responses** — Real-time token streaming with automatic parsing of tool outputs and citations.
## Project Structure
```
streamlit-based-rag-app-with-docling/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Python dependency management
├── uv.lock                     # UV lock file
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore file
└── src/
    ├── __init__.py             # Package initializer
    ├── agent.py                # LangGraph agent configuration
    ├── document_processor.py   # Docling document processing
    ├── structure_visualizer.py # Document structure analysis
    ├── tools.py                # Agent tools definition
    └── vectorstore.py          # ChromaDB vector store management
```
## Getting Started
### Prerequisites
- Python 3.12 or higher
- Gemini API key
- ONNX graphics runtime libraries:
```bash
sudo apt-get update && sudo apt-get install -y libgl1 libglib2.0-0 libgomp1
```
### Setup
1. Clone the repository:
```bash
git clone https://github.com/Dr-Aniekan-Udo/Streamlit-based-RAG-app-with-Docling.git
cd Streamlit-based-RAG-app-with-Docling
```
2. Install dependencies:
```bash
# Using UV (recommended)
uv sync
# Or using pip (if UV is not available)
# First install CPU-only torch to avoid GPU bloat:
pip install torch==2.5.1+cpu torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```
3. Configure environment:
```bash
cp .env.example .env
```
Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```
## Usage
1. Start the application:
```bash
uv run streamlit run app.py
# Or if UV venv is activated:
streamlit run app.py
```
2. Upload documents:
   - Click the file uploader in the sidebar
   - Select one or more documents (PDF, DOCX, PPTX, or HTML)
   - Click **Process & Index**
3. Start chatting:
   - Once processing is complete, navigate to the **Chat** tab
   - Ask questions about your documents
   - Get intelligent, context-aware answers
4. Explore document structure:
   - Switch to the **Document Structure** tab
   - Select a document to analyze
   - View detailed information about content, hierarchy, tables, and images
## How It Works
1. **Document Upload** — Users upload documents through the Streamlit interface.
2. **Processing with Docling** — Documents are processed using Docling, which:
   - Extracts text with OCR support and table processing
   - Identifies document structure (headings, paragraphs, tables)
   - Preserves layout and formatting
   - Extracts images and their captions
3. **Text Chunking** — Processed documents are split into optimized chunks for better retrieval.
4. **Vector Store Creation** — Text chunks are embedded and stored in ChromaDB for semantic search.
5. **Agent Creation** — A LangGraph agent is configured with:
   - Access to the vector store through a search tool
   - Conversation memory for context
   - Streaming capabilities for real-time responses
6. **Conversation** — Users interact with the agent, which:
   - Searches the vector store for relevant information
   - Generates contextual answers based on document content
   - Maintains conversation history for follow-up questions
## Production Considerations
- **Persistent storage** — Use a persistent vector database instead of in-memory storage
- **Batch processing** — Handle large document collections more efficiently (batched slicing is already implemented)
- **GPU acceleration** — Speed up OCR and document processing with GPU
- **Authentication** — Add user authentication and access controls
- **Caching** — Implement caching for processed documents to reduce query costs
- **Rate limiting** — Add API rate limiting for LLM calls
- **Error handling** — Enhanced error recovery and logging
- **Monitoring** — Add application monitoring and analytics
- **Framework** — For large-scale use, consider FastAPI/Express/Gin backend with React/Angular frontend, or unified frameworks like Dash or Reflex
## License
MIT
## Acknowledgments
- **Docling** by IBM Research for advanced document understanding
- **LangChain** for the LLM framework
- **LangGraph** for agent orchestration
- **Streamlit** for the web interface
- **Google Gemini** for language models
- **DataCamp** and **LangChain Academy** for tutorials and documentation
## Contact
- **Email**: [Aniekan Udo @Gmail](mailto:aniekanetimudo+reachout@gmail.com)
- **LinkedIn**: [Aniekan Udo @Linkedin](https://www.linkedin.com/in/aniekan-etim-udo)
