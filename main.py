import io
import tempfile
from flask import Flask, render_template, request, send_file
import xml.etree.ElementTree as ET
import os
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    num_files = 0  # Variable to store the number of files uploaded
    if request.method == 'POST':
        files = request.files.getlist('files')
        num_files = len(files)  # Update the variable with the number of files uploaded

        abw_document = ET.Element("ABWDocument")
        abw_document.set("xmlns:agrlib", "http://services.agresso.com/schema/ABWSchemaLib/2005/05/13")
        abw_document.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        abw_document.set("xsi:schemaLocation", "http://services.agresso.com/schema/ABWDocument/2005/05/13 http://services.agresso.com/schema/ABWDocument/2005/05/13/ABWDocument.xsd")
        abw_document.set("xmlns", "http://services.agresso.com/schema/ABWDocument/2005/05/13")

        documents_root = ET.SubElement(abw_document, "Documents")

        for file in files:
            # Create a new Document element
            filename = file.filename
            document = ET.SubElement(documents_root, "Document")
            
            # Remove path only keep filename
            filename = os.path.basename(filename)

            external_doc_id = re.findall("\d+", filename.removesuffix('.pdf'))[0]

            # Create and append the child elements for the current Document
            ET.SubElement(document, "agrlib:ExternalDocId").text = external_doc_id
            ET.SubElement(document, "DocType").text = "CURDOK"
            ET.SubElement(document, "DocIndex1").text = "1K"
            ET.SubElement(document, "DocIndex1OK").text = "1"
            ET.SubElement(document, "DocIndex2").text = "1010"
            ET.SubElement(document, "DocIndex2OK").text = "1"
            ET.SubElement(document, "DocIndex3").text = external_doc_id
            ET.SubElement(document, "DocIndex3OK").text = "1"

            pages_element = ET.SubElement(document, "Pages")

            page_element = ET.SubElement(pages_element, "Page")
            ET.SubElement(page_element, "PageNo").text = "1"
            ET.SubElement(page_element, "Filename").text = filename

        # Create the XML tree
        tree = ET.ElementTree(abw_document)

        generated_file = io.BytesIO()
        tree.write(generated_file, encoding="utf-8", xml_declaration=True)
        generated_file.seek(0)

        return send_file(generated_file, as_attachment=True, download_name="generated.xml", mimetype="application/xml")
    
    return render_template('index.html', num_files=num_files)

if __name__ == '__main__':
    app.run(debug=True)
