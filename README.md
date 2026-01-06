# Document Intelligence Assistant

A powerful Streamlit application that transforms your documents into an intelligent chatbot using Docling for document processing and LangGraph for conversational AI.

![Document Intelligence](./images/document-intelligence.png)

## Overview

This application allows you to upload various document formats (PDF, Word, PowerPoint, HTML) and interact with them through a conversational AI interface. It combines IBM's Docling library for advanced document understanding with LangGraph for building sophisticated AI agents.

## Features

### 📄 Multi-Format Document Support

- **PDF documents** - Full text extraction with OCR support
- **Word documents (.docx)** - Complete text and structure preservation
- **PowerPoint presentations (.pptx)** - Slide content extraction
- **HTML files** - Web content processing

### 💬 Intelligent Chat Interface

Ask questions about your documents and get accurate, context-aware answers powered by OpenAI's language models.

![Chat Interface](./images/chatting.png)

### 📊 Document Structure Visualization

Explore your documents in detail with multiple visualization tabs:

![Document Structure](./images/final-tabs.png)

- **Summary** - Overview of pages, tables, images, and content types
- **Hierarchy** - Document outline and heading structure
- **Tables** - Interactive table extraction and display
- **Images** - Picture extraction with captions and positioning

![Docling Visualization](./images/docling-visualized.png)


This version has some the architectural improvements added, such as the **Batching Strategy** (to fix the memory crashes), the **Look-back Overlap** (to fix the cut-off sentences), and the **StateGraph** agent for stability and prolonged conversation.

### 🔍 Advanced Document Processing

- **Batched Memory Management** – Automatically slices large files (via `pypdf`) into memory-safe batches to prevent crashes.
- **Context-Aware Overlap** – Implements "Look-back" logic to preserve semantic meaning across page boundaries.
- **Precise Page Citations** – Tracks and preserves exact page numbers across batches for accurate source referencing.
- **Aggregated Visualization** – Stitches batched data back together for a unified view of document structure, tables, and images.

### 🤖 LangGraph AI Agent

- **StateGraph Architecture** – Built on LangGraph's Core API (`StateGraph`) for robust, explicit control flow.
- **Persistent Memory** – Uses `MemorySaver` checkpoints to maintain deep context across long conversations.
- **Gemini 2.5 Integration** – Optimized for `gemini-2.5-flash` with native handling of structured responses.
- **Streaming Responses** – Real-time token streaming with automatic parsing of tool outputs and citations.

## Installation

### Prerequisites

- Python 3.10 or higher
- Gemini API key, you can modify to use Openai
- onnx graphics run time libraries
```bash
sudo apt-get update && sudo apt-get install -y libgl1 libglib2.0-0 libgomp1
```

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-url>
```

2. Install dependencies (ensure you have UV):

```bash
# Using UV lock file (recommended)
uv sync
```

```bash
# Using attached requirements file: if UV is not available
# If you are using cpu run this first to avoid installation of GPU-based torch
pip install torch==2.5.1+cpu torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu

pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit application:

```bash
un streamlit run app.pyuv r
# or if uv venv is activated or not in used
streamlit run app.py 
python -m streamlit run app.py
```

2. Upload your documents:
   - Click on the file uploader in the sidebar
   - Select one or more documents (PDF, DOCX, PPTX, or HTML)
   - Click "Process & Index" to process the documents

3. Start chatting:
   - Once processing is complete, navigate to the "Chat" tab
   - Ask questions about your documents
   - Get intelligent, context-aware answers

4. Explore document structure:
   - Switch to the "Document Structure" tab
   - Select a document to analyze
   - View detailed information about content, hierarchy, tables, and images

## Project Structure

```
app/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── pyproject.toml              # python dependecy management
├── uv.lock
├── .env.example               # Environment variables template
├── .gitignore                # Git ignore file
└── src/
    ├── __init__.py           # Package initializer
    ├── agent.py              # LangGraph agent configuration
    ├── document_processor.py # Docling document processing
    ├── structure_visualizer.py # Document structure analysis
    ├── tools.py              # Agent tools definition
    └── vectorstore.py        # Vector store management
```

## Key Dependencies

- **docling[rapidocr] (>=2.55.0)** – Advanced document processing, OCR, and structure extraction.
- **langgraph (>=0.2.0)** – State-based agent orchestration with memory persistence (`StateGraph`).
- **langchain-google-genai (>=4.1.2)** – Google Gemini integration for embeddings (`text-embedding-004`) and chat (`gemini-2.5-flash`).
- **langchain-chroma (>=0.1.4)** – Integration for ChromaDB vector storage.
- **pypdf (>=5.0.0)** – PDF manipulation for advanced batch processing and page slicing.
- **streamlit (>=1.32.0)** – Interactive web interface for chat and visualization.
- **langchain (>=0.3.0)** – Core framework for chaining tools and retrieval.
- **pandas (>=2.0.0)** – Data handling for tables and statistics visualization.
- **python-dotenv (>=1.0.0)** – Environment variable management for API keys.

## How It Works

1. **Document Upload**: Users upload documents through the Streamlit interface

2. **Processing with Docling**: Documents are processed using Docling, which:
   - Extracts text with OCR support and table processing
   - Identifies document structure (headings, paragraphs, tables)
   - Preserves layout and formatting
   - Extracts images and their captions

3. **Text Chunking**: Processed documents are split into optimized chunks for better retrieval

4. **Vector Store Creation**: Text chunks are embedded and stored in ChromaDB for semantic search

5. **Agent Creation**: A LangGraph agent is configured with:
   - Access to the vector store through a search tool
   - Conversation memory for context
   - Streaming capabilities for real-time responses

6. **Conversation**: Users interact with the agent, which:
   - Searches the vector store for relevant information
   - Generates contextual answers based on document content
   - Maintains conversation history for follow-up questions

## Production Considerations

For production deployment, consider:

- **Persistent storage** - Use a persistent vector database infrastructure instead of in-memory storage used here
- **Batch processing** - Handle large document collections more efficiently. currently batching for large docyument is implement
- **GPU acceleration** - Speed up OCR and document processing with AI chips or GPU
- **Authentication** - Add user authentication and access controls for security
- **Caching** - Implement caching for processed documents to reduce query cost and scale better
- **Rate limiting** - Add API rate limiting for OpenAI calls to avoid attacks
- **Error handling** - Enhanced error recovery and logging for easy tracing and debugging
- **Monitoring** - Add application monitoring and analytics for realtime app management
- **Framework** - for large-scale consumers, swap streamlit for fast and concurrent backend frameworks like fastapi(Python), Express.js(Node.js), Gin(Go) and React or angular frontend, or a unified framework like Dash, Reflex.

## License

This project is for educational and skill demonstration purpose.

## Acknowledgments

- **Docling** by IBM Research for advanced document understanding
- **LangChain** for the LLM framework
- **LangGraph** for agent orchestration
- **Streamlit** for the web interface
- **OpenAI** for language models
- **Datacamp** and **LangchainAcademy** for tutorial guide and documentation
