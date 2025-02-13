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
    toc = []
    visible_toc = []
    current_page = 1  # Start from page 1
    toc_page_number = None  # Will store where to insert TOC
    
    def process_section(title, content, level=1):
        nonlocal current_page, toc_page_number

        if isinstance(content, dict) and "_toc_" in content:
            toc_page_number = current_page - 1
            current_page += 1
            return

        if isinstance(content, list):
            if not any(parent["title"] == "Introduction" for parent in parent_sections):
                toc.append([level, title, current_page])
                visible_toc.append((title, current_page, level))

            for pdf_file in content:
                pdf_path = os.path.join(INPUT_DIR, pdf_file)
                if os.path.exists(pdf_path):
                    sub_doc = fitz.open(pdf_path)
                    page_count = len(sub_doc)
                    doc.insert_pdf(sub_doc, links=True, annots=True, show_progress=False)
                    current_page += page_count
                    sub_doc.close()
                else:
                    print(f"⚠️ File not found: {pdf_path}")

        elif isinstance(content, dict):
            if title != "Introduction":
                toc.append([level, title, current_page])
                visible_toc.append((title, current_page, level))
            
            parent_sections.append({"title": title, "level": level})
            for sub_title, sub_content in content.items():
                process_section(sub_title, sub_content, level=level + 1)
            parent_sections.pop()

    parent_sections = []
    
    # First pass: process all documents
    for section, content in SCHEMA.items():
        process_section(section, content, level=1)

    if toc_page_number is None:
        print("⚠️ No TOC placement found in schema, adding at the beginning")
        toc_page_number = 0

    # Create and insert TOC at the specified position
    toc_page = doc.new_page(toc_page_number)
    
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
    
    # Add title with title font
    tw = fitz.TextWriter(toc_page.rect)
    tw.append((50, 50), "Table des Matières", font=title_font, fontsize=24)
    tw.write_text(toc_page)

    # Add visible TOC entries with text font
    y_position = 100
    page_width = toc_page.rect.width
    margin_left = 50
    margin_right = 50
    content_width = page_width - margin_left - margin_right
    last_level = 1  # Track the level of the previous entry

    for title, page_number, level in visible_toc:
        # Add extra spacing before new main section (except first one)
        if level == 1 and last_level != 1:
            y_position += 40  # Bigger gap before new main sections
        
        indent = 30 * (level - 1)
        text_x = margin_left + indent
        text_y = y_position

        entry_text = f"{title}"
        page_text = f"{page_number}"
        
        # Use title font for main sections (level 1) and text font for subsections
        current_font = title_font if level == 1 else text_font
        current_size = 14 if level == 1 else 11
        
        # Calculate text widths for proper dot spacing
        title_width = current_font.text_length(entry_text, fontsize=current_size)
        page_num_width = text_font.text_length(page_text, fontsize=11)
        
        # Calculate available space for dots
        dots_width = content_width - indent - title_width - page_num_width - 20
        
        # Calculate number of dots to fill the space (using a smaller dot size)
        dot_char = "."
        dot_width = text_font.text_length(dot_char, fontsize=9)
        num_dots = int(dots_width / dot_width)
        
        tw = fitz.TextWriter(toc_page.rect)
        
        # Add the title (left-aligned)
        tw.append((text_x, text_y), entry_text, font=current_font, fontsize=current_size)
        
        # Add dots (always with text font)
        if level == 1:
            dot_y = text_y + 2  # Adjust dot position for better alignment with larger text
        else:
            dot_y = text_y
        
        tw.append((text_x + title_width + 10, dot_y), 
                 dot_char * num_dots, 
                 font=text_font, 
                 fontsize=9)
        
        # Add page number (right-aligned)
        page_x = page_width - margin_right - page_num_width
        tw.append((page_x, text_y), page_text, font=text_font, fontsize=11)
        
        tw.write_text(toc_page)

        # Make the entire line clickable
        link_rect = fitz.Rect(text_x, text_y - 10, page_width - margin_right, text_y + 4)
        toc_page.insert_link({
            "kind": fitz.LINK_GOTO,
            "from": link_rect,
            "page": page_number - 1
        })

        # Add normal spacing after entries
        y_position += 25  # Same spacing for all entries
        last_level = level  # Remember current level for next iteration

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