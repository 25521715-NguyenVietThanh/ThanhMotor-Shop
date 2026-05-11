import ast
import os
from docx import Document
from docx.shared import RGBColor, Pt

def extract_docstrings_from_file(file_path):
    """
    Đọc file Python và trích xuất các docstring của Module, Class, Function.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception:
        return []

    results = []
    module_doc = ast.get_docstring(tree)
    if module_doc:
        results.append(("Module", os.path.basename(file_path), module_doc))

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            if doc:
                results.append(("Class", node.name, doc))
        elif isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            if doc:
                results.append(("Function", node.name, doc))
    return results

def extract_to_word(project_path):
    """
    Quét dự án và tạo file Word giữ nguyên định dạng Heading nhưng viết sát nhau hơn.
    """
    doc = Document()
    
    title = doc.add_heading("TÀI LIỆU DOCSTRING PROJECT (THANHMOTOR SHOP)", 0)
    title.alignment = 1

    for root, dirs, files in os.walk(project_path):
        # Bỏ qua các thư mục rác
        if any(ignored_dir in root for ignored_dir in ["venv", "__pycache__", ".git", "migrations"]):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                docs = extract_docstrings_from_file(file_path)

                if docs:
                    # Heading 1: Tên File
                    h1 = doc.add_heading(f"File: {file}", level=1)
                    h1.paragraph_format.space_before = Pt(12) # Khoảng cách phía trên file mới
                    h1.paragraph_format.space_after = Pt(2)   # Viết sát nội dung bên dưới

                    for doc_type, name, content in docs:
                        # Heading 2: Tên Class/Function
                        h2 = doc.add_heading(f"{doc_type}: {name}", level=2)
                        h2.paragraph_format.space_before = Pt(4)  # Thu hẹp khoảng cách với mục trên
                        h2.paragraph_format.space_after = Pt(0)   # Viết sát với nội dung docstring
                        
                        # Nội dung Docstring
                        p = doc.add_paragraph()
                        # Loại bỏ các dòng trống thừa trong nội dung và các dấu xuống dòng dư
                        clean_content = content.strip()
                        run = p.add_run(clean_content)
                        
                        # Làm đẹp
                        run.italic = True
                        run.font.color.rgb = RGBColor(89, 89, 89)
                        
                        # Thiết lập để paragraph này không tự tạo khoảng cách lớn bên dưới
                        p.paragraph_format.space_after = Pt(2)

    output_name = "Tai_lieu_docstring.docx"
    doc.save(output_name)
    print(f"✅ Đã trích xuất xong! Định dạng cũ được giữ nguyên nhưng viết sát nhau hơn.")

if __name__ == "__main__":
    print("⏳ Đang xử lý tài liệu...")
    extract_to_word(".")