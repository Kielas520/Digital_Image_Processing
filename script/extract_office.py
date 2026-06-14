import zipfile
import os
import xml.etree.ElementTree as ET
import shutil
import sys

def extract_office_doc(filepath, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    images_dir = os.path.join(output_dir, 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    text_content = []
    
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            # 1. 提取所有图片 (Extract Images)
            for name in z.namelist():
                if name.startswith('word/media/') or name.startswith('ppt/media/'):
                    filename = os.path.basename(name)
                    if filename: # Ignore directory entries
                        source = z.open(name)
                        target = open(os.path.join(images_dir, filename), "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)

            # 2. 提取文本内容 (Extract Text)
            if filepath.endswith('.docx'):
                if 'word/document.xml' in z.namelist():
                    xml_content = z.read('word/document.xml')
                    root = ET.fromstring(xml_content)
                    # DOCX text is in <w:t> tags
                    for elem in root.iter():
                        if elem.tag.endswith('}t') and elem.text:
                            text_content.append(elem.text)
            
            elif filepath.endswith('.pptx'):
                # PPTX text is in slides
                slide_files = [n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
                # Sort slides numerically (slide1.xml, slide2.xml...)
                slide_files.sort(key=lambda x: int(os.path.basename(x).replace('slide', '').replace('.xml', '')))
                
                for slide_file in slide_files:
                    xml_content = z.read(slide_file)
                    root = ET.fromstring(xml_content)
                    # PPTX text is in <a:t> tags
                    text_content.append(f"\n--- {os.path.basename(slide_file)} ---")
                    for elem in root.iter():
                        if elem.tag.endswith('}t') and elem.text:
                            text_content.append(elem.text)
                            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

    # Save text to a .txt file
    text_path = os.path.join(output_dir, 'extracted_text.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text_content))
        
    print(f"Extraction complete for {filepath}.")
    print(f"Text saved to: {text_path}")
    print(f"Images saved to: {images_dir}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_office.py <filepath> <output_dir>")
        sys.exit(1)
    extract_office_doc(sys.argv[1], sys.argv[2])
