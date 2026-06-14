import zipfile
import xml.etree.ElementTree as ET
import os
import shutil

pptx_path = "第01章 绪论.pptx"
output_dir = "output_ch01_slide24"
os.makedirs(output_dir, exist_ok=True)

with zipfile.ZipFile(pptx_path, 'r') as z:
    rels_path = 'ppt/slides/_rels/slide24.xml.rels'
    if rels_path in z.namelist():
        rels_xml = z.read(rels_path)
        root = ET.fromstring(rels_xml)
        
        for rel in root:
            target = rel.attrib.get('Target')
            if target and target.startswith('../media/'):
                # Extract image
                media_path = target.replace('../', 'ppt/')
                filename = os.path.basename(media_path)
                out_path = os.path.join(output_dir, filename)
                
                with z.open(media_path) as source, open(out_path, "wb") as f:
                    shutil.copyfileobj(source, f)
                print(f"Extracted: {out_path}")
    else:
        print("Slide 24 relationships not found.")
