"""
PDF Merger for Rental Application

This script merges multiple PDF files into a single document with a table of contents.
The document structure is defined in config.py (see config.example.py for template).

Features:
- Automatic TOC generation with clickable links
- Custom fonts for better styling
- Preserves text selection in PDFs
- Hierarchical document organization
"""

import fitz  # PyMuPDF
import os
from config import SCHEMA  # Import SCHEMA from config file

# 🔹 SET YOUR DIRECTORIES HERE
INPUT_DIR = "../../CleanFiles"
OUTPUT_DIR = "my_output_folder"
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "dossier_locatif.pdf")

# Add font paths
TITLE_FONT_PATH = "./AirbnbCereal_W_Blk.otf"
TEXT_FONT_PATH = "./AirbnbCereal_W_Bk.otf"  # or any other font you want to use for regular text

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def merge_pdfs():
    doc = fitz.open()
    
    # Load custom fonts
    try:
        title_font = fitz.Font(fontfile=TITLE_FONT_PATH)
    except:
        print("⚠️ Title font not loaded, falling back to helvetica")
        title_font = fitz.Font("helv")

    try:
        text_font = fitz.Font(fontfile=TEXT_FONT_PATH)
    except:
        print("⚠️ Text font not loaded, falling back to helvetica")
        text_font = fitz.Font("helv")
    
    toc = []  # Internal TOC for PDF navigation
    visible_toc = []  # TOC entries to display on Page 1
    current_page = 2  # Start from page 2 since page 1 will be TOC
    
    def process_section(title, content, level=1):
        nonlocal current_page

        # If it's a list of PDFs, add them
        if isinstance(content, list):
            # Only add to TOC once, before processing all files
            if not any(parent["title"] == "Introduction" for parent in parent_sections):
                toc.append([level, title, current_page])
                visible_toc.append((title, current_page, level))

            # Process all files in the section
            for pdf_file in content:
                pdf_path = os.path.join(INPUT_DIR, pdf_file)

                if os.path.exists(pdf_path):
                    sub_doc = fitz.open(pdf_path)
                    page_count = len(sub_doc)

                    # Insert the document into merged PDF while preserving text
                    doc.insert_pdf(sub_doc, links=True, annots=True, show_progress=False)

                    # Update current page count
                    current_page += page_count
                    sub_doc.close()
                else:
                    print(f"⚠️ File not found: {pdf_path}")

        # If it's a nested dictionary, process subsections
        elif isinstance(content, dict):
            # Add to TOC only if not Introduction
            if title != "Introduction":
                toc.append([level, title, current_page])  # Add section to TOC
                visible_toc.append((title, current_page, level))
            
            # Keep track of parent sections for nested items
            parent_sections.append({"title": title, "level": level})
            
            for sub_title, sub_content in content.items():
                process_section(sub_title, sub_content, level=level + 1)
            
            parent_sections.pop()

    # Initialize parent sections tracker
    parent_sections = []
    
    # Process the schema
    for section, content in SCHEMA.items():
        process_section(section, content, level=1)

    # Create TOC page at the beginning
    toc_page = doc.new_page(0)  # Insert TOC as first page
    
    # Add title with title font
    tw = fitz.TextWriter(toc_page.rect)
    tw.append((50, 50), "Table des Matières", font=title_font, fontsize=20)
    tw.write_text(toc_page)

    # Add visible TOC entries with text font
    y_position = 90
    for title, page_number, level in visible_toc:
        indent = 20 * (level - 1)
        text_x = 50 + indent
        text_y = y_position

        # Create the entry text
        entry_text = f"{title}"
        page_text = f"Page {page_number}"
        
        # Use title font for main sections (level 1) and text font for subsections
        current_font = title_font if level == 1 else text_font
        current_size = 13 if level == 1 else 11
        
        # Calculate positions
        entry_width = len(entry_text) * (7 if level > 1 else 8)  # Slightly wider for titles
        dots_width = 350 - entry_width - 50  # Space for dots
        
        # Use TextWriter for selectable text
        tw = fitz.TextWriter(toc_page.rect)
        
        # Add the title (left-aligned)
        tw.append((text_x, text_y), entry_text, font=current_font, fontsize=current_size)
        
        # Add dots (always with text font)
        tw.append((text_x + entry_width + 5, text_y), 
                 "." * int(dots_width/4), 
                 font=text_font, 
                 fontsize=11)
        
        # Add page number (right-aligned, always with text font)
        tw.append((400, text_y), page_text, font=text_font, fontsize=11)
        
        # Write all text at once
        tw.write_text(toc_page)

        # Make the entire line clickable
        link_rect = fitz.Rect(text_x, text_y - 10, 450, text_y + 4)
        toc_page.insert_link({
            "kind": fitz.LINK_GOTO,
            "from": link_rect,
            "page": page_number - 1
        })

        y_position += 25 if level == 1 else 20  # More space after main sections

    # Set the PDF navigation TOC
    doc.set_toc(toc)

    # Save the merged PDF with text preservation
    doc.save(
        OUTPUT_PDF,
        garbage=4,  # Optimize PDF
        deflate=True,  # Compress streams
        clean=True  # Remove unused elements
    )
    doc.close()

    print(f"✅ Merged PDF created with selectable text and navigation: {OUTPUT_PDF}")


# Run the merging function
if __name__ == "__main__":
    merge_pdfs()