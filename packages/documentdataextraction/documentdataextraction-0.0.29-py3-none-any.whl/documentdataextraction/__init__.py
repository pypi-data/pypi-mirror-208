import os
from pathlib import Path
from visitingcard import extract
import pdfkit
from flask import request, make_response
import loggerutility as logger
from readchequeutility import ReadCheque
from .GoogleCloudAIDataExtractor import GoogleCloudAIDataExtractor
from .OpenAIDataExtractor import OpenAIDataExtractor
import json

class DataExtractor:
    """
    A resource for extracting invoice data using invoice2data library
    """

    def __init__(self):
        self.file_storage_path = os.environ.get('de_storage_path', '/flask_downloads')
        self.template_folder = os.environ.get('de_templates_path', '/DocDataExtraction')

    def get(self):
        final_result = {}
        global result
        templates = ""
        input_reader = ""
        try:
            invoice_file_part = request.files.get('file_0', None)

            if not invoice_file_part:
                raise Exception('Invoice file not found in request payload')

            logger.log(f"inside get  {invoice_file_part}","0")
            json_Datas = request.args.get('jsonData')
            jsonData = json.loads(json_Datas)
            proc_mtd = ""

            
            if 'extract_templ' in jsonData.keys():
                given_temp_path = jsonData['extract_templ']
                
            if 'proc_mtd' in jsonData.keys():
                proc_mtd = jsonData['proc_mtd']
                proc_mtd_value = proc_mtd.split("-")

            logger.log(f"inside get:extract_templ:given_temp_path[{given_temp_path}]","0")
            if given_temp_path:
                if given_temp_path != 'DocDataExtraction': 
                    self.template_folder =  self.template_folder +'/'+given_temp_path+'/'

            logger.log(f"inside get template_folder[{self.template_folder}]","0")

            filename = invoice_file_part.filename
            file_path = os.path.join(self.file_storage_path, invoice_file_part.filename)
            logger.log(f"inside file_path  {file_path}","0")
            
            if '.TXT' in filename or '.txt' in filename or '.PDF' in filename or '.pdf' in filename or '.xls' in filename or '.xlsx' in filename or '.docx' in file_path or '.DOCX' in file_path:
                input_reader = request.args.get('input_reader', 'pdftotext')

            if '.png' in filename or '.PNG' in filename or '.jpg' in filename or '.JPG' in filename or '.jpeg' in filename or '.JPEG' in filename:
                input_reader = request.args.get('input_reader', 'tesseract')

            logger.log(f"Read Image  file using tesseract::input_reader:{input_reader}","0")

            Path(self.file_storage_path).mkdir(parents=True, exist_ok=True)
            
            invoice_file_part.save(file_path)

            if '.TXT' in filename or '.txt' in filename:
                dot_ind = filename.rindex('.')
                only_name = filename[:dot_ind]

                html_file_name = self.file_storage_path + "/" + only_name + ".html"
                output_file_name = self.file_storage_path + "/" + only_name + ".pdf"
                with open(file_path) as file:
                    with open(html_file_name, "w") as output:
                        file = file.read()
                        file = file.replace("\n", "<br>")
                        output.write(file)

                pdfkit.from_file(html_file_name, output_file_name)
                try:
                    os.remove(file_path)
                    file_path = os.path.join(html_file_name)
                    os.remove(file_path)
                except Exception as ex:
                    logger.log(f"DataExtractor: Exception while removing file {ex}","0")

                file_path = os.path.join(self.file_storage_path, output_file_name)
                
            if '.PDF' in filename or '.pdf' in filename and not given_temp_path == 'Visiting_Card':
                logger.log(f"Read pdf file","0")
                import fitz
                from pdf2image import convert_from_path
                file_path = os.path.join(self.file_storage_path, invoice_file_part.filename)
                pdf_file = fitz.open(file_path)
                for page_index in range(len(pdf_file)):
                    page = pdf_file[page_index]
                    image_list = page.getImageList()
                logger.log(f"{page.getImageList()}","0")
                
                if image_list: 
                    logger.log(f"[+] Found a total of {len(image_list)} images in page {page_index}","0")
                    input_reader = request.args.get('input_reader', 'tesseract')
                    new_img_file_path = os.path.join(self.file_storage_path, 'out.jpg')
                    logger.log(f"file_path--[{file_path}],new_img_file_path[{new_img_file_path}]","0")
                    images = convert_from_path(file_path, 200)
                 
                    for page in images: 
                        page.save(new_img_file_path, 'JPEG')
                else:
                    logger.log(f"[!] No images found on page {page_index}","0")  

            from invoice2data import extract_data
            from invoice2data.extract.loader import read_templates

            logger.log(f"template_Name [{given_temp_path}]","0")
            if not given_temp_path == 'Visiting_Card':
                logger.log(f"Read::self.template_folder: {self.template_folder}","0")
                if os.path.exists(self.template_folder):
                    templates = read_templates(self.template_folder)
                logger.log(f"Read::self.template_folder: {templates}","0")
                if len(input_reader) > 0:
                    input_reader_module = self.get_input_reader_module(input_reader)
                    logger.log(f"input_reader_module :{input_reader_module}","0")

            input_document_type = request.args.get('input_document_type', '')
            logger.log(f"input_document_type [ {input_document_type} ]","0")

            if input_document_type == 'cheque':
                read_cheque = ReadCheque()
                result = read_cheque.read_cheque_details(file_path, templates, input_reader_module)
            elif given_temp_path == 'Visiting_Card':
                result = extract(file_path)
            else:
                try:
                    if 'GC' in proc_mtd_value[1]:
                        googlecloudaiprocess = GoogleCloudAIDataExtractor()
                        result = googlecloudaiprocess.Data_Process(file_path=file_path, templates=templates, input_reader_module=input_reader_module,template_folder=self.template_folder)

                    elif 'AI' in proc_mtd_value[1]:
                        openaidataextractor = OpenAIDataExtractor()
                        result = openaidataextractor.OpenAIDataExtract(file_path=file_path,jsonData=jsonData,templates=templates)
                        logger.log(f"Result !!!!!!!!!!!!!!!!!!!!!! 216","0")
                    else:
                        result = extract_data(invoicefile=file_path,templates=templates,input_module=input_reader_module)
                except Exception as e:
                    logger.log(f"Issue:::  {e}","0")

            try:
                os.remove(file_path)
            except Exception as ex:
                logger.log(f"DataExtractor: Exception while removing file  {ex}","0")

            logger.log(f"result  {str(result)}" ,"0" )

            if 'AI' not in proc_mtd_value[1]:
                for key, value in result.items():
                    if key == "year_of_birth":
                        if value:
                            logger.log(f"{value}","0")
                            values = "1/1/"+str(value)
                            result["dob"] = values
            
            logger.log(f"result::{str(result)}","0")
             
            if 'AI' not in proc_mtd_value[1]:
                if not isinstance(result, bool):
                    result = self._reform_result(result)

            final_result['status'] = 1
            final_result['result'] = result
        except Exception as ex:
            final_result['status'] = 0
            final_result['error'] = str(ex)

        return final_result

    @staticmethod
    def get_input_reader_module(input_reader):
        if input_reader == 'pdftotext':
            from invoice2data.input import pdftotext
            return pdftotext
        elif input_reader == 'pdfminer':
            from invoice2data.input import pdfminer_wrapper
            return pdfminer_wrapper
        elif input_reader == 'tesseract':
            from invoice2data.input import tesseract
            return tesseract

        raise Exception('Invalid input reader "{}"'.format(input_reader))

    @staticmethod
    def _reform_result(result):
        if result is None:
            return '{}'

        result_copy = {}

        for prop in result:
            result_copy[prop] = str(result[prop])

        return result_copy
