import ast
import os
from docx import Document
from docx.shared import RGBColor

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
    Quét dự án và tạo file Word với định dạng tối ưu, các function viết sát nhau hơn.
    """
    doc = Document()
    
    title = doc.add_heading("TÀI LIỆU DOCSTRING PROJECT (THANHMOTOR SHOP)", 0)
    title.alignment = 1

    for root, dirs, files in os.walk(project_path):
        if any(ignored_dir in root for ignored_dir in ["venv", "__pycache__", ".git", "migrations"]):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                docs = extract_docstrings_from_file(file_path)

                if docs:
                    # Tiêu đề File (Heading 1) - Tạo ranh giới giữa các file
                    doc.add_heading(f"File: {file}", level=1)

                    for doc_type, name, content in docs:
                        if doc_type == "Module":
                            # Module docstring ghi bình thường
                            p = doc.add_paragraph()
                            run = p.add_run(f"Mô tả file: {content.strip()}")
                            run.italic = True
                            run.font.color.rgb = RGBColor(89, 89, 89)
                        else:
                            # Class và Function dùng Bullet point để viết sát nhau
                            # Format: [Loại] Tên: Nội dung docstring
                            p = doc.add_paragraph(style='List Bullet')
                            
                            # Tên Function/Class in đậm
                            run_name = p.add_run(f"{doc_type} {name}: ")
                            run_name.bold = True
                            
                            # Nội dung docstring in nghiêng, màu xám
                            run_content = p.add_run(content.strip().replace('\n', ' '))
                            run_content.italic = True
                            run_content.font.color.rgb = RGBColor(89, 89, 89)

                    # Chỉ thêm 1 dòng trống sau khi kết thúc 1 FILE
                    doc.add_paragraph()

    output_name = "Tai_lieu_docstring.docx"
    doc.save(output_name)
    print(f"✅ Đã trích xuất thành công! Các function đã được gom gọn. Kiểm tra: {output_name}")

if __name__ == "__main__":
    print("⏳ Đang quét và tối ưu hóa tài liệu...")
    extract_to_word(".")