#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
import sys

def extract_text_from_docx(docx_path):
    """Extract text from a .docx file"""
    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            
            paragraphs = []
            for paragraph in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                texts = []
                for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if node.text:
                        texts.append(node.text)
                if texts:
                    paragraphs.append(''.join(texts))
            
            return '\n'.join(paragraphs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 extract_docx.py <docx_file>")
        sys.exit(1)
    
    text = extract_text_from_docx(sys.argv[1])
    if text:
        print(text)
