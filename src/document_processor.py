"""
Docling integration for processing uploaded documents.
"""

import os
from typing import List, Any
from io import BytesIO
from pypdf import PdfReader, PdfWriter # for pdf slicing

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.document import DocumentStream
from langchain_core.documents import Document

class DocumentProcessor:
    """Handles document processing using Docling."""

    def __init__(self):
        """Initialize the Docling DocumentConverter."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.generate_picture_images = True 
        pipeline_options.images_scale = 2.0 

        self.converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

    def process_uploaded_files(self, uploaded_files) -> tuple[List[Document], List[Any]]:
        documents = []
        docling_docs = []

        for uploaded_file in uploaded_files:
            print(f"📄 Processing {uploaded_file.name}...")
            
            # Initialize a "Context Buffer" ---
            # This will hold the last ~300 chars of the previous page to ensure sentence continuity
            last_page_tail = "" 
            
            try:
                master_bytes = BytesIO(uploaded_file.getvalue())
                reader = PdfReader(master_bytes)
                total_pages = len(reader.pages)
                BATCH_SIZE = 50 

                for start_page in range(0, total_pages, BATCH_SIZE):
                    end_page = min(start_page + BATCH_SIZE, total_pages)
                    
                    # ... (Standard PDF Slicing setup) ...
                    writer = PdfWriter()
                    for i in range(start_page, end_page):
                        writer.add_page(reader.pages[i])
                    
                    batch_stream = BytesIO()
                    writer.write(batch_stream)
                    batch_stream.seek(0)
                    source = DocumentStream(name=f"batch_{start_page}", stream=batch_stream)

                    try:
                        result = self.converter.convert(source)
                        doc = result.document
                        
                        pages_content = {} 

                        # Extract text (same as before)
                        for item in doc.texts:
                            internal_page_no = item.prov[0].page_no
                            if internal_page_no not in pages_content:
                                pages_content[internal_page_no] = ""
                            
                            if item.label == "section_header":
                                pages_content[internal_page_no] += f"\n## {item.text}\n"
                            elif item.label == "title":
                                pages_content[internal_page_no] += f"\n# {item.text}\n"
                            else:
                                pages_content[internal_page_no] += f"{item.text}\n"

                        # Create Documents with OVERLAP
                        for internal_page_no, raw_content in pages_content.items():
                            real_page_number = start_page + internal_page_no
                            
                            # Prepend the "Tail" from previous page ---
                            # If we have a tail, add it to the start of this page with a visual separator
                            if last_page_tail:
                                final_content = f"...{last_page_tail}\n\n{raw_content}"
                            else:
                                final_content = raw_content

                            # Update the "Tail" for the NEXT page
                            # Grab the last 300 characters of the CURRENT page
                            if len(raw_content) > 300:
                                last_page_tail = raw_content[-300:]
                            else:
                                last_page_tail = raw_content

                            page_doc = Document(
                                page_content=final_content,
                                metadata={
                                    "source": uploaded_file.name,
                                    "filename": uploaded_file.name,
                                    "page": real_page_number,
                                    "total_pages": total_pages
                                }
                            )
                            documents.append(page_doc)

                        # Store for visualization (WITH OFFSET)
                        docling_docs.append({
                            'filename': f"{uploaded_file.name} (Pages {start_page}-{end_page})",
                            'doc': doc,
                            'page_offset': start_page
                        })

                    except Exception as e:
                        print(f"   ⚠️ Error on batch {start_page}: {str(e)}")
                        continue

            except Exception as e:
                print(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                continue

        return documents, docling_docs
