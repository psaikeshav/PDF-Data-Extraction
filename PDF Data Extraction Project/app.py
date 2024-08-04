from flask import Flask, request, render_template, send_file
import os
import pandas as pd
import pdfminer
from pdfminer.high_level import extract_text
from PIL import Image
import pytesseract
import cv2
import pdfplumber
import re
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def convert_to_excel(data, output_path):
    df = pd.DataFrame([data])
    df.to_excel(output_path, index=False)

def convert_to_csv(data, output_path):
    df = pd.DataFrame([data])
    df.to_csv(output_path, index=False)

def extract_text_from_pdf(pdf_path):
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            extracted_data.append(text)
    return extracted_data

words_to_remove=["Course","Student","Name","Tech","Computer","Science"," Computer","currently","in","is","my","B"]

def get_customer_name(text):
    start_keyword = "Name:"
    end_keyword = "Address"
    try:
        start_index = text.index(start_keyword) + len(start_keyword)
        end_index = text.index(end_keyword, start_index)
        address = text[start_index:end_index].strip()
        return address
    except ValueError:
        return "Unavailable."

def get_address(text):
    start_keyword = "Address:"
    end_keyword = "Phone"
    
    try:
        start_index = text.index(start_keyword) + len(start_keyword)
        end_index = text.index(end_keyword, start_index)
        address = text[start_index:end_index].strip()
        return address
    except ValueError:
        return "Unavailable."

def get_phone_number(text):
    start_keyword = "Number:"
    end_keyword = "Email"
    
    try:
        start_index = text.index(start_keyword) + len(start_keyword)
        end_index = text.index(end_keyword, start_index)
        address = text[start_index:end_index].strip()
        return address
    except ValueError:
        return "Unavailable."
    
def get_email(text):
    start_keyword = "Email:"
    end_keyword = "Roof"
    try:
        start_index = text.index(start_keyword) + len(start_keyword)
        end_index = text.index(end_keyword, start_index)
        email= text[start_index:end_index].strip()
        return email
    except ValueError:
        return "Unavailable."
    
def remove_newlines(text):
    return text.replace('\n', ' ')

def parse_extracted_data(extracted_data):
    parsed_data = {
        "Customer Name": [],
        "Address": [],
        "Phone Number": [],
        "Email": [],
        "Roof Type": [],
        "Door Materials":[]
    }
    page_text=remove_newlines(extracted_data)
    print(page_text)
    if(get_customer_name(page_text)):
        customer_name = get_customer_name(page_text)
    else:
        return parsed_data
    address=get_address(page_text)
    phoneNumber=get_phone_number(page_text)
    email=get_email(page_text)
    
    parsed_data["Customer Name"].append(customer_name)
    parsed_data["Address"].append(address)
    parsed_data["Phone Number"].append(phoneNumber)
    parsed_data["Email"].append(email)
    parsed_data["Roof Type"].append("Ceramic")
    parsed_data["Door Materials"].append("Wood")
    return parsed_data

def process_pdf(pdf_path, output_path, output_format='excel'):
    extracted_text=extract_text_from_pdf(pdf_path)
    
    df = pd.read_csv("data.csv")
    a=parse_extracted_data(extracted_text[0])
    new_entry_df = pd.DataFrame(a)

    df = df._append(new_entry_df, ignore_index=True)
    print(new_entry_df)
    file_path=("data.csv")
    if os.path.exists(file_path):
        os.remove(file_path)

    df.to_csv("data.csv" ,mode='w',index=False)
    
    if output_format == 'excel':
        convert_to_excel(a, output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        output_path = os.path.join(PROCESSED_FOLDER, f"{os.path.splitext(file.filename)[0]}.xlsx")
        process_pdf(file_path, output_path, output_format='excel')
        return render_template('download.html', filename=os.path.basename(output_path))
    return 'File upload failed'

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)