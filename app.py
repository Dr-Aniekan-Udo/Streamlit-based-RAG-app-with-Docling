"""
Streamlit app for converting documents into a chatbot using Docling and LangGraph.
"""

import os

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_extras.bottom_container import bottom

# Load environment variables
load_dotenv()

# Import our modules
from src.document_processor import DocumentProcessor
from src.vectorstore import VectorStoreManager
from src.tools import create_search_tool
from src.agent import create_documentation_agent
from src.structure_visualizer import DocumentStructureVisualizer


# Page configuration
st.set_page_config(
    page_title="Document Intelligence Assistant", page_icon="📄", layout="wide"
)


def initialize_session_state():
    """Initialize all session state variables."""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = "not_started"
    if "docling_docs" not in st.session_state:
        st.session_state.docling_docs = []


def process_and_index(uploaded_files):
    """Process uploaded documents and create vector store."""
    try:
        # Step 1: Process documents with Docling
        with st.spinner(
            f"📄 Processing {len(uploaded_files)} document(s) with Docling..."
        ):
            processor = DocumentProcessor()
            documents, docling_docs = processor.process_uploaded_files(uploaded_files)
            st.session_state.docling_docs = docling_docs

        if not documents:
            st.error(
                "No documents were processed. Please check the files and try again."
            )
            return

        # Step 2: Chunk and create vector store
        with st.spinner("✂️ Chunking documents..."):
            vs_manager = VectorStoreManager()
            chunks = vs_manager.chunk_documents(documents)

        with st.spinner("🔢 Creating vector store..."):
            vectorstore = vs_manager.create_vectorstore(chunks)
            st.session_state.vectorstore = vectorstore

        # Step 3: Create agent
        with st.spinner("🤖 Creating agent..."):
            search_tool = create_search_tool(vectorstore)
            agent = create_documentation_agent([search_tool])
            st.session_state.agent = agent

        st.session_state.processing_status = "completed"
        st.success("✅ Documents indexed! You can now chat with them below.")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.session_state.processing_status = "error"


def render_sidebar():
    """Render the sidebar with setup controls."""
    with st.sidebar:
        st.title("⚙️ Setup")

        # File uploader
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["pdf", "docx", "pptx", "html"],
            accept_multiple_files=True,
            help="Upload PDF, Word (DOCX), PowerPoint (PPTX), or HTML files",
        )

        # Show uploaded files count
        if uploaded_files:
            st.info(f"📊 {len(uploaded_files)} file(s) uploaded")

            # List uploaded files
            with st.expander("📁 Uploaded Files"):
                for file in uploaded_files:
                    st.write(f"- {file.name} ({file.type})")

            # Process button
            if st.button("🚀 Process & Index", width="stretch"):
                st.session_state.uploaded_files = uploaded_files
                process_and_index(uploaded_files)

        # Status indicator
        st.divider()
        st.subheader("📊 Status")

        if st.session_state.processing_status == "not_started":
            st.info("Ready to start")
        elif st.session_state.processing_status == "completed":
            st.success("✅ Ready to chat!")
        elif st.session_state.processing_status == "error":
            st.error("❌ Error occurred")

        # Tips
        with st.expander("💡 Tips"):
            st.markdown(
                """
            **Supported formats:**
            - PDF documents
            - Word documents (.docx)
            - PowerPoint presentations (.pptx)
            - HTML files

            **Best practices:**
            - Upload related documents together
            - Start with a few documents for testing
            - Documents are processed with OCR for scanned content
            - Tables and structure are preserved

            **For production:**
            - Add persistent vector storage
            - Implement batch processing
            - Use GPU acceleration for faster processing
            - Add authentication and access controls
            """
            )


def render_structure_viz():
    """Render document structure visualization with support for batched documents."""
    st.title("📊 Document Structure")

    if not st.session_state.docling_docs:
        st.info("👈 Please upload and process your documents first to see their structure!")
        return

    # GROUPING LOGIC: Reconstruct original filenames from batches
    #    The processor saves names as "MyBook.pdf (Pages 0-10)"
    #    We split on " (Pages" to get back "MyBook.pdf"
    unique_files = {}
    for batch in st.session_state.docling_docs:
        # Extract base name (e.g., "Book.pdf" from "Book.pdf (Pages 0-10)")
        full_name = batch['filename']
        if " (Pages" in full_name:
            base_name = full_name.split(" (Pages")[0]
        else:
            base_name = full_name
        
        if base_name not in unique_files:
            unique_files[base_name] = []
        unique_files[base_name].append(batch)

    # Document Selector (Shows clean names like "Book.pdf")
    selected_base_name = st.selectbox("Select document to analyze:", list(unique_files.keys()))

    if not selected_base_name:
        return

    # Get all batches for this file
    selected_batches = unique_files[selected_base_name]

    # Instantiate Visualizer with the LIST of batches
    #    (This uses the new class you just updated)
    visualizer = DocumentStructureVisualizer(selected_batches)

    # Display structure in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📑 Summary", "🏗️ Hierarchy", "📊 Tables", "🖼️ Images"])

    with tab1:
        st.subheader(f"Summary: {selected_base_name}")
        summary = visualizer.get_document_summary()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Pages", summary['num_pages'])
        with col2:
            st.metric("Tables", summary['num_tables'])
        with col3:
            st.metric("Images", summary['num_pictures'])
        with col4:
            st.metric("Text Items", summary['num_texts'])

        st.subheader("Content Types")
        if summary['text_types']:
            text_types_df = pd.DataFrame([
                {'Type': k, 'Count': v}
                for k, v in sorted(summary['text_types'].items(), key=lambda x: -x[1])
            ])
            st.dataframe(text_types_df, width="stretch")
        else:
            st.info("No text content detected.")

    with tab2:
        st.subheader("Document Hierarchy")
        hierarchy = visualizer.get_document_hierarchy()

        if hierarchy:
            # Sort by page number to ensure order is correct across batches
            sorted_hierarchy = sorted(hierarchy, key=lambda x: (x['page'] if x['page'] is not None else -1))
            
            for item in sorted_hierarchy:
                indent = "  " * (item['level'] - 1)
                page_str = f"Page {item['page']}" if item['page'] is not None else "Unknown Page"
                st.markdown(f"{indent}**{item['text']}** _({page_str})_")
        else:
            st.info("No hierarchical structure detected")

    with tab3:
        st.subheader("Tables")
        tables_info = visualizer.get_tables_info()

        if tables_info:
            # Sort tables by table number
            sorted_tables = sorted(tables_info, key=lambda x: x['table_number'])
            
            for table_data in sorted_tables:
                page_str = f"Page {table_data['page']}" if table_data['page'] is not None else ""
                st.markdown(f"### Table {table_data['table_number']} ({page_str})")

                if table_data['caption']:
                    st.caption(table_data['caption'])

                if not table_data['is_empty']:
                    st.dataframe(table_data['dataframe'], width="stretch")
                else:
                    st.info("Table is empty")

                st.divider()
        else:
            st.info("No tables found in this document")

    with tab4:
        st.subheader("Images")
        pictures_info = visualizer.get_pictures_info()

        if pictures_info:
            # Sort by page 
            sorted_pics = sorted(pictures_info, key=lambda x: (x['page'] if x['page'] is not None else -1))
            
            for pic_data in sorted_pics:
                page_str = f"Page {pic_data['page']}" if pic_data['page'] is not None else ""
                st.markdown(f"**Image {pic_data['picture_number']}** ({page_str})")

                if pic_data['caption']:
                    st.caption(pic_data['caption'])

                # Display the actual image if available
                if pic_data['pil_image'] is not None:
                    st.image(pic_data['pil_image'], width="stretch")
                else:
                    st.info("Image data not available")

                # Show bounding box info
                if pic_data['bounding_box']:
                    bbox = pic_data['bounding_box']
                    with st.expander("📐 Position Details"):
                        st.text(f"Position: ({bbox['left']:.1f}, {bbox['top']:.1f}) - ({bbox['right']:.1f}, {bbox['bottom']:.1f})")

                st.divider()
        else:
            st.info("No images found in this document")


def render_chat():
    """Render the chat interface."""
    # Check if agent is ready
    if st.session_state.agent is None:
        st.info("👈 Please upload and process your documents in the sidebar first!")
        st.markdown(
            """
        ### How to use:
        1. Upload your documents in the sidebar (PDF, DOCX, PPTX, or HTML)
        2. Click "Process & Index" and wait for processing
        3. Start asking questions about your documents!

        ### What you can do:
        - Ask questions about document content
        - Compare information across multiple documents
        - Extract specific data or insights
        - Summarize document sections
        """
        )
        return

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input in bottom container (attempt to fix positioning in tabs)
    with bottom():
        prompt = st.chat_input("Ask a question about your documents...")

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            # Create status and message placeholders
            status_placeholder = st.empty()
            message_placeholder = st.empty()

            try:
                # Create config with thread ID for conversation memory
                config = {"configurable": {"thread_id": "document_chat"}}

                # Generator function for real-time streaming
                # Generator function for real-time streaming
                def generate_response():
                    """Generator that yields tokens from LangGraph stream."""
                    status_placeholder.markdown("🤔 **Thinking...**")
                    first_content_token = True
                    tool_call_detected = False
                    final_answer_started = False

                    # Stream with "messages" mode for real LLM tokens
                    for msg, metadata in st.session_state.agent.stream(
                        {"messages": [HumanMessage(content=prompt)]},
                        config=config,
                        stream_mode="messages",
                    ):
                        # Check which node is streaming
                        langgraph_node = metadata.get("langgraph_node", "")

                        # Skip tool outputs (search results)
                        if "tools" in langgraph_node.lower() or "tool" in langgraph_node.lower():
                            if not tool_call_detected:
                                status_placeholder.markdown("🔍 **Searching documents...**")
                                tool_call_detected = True
                            continue

                        # Only stream content from the "agent" node
                        if "agent" in langgraph_node.lower() and hasattr(msg, "content"):
                            
                            raw_content = msg.content
                            
                            # Handle Gemini's List-based Content and no-list one from openai
                            # Gemini sometimes returns [{"type": "text", "text": "..."}] instead of "..."
                            content = ""
                            
                            if isinstance(raw_content, list):
                                for part in raw_content:
                                    # Extract text from dictionary format
                                    if isinstance(part, dict) and "text" in part:
                                        content += part["text"]
                                    # Or just append if it's already a string part
                                    elif isinstance(part, str):
                                        content += part
                            else:
                                # Normal case (String)
                                content = str(raw_content)

                            # Only yield non-empty content tokens
                            if content:
                                if first_content_token:
                                    status_placeholder.markdown("💬 **Generating answer...**")
                                    first_content_token = False
                                    final_answer_started = True

                                if final_answer_started:
                                    yield content

                    # Clear status when streaming is complete
                    status_placeholder.empty()

                # Use st.write_stream for automatic token-by-token display
                with message_placeholder.container():
                    full_response = st.write_stream(generate_response())

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Chat error: {error_details}")  # Log to console
                error_msg = f"❌ Error: {str(e)}"
                status_placeholder.empty()
                message_placeholder.markdown(error_msg)
                full_response = error_msg

        # Add assistant response to history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


def main():
    """Main application function."""
    initialize_session_state()
    render_sidebar()

    # Create tabs for different views
    tab1, tab2 = st.tabs(["💬 Chat", "📊 Document Structure"])

    with tab1:
        render_chat()

    with tab2:
        render_structure_viz()


if __name__ == "__main__":
    main()
