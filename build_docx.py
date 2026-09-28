# SCRIPT TO CONVERT MARKDOWN REPORT TO DOCX
# Path: C:/Users/Admin/.gemini/antigravity/scratch/crop_recommendation_system/build_docx.py

import os
import re
import sys

def check_docx_installed():
    try:
        import docx
        print("python-docx is already installed.")
    except ImportError:
        print("python-docx is not installed. Installing it now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])

check_docx_installed()

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_shading(cell, hex_color):
    """Set the background color of a cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for table cells."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_page_number(run):
    """Inserts a page number field in a footer run."""
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def convert_md_to_docx(md_path, docx_path):
    print(f"Reading markdown from {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    doc = Document()
    
    # Page setup
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Document styles configuration
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x1e, 0x29, 0x3b) # Slate grey
    
    # Custom colors
    PRIMARY_COLOR = RGBColor(16, 185, 129) # Emerald #10b981
    SECONDARY_COLOR = RGBColor(59, 130, 246) # Blue #3b82f6
    TEXT_COLOR = RGBColor(30, 41, 59) # Slate #1e293b
    
    in_code_block = False
    code_content = []
    
    in_table = False
    table_rows = []
    
    # Helper to clear formatting and set font
    def set_font(run, name='Calibri', size=Pt(11), color=TEXT_COLOR, bold=False, italic=False):
        run.font.name = name
        run.font.size = size
        run.font.color.rgb = color
        run.bold = bold
        run.italic = italic
        
    # Title Page Generation
    doc.add_paragraph('\n' * 5)
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("CROP RECOMMENDATION SYSTEM USING PYTHON AND MACHINE LEARNING")
    set_font(title_run, size=Pt(24), color=PRIMARY_COLOR, bold=True)
    
    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run("A Comprehensive Academic Project Report")
    set_font(sub_run, size=Pt(14), color=SECONDARY_COLOR, italic=True)
    
    doc.add_paragraph('\n' * 8)
    
    info_p = doc.add_paragraph()
    info_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info_run1 = info_p.add_run("Team Members:\n")
    set_font(info_run1, size=Pt(12), bold=True)
    info_run2 = info_p.add_run("G. Vamsi Krishna  |  Akshatha M  |  Dhanashree V Naik\n\n")
    set_font(info_run2, size=Pt(12))
    info_run3 = info_p.add_run("Academic Year: 2026\nCourse: Python Mini Project")
    set_font(info_run3, size=Pt(10), color=RGBColor(148, 163, 184))
    
    doc.add_page_break()
    
    # Configure Headers & Footers on normal pages
    footer = sections[0].footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer_run = footer_p.add_run("Page ")
    set_font(footer_run, size=Pt(9), color=RGBColor(148, 163, 184))
    add_page_number(footer_run)
    
    header = sections[0].header
    header_p = header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header_run = header_p.add_run("Crop Recommendation System Using Python and Machine Learning")
    set_font(header_run, size=Pt(8.5), color=RGBColor(148, 163, 184), italic=True)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 1. Code block handling
        if stripped.startswith("```"):
            if in_code_block:
                # End of code block, write accumulated text
                in_code_block = False
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(6)
                
                # Shading of code block background using XML manipulation
                pBdr = parse_xml(r'<w:pBdr %s><w:left w:val="single" w:sz="24" w:space="4" w:color="10B981"/></w:pBdr>' % nsdecls('w'))
                p._p.get_or_add_pPr().append(pBdr)
                shd = parse_xml(r'<w:shd %s w:fill="F8FAFC"/>' % nsdecls('w'))
                p._p.get_or_add_pPr().append(shd)
                
                code_text = "".join(code_content)
                code_run = p.add_run(code_text)
                set_font(code_run, name='Courier New', size=Pt(9), color=RGBColor(15, 23, 42))
                code_content = []
            else:
                in_code_block = True
            i += 1
            continue
            
        if in_code_block:
            code_content.append(line)
            i += 1
            continue
            
        # 2. Table handling
        if stripped.startswith("|"):
            in_table = True
            table_rows.append(stripped)
            i += 1
            continue
        elif in_table:
            # End of table, process and write table
            in_table = False
            # Remove separator row (like |:---|:---|)
            processed_rows = []
            for tr in table_rows:
                if re.search(r'^\|[\s:-|]+$', tr):
                    continue
                processed_rows.append(tr)
                
            if processed_rows:
                # Parse rows
                grid = []
                for tr in processed_rows:
                    cells = [c.strip() for c in tr.split("|")[1:-1]]
                    grid.append(cells)
                    
                if grid:
                    num_cols = len(grid[0])
                    num_rows = len(grid)
                    table = doc.add_table(rows=num_rows, cols=num_cols)
                    table.autofit = True
                    
                    # Style and populate
                    for r_idx, row_data in enumerate(grid):
                        row = table.rows[r_idx]
                        is_header = (r_idx == 0)
                        for c_idx, cell_value in enumerate(row_data):
                            # Ensure cell exists
                            if c_idx < len(row.cells):
                                cell = row.cells[c_idx]
                                cell.text = cell_value
                                
                                # Margins / Padding
                                set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
                                
                                # Shading
                                if is_header:
                                    set_cell_shading(cell, "10B981") # Emerald primary
                                    for p in cell.paragraphs:
                                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        for run in p.runs:
                                            set_font(run, size=Pt(10), color=RGBColor(255,255,255), bold=True)
                                else:
                                    bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                                    set_cell_shading(cell, bg_color)
                                    for p in cell.paragraphs:
                                        for run in p.runs:
                                            set_font(run, size=Pt(9.5), color=TEXT_COLOR)
                                            
                    # Add space after table
                    doc.add_paragraph().paragraph_format.space_after = Pt(12)
            table_rows = []
            
        # 3. Headings
        if stripped.startswith("# "):
            val = stripped[2:]
            if "CROP RECOMMENDATION SYSTEM" in val.upper():
                i += 1
                continue # Skip title since we already wrote title page
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(val)
            set_font(run, size=Pt(18), color=PRIMARY_COLOR, bold=True)
            i += 1
            continue
            
        elif stripped.startswith("## TABLE OF CONTENTS"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
            run = p.add_run("TABLE OF CONTENTS")
            set_font(run, size=Pt(16), color=PRIMARY_COLOR, bold=True)
            
            toc_data = [
                ("", "Abstract", "2"),
                # Chapter I
                ("I", "Introduction", "3"),
                ("I", "1.1 Agricultural Background and Global Context", "3"),
                ("I", "1.2 Problem Identification in Traditional Farming Systems", "4"),
                ("I", "1.3 Role of Artificial Intelligence and Machine Learning in Smart Agriculture", "5"),
                ("I", "1.4 Detailed Literature Survey and Related Works", "6"),
                # Chapter II
                ("II", "Objectives", "8"),
                ("II", "2.1 Smart Crop Recommendation", "8"),
                ("II", "2.2 Multi-Parameter Analysis", "9"),
                ("II", "2.3 Mitigation of Crop Failure and Financial Risks", "9"),
                ("II", "2.4 Soil Quality Preservation and Sustainability", "10"),
                ("II", "2.5 Technological Empowerment of Smallholder Farmers", "10"),
                # Chapter III
                ("III", "Hardware and Software Requirements", "11"),
                ("III", "3.1 Hardware Configurations (Minimum & Recommended Development Specs)", "11"),
                ("III", "3.2 Hardware Specifications for Client Deployment", "11"),
                ("III", "3.3 Software Stack and Development Environment Setup", "12"),
                ("III", "3.4 Description and Justification of Libraries Used", "13"),
                # Chapter IV
                ("IV", "Dataset Description", "15"),
                ("IV", "4.1 Dataset Source, Collection, and Characteristics", "15"),
                ("IV", "4.2 Statistical Summary of Features", "15"),
                ("IV", "4.3 Detailed Description of Features and Attributes", "16"),
                ("IV", "4.4 Target Label Classes and Agricultural Classifications", "17"),
                # Chapter V
                ("V", "Methodology", "18"),
                ("V", "5.1 Proposed System Architecture and Dataflow", "18"),
                ("V", "5.2 Machine Learning Algorithms Used", "19"),
                ("V", "  5.2.1 Decision Tree Classifier: Theory, Math, and Splitting Criteria", "19"),
                ("V", "  5.2.2 Random Forest Classifier: Bagging, Feature Randomness, and Ensemble Voting", "21"),
                ("V", "5.3 System Flowchart and Step-by-Step Computational Workflow", "23"),
                # Chapter VI
                ("VI", "Results and Analysis", "24"),
                ("VI", "6.1 Performance Evaluation Metrics: Theoretical Foundations", "24"),
                ("VI", "6.2 Model Comparison and Evaluation Results", "25"),
                ("VI", "6.3 Feature Importance Analysis and Agronomic Discussion", "26"),
                ("VI", "6.4 Prediction Results under Real-World Scenarios", "27"),
                ("VI", "6.5 User Interface and Web Application Workflows", "28"),
                # Chapter VII
                ("VII", "Conclusion", "30"),
                ("VII", "7.1 Summary of Contributions", "30"),
                ("VII", "7.2 Project Limitations", "30"),
                ("VII", "7.3 Directions for Future Work", "31"),
                # Chapter VIII
                ("VIII", "References", "32"),
                # Chapter IX
                ("IX", "Appendix: Source Code", "33"),
                ("IX", "9.1 Training Script (train.py)", "33"),
                ("IX", "9.2 Prediction Module (predict.py)", "35"),
                ("IX", "9.3 Flask Web Application (app.py)", "36"),
                ("IX", "9.4 Front-end Styling (style.css)", "38"),
                ("IX", "9.5 Interactivity Script (script.js)", "40")
            ]
            
            table = doc.add_table(rows=len(toc_data) + 1, cols=3)
            table.autofit = True
            
            # Format Header
            hdr_row = table.rows[0]
            hdr_row.cells[0].text = "Chapter No"
            hdr_row.cells[1].text = "Description"
            hdr_row.cells[2].text = "Page No"
            
            for cell in hdr_row.cells:
                set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
                set_cell_shading(cell, "10B981") # Emerald primary
                for p_elm in cell.paragraphs:
                    p_elm.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r_elm in p_elm.runs:
                        set_font(r_elm, size=Pt(10), color=RGBColor(255, 255, 255), bold=True)
                        
            # Fill Data
            for r_idx, (ch_no, desc, pg_no) in enumerate(toc_data, start=1):
                row = table.rows[r_idx]
                row.cells[0].text = ch_no
                row.cells[1].text = desc
                row.cells[2].text = pg_no
                
                # Text alignments
                row.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
                row.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Styling and padding
                for c_idx, cell in enumerate(row.cells):
                    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                    bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                    set_cell_shading(cell, bg_color)
                    for p_elm in cell.paragraphs:
                        for r_elm in p_elm.runs:
                            is_bold = (ch_no != "" and (desc in ["Introduction", "Objectives", "Hardware and Software Requirements", "Dataset Description", "Methodology", "Results and Analysis", "Conclusion", "References", "Appendix: Source Code"] or desc == "Abstract"))
                            set_font(r_elm, size=Pt(9.5), color=TEXT_COLOR, bold=is_bold)
                            
            # Merge column 0 cells for Chapters
            start_row_idx = 1
            current_ch = toc_data[0][0]
            for idx in range(1, len(toc_data)):
                ch = toc_data[idx][0]
                row_idx = idx + 1
                if ch == current_ch:
                    continue
                else:
                    if current_ch != "" and (row_idx - 1) > start_row_idx:
                        cell_start = table.cell(start_row_idx, 0)
                        cell_end = table.cell(row_idx - 1, 0)
                        cell_start.merge(cell_end)
                        cell_start.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    start_row_idx = row_idx
                    current_ch = ch
                    
            last_row_idx = len(toc_data)
            if current_ch != "" and last_row_idx > start_row_idx:
                cell_start = table.cell(start_row_idx, 0)
                cell_end = table.cell(last_row_idx, 0)
                cell_start.merge(cell_end)
                cell_start.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                
            doc.add_paragraph().paragraph_format.space_after = Pt(12)
            
            i += 1
            while i < len(lines) and "</table>" not in lines[i]:
                i += 1
            i += 1
            continue
            
        elif stripped.startswith("## "):
            val = stripped[3:]
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(val)
            set_font(run, size=Pt(14), color=SECONDARY_COLOR, bold=True)
            i += 1
            continue
            
        elif stripped.startswith("### "):
            val = stripped[4:]
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(val)
            set_font(run, size=Pt(12), color=TEXT_COLOR, bold=True)
            i += 1
            continue
            
        # 4. Bullet lists
        if stripped.startswith("* ") or stripped.startswith("- "):
            val = stripped[2:]
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            
            # Format bold inline elements like **Bold:**
            parts = re.split(r'(\*\*.*?\*\*)', val)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run(part[2:-2])
                    set_font(run, bold=True)
                else:
                    run = p.add_run(part)
                    set_font(run)
            i += 1
            continue
            
        # 5. Math block or diagrams representation
        if stripped.startswith("$$") or stripped.startswith("\\[") or stripped.startswith("\\]"):
            i += 1
            continue # skip math markers, let equations display in paragraph
            
        # 6. Page breaks
        if stripped == "---":
            # Add a divider or page break if it makes sense, we'll add page break for top sections
            # but let's just make it a clean paragraph spacing here.
            doc.add_paragraph().paragraph_format.space_after = Pt(12)
            i += 1
            continue
            
        # 7. Normal Paragraph
        if stripped:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            
            # Handle inline styling: Bold (**text**) and Italic (*text* or \(_...\) or \(...\))
            parts = re.split(r'(\*\*.*?\*\*|\(.*?\)|\\\(.*?\\\))', line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run(part[2:-2])
                    set_font(run, bold=True)
                elif part.startswith("\\(") and part.endswith("\\)"):
                    # Math formula
                    run = p.add_run(part[2:-2])
                    set_font(run, name='Times New Roman', italic=True)
                elif part.startswith("(") and part.endswith(")"):
                    # Regular parens
                    run = p.add_run(part)
                    set_font(run)
                else:
                    run = p.add_run(part)
                    set_font(run)
                    
        i += 1
        
    print(f"Saving Word document to {docx_path}...")
    doc.save(docx_path)
    print("Document saved successfully!")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    md_path = os.path.join(base_dir, "project_report.md")
    docx_path = os.path.join(base_dir, "project_report_v2.docx")
    
    # Try using artifact path if local not found
    if not os.path.exists(md_path):
        md_path = r"C:\Users\Admin\.gemini\antigravity\brain\b69a7a05-5336-461f-9370-7be579901432\project_report.md"
        
    convert_md_to_docx(md_path, docx_path)
