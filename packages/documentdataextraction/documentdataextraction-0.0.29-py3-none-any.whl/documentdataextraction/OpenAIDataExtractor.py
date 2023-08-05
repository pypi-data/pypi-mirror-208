import requests, json, traceback, openai
import os
from invoice2data import extract_data
from flask import request
import loggerutility as logger
from PIL import Image
from tempfile import TemporaryDirectory
from pdf2image import convert_from_path
import cv2
import pytesseract
import yaml
from .GenerateExtractTemplate import GenerateExtractTemplate
import pdfplumber
import pdftotext
import datetime
import docx2txt
import pandas as pd
import pathlib
from striprtf.striprtf import rtf_to_text

class OpenAIDataExtractor:

    def pytesseract_ocr(self,PDF_file):
        image_file_list = []
        with TemporaryDirectory() as tempdir:
            pdf_pages = convert_from_path(PDF_file, 500)
            for page_enumeration, page in enumerate(pdf_pages, start=1):
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg"
                page.save(filename, "JPEG")
                image_file_list.append(filename)

            for image_file in image_file_list:
                text = str(((pytesseract.image_to_string(Image.open(image_file)))))

            return text
        
    def pdfplumber_ocr(self,PDF_file):
        OCR_Text=''
        pdffile = pdfplumber.open(PDF_file)
        for i in range(len(pdffile.pages)):
            OCRTEXT = pdffile.pages[i].extract_text()
            OCR_Text = OCR_Text +'\n'+ OCRTEXT
        
        return OCR_Text
    
    def pdftotext_ocr(self,PDF_file):
        with open(PDF_file, "rb") as f:
            pdf = pdftotext.PDF(f)

        OCR_Text = "\n\n".join(pdf)
        return OCR_Text

    def OpenAIDataExtract(self,file_path : str, jsonData : str, templates : str):
        try:
            
            ent_code = ""
            ent_name = ""
            mandatory = []

            logger.log(f"json data   ::::: 61 {jsonData}","0")
            logger.log(f"OpenAIDataExtract all Parameters::  \n{locals()}\n","0")
            
            if 'ai_proc_templ' in jsonData.keys():
                ai_proc_templ = jsonData['ai_proc_templ']
            
            if 'proc_api_key' in jsonData.keys():
                proc_api_key = jsonData['proc_api_key']

            if 'userId' in jsonData.keys():
                userId = jsonData['userId']
                
            if 'objName' in jsonData.keys():
                objName = jsonData['objName']

            if 'ent_code' in jsonData.keys():
                ent_code = jsonData['ent_code']

            if 'ent_name' in jsonData.keys():
                ent_name = jsonData['ent_name']
 
            if 'IS_OCR_EXIST' in jsonData.keys():
                IS_OCR_EXIST = jsonData['IS_OCR_EXIST']

            if 'ai_proc_variables' in jsonData.keys():
                ai_proc_variables = jsonData['ai_proc_variables']


            if isinstance(ai_proc_variables, str):
                ai_proc_variables = json.loads(ai_proc_variables)

            if ai_proc_variables:
                for val in ai_proc_variables["Details"]:
                    if val['mandatory'] == 'true':
                        mandatory.append(val['name'])
            
            logger.log(f"ai_proc_variables::::88> {ai_proc_variables}","0")
            
            if 'proc_mtd' in jsonData.keys():
                proc_mtd = jsonData['proc_mtd']
                proc_mtd_value = proc_mtd.split("-")
            
            OCR_Text = ""
            finalResult = ""
            self.result = {}
            df = None
            fileExtension = (pathlib.Path(file_path).suffix)
            logger.log(f"\nfileExtention::::> {fileExtension}","0")
            fileExtension_lower = fileExtension.lower()
            logger.log(f"\nfileExtention_lower()::::> {fileExtension_lower}","0")

            if IS_OCR_EXIST == 'false':
                logger.log(f"OCR Start !!!!!!!!!!!!!!!!!102","0")            
                if '.PDF' in file_path or '.pdf' in file_path:

                    if proc_mtd_value[0] == 'PP':
                        OCR_Text=self.pdfplumber_ocr(file_path)

                    elif proc_mtd_value[0] == 'PT':
                        OCR_Text=self.pdftotext_ocr(file_path)

                    elif proc_mtd_value[0] == 'PO':
                        OCR_Text=self.pytesseract_ocr(file_path)

                    logger.log(f"OpenAI pdf ocr ::::: {OCR_Text}","0")
                
                elif '.docx' in file_path or '.DOCX' in file_path:
                    OCR_Text = docx2txt.process(file_path)

                    logger.log(f"OpenAI DOCX ocr ::::: {OCR_Text}","0")

                # Added by SwapnilB for handling xls case on 28-Mar-23 [START]
                elif ".xls" in fileExtension_lower or ".xlsx" in fileExtension_lower:
                    logger.log(f"inside .xls condition","0")
                    df = pd.read_excel(file_path)
                    xls_ocr = df.to_csv()
                    OCR_Text = xls_ocr.replace(","," ")
                    logger.log(f"\nxls_ocr type ::::: \t{type(OCR_Text)}","0")
                    logger.log(f"\nxls_ocr ::::: \n{OCR_Text}\n","0")
                    
                elif ".csv" == fileExtension_lower :
                    logger.log(f"inside .csv condition","0")
                    df = pd.read_csv(file_path)
                    csv_ocr = df.to_csv()           # to handle multiple spaces between columns
                    OCR_Text = csv_ocr.replace(","," ")
                    logger.log(f"\ncsv_ocr type ::::: \t{type(OCR_Text)}","0")
                    logger.log(f"\ncsv_ocr ::::: \n{OCR_Text}\n","0")
                
                elif ".rtf" == fileExtension_lower :
                    logger.log(f"inside .rtf condition","0")
                    with open(file_path) as infile:
                        content = infile.read()
                        OCR_Text = rtf_to_text(content, errors="ignore")  # to handle encoding error
                    logger.log(f"\nrtf_ocr type ::::: \t{type(OCR_Text)}","0")
                    logger.log(f"\nrtf_ocr ::::: \n{OCR_Text}\n","0")
                
                # Added by SwapnilB for handling xls case on 28-Mar-23 [END]

                else:
                    path = file_path
                    image = cv2.imread(path, 0)
                    OCR = pytesseract.image_to_string(image)
                    logger.log(f"{OCR}","0")
                    OCR_Text = OCR
                
                logger.log(f"OCR End !!!!!!!!!!!!!!!!!156","0")
                if not ent_code and not ent_name:
                    logger.log(f"INSIDE entcode and entname not blank","0")
                    try:
                        if proc_mtd_value[0] == 'PT':
                            from invoice2data.input import pdftotext
                            input_module = pdftotext

                        elif proc_mtd_value[0] == 'PP':
                            # from invoice2data.input import pdfplumber
                            # input_module = pdfplumber
                            logger.log(f"PP !!!!!!!!!!!! 175","0")
                            from invoice2data.input import pdftotext
                            input_module = pdftotext

                        elif proc_mtd_value[0] == 'PO':
                            from invoice2data.input import tesseract
                            input_module =  tesseract
                    
                        logger.log(f"Template Extraction call Start !!!!!!!!!!!!!!!!!183","0")
                        resultdata = extract_data(invoicefile=file_path,templates=templates,input_module=input_module)
                        # resultdata = dict(resultdata)
                        logger.log(f"Template Extraction call End !!!!!!!!!!!!!!!!!111","0")
                        logger.log(f"Template extracted data  ::::: 186 {resultdata}","0")
                        logger.log(f"resultdata type  ::::: 187 {type(resultdata)}","0")

                        if isinstance(resultdata, bool) and mandatory != "":
                            self.result['OCR_DATA']=OCR_Text
                            self.result['isMandatoryExtracted']='false'
                            return self.result
                            # resultdata = {}
                        
                        resultdata['isTemplateExtracted']='true'

                        for valuesOfmandatory in mandatory:
                            print(valuesOfmandatory)
                            if valuesOfmandatory in resultdata:
                                if not resultdata[valuesOfmandatory]:  
                                    self.result['OCR_DATA']=OCR_Text
                                    self.result["EXTRACT_TEMPLATE_DATA"] = resultdata
                                    self.result['isMandatoryExtracted']='false'
                                    return self.result
                            
                        # resultdata['isTemplateExtracted']='true'
                        if 'ent_code' in resultdata.keys():
                            self.result["EXTRACT_TEMPLATE_DATA"] = resultdata
                            self.result['OCR_DATA']=OCR_Text
                            self.result['isMandatoryExtracted']='true'
                            return self.result
                            
                        
                    except Exception as e:
                        logger.log(f'\n Exception : {e}', "1")

            else:
                if 'OCR_DATA' in jsonData.keys():
                    OCR_Text = jsonData['OCR_DATA']

            if ai_proc_templ:
                if 'AID' in proc_mtd_value[1]:
                    logger.log(f"AID !!!!!!!!!!!! 204","0")
                    finalResult = self.extractdatausing_davinci(proc_api_key=proc_api_key, OCR_Text=OCR_Text, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables)
                    

                elif 'AIT' in proc_mtd_value[1]:
                    finalResult = self.extractdatausing_turbo(proc_api_key = proc_api_key, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables, OCR_Text = OCR_Text)
                
                self.result["EXTRACT_LAYOUT_DATA"] = finalResult
                self.result['OCR_DATA']=OCR_Text
            
            logger.log(f"Response Return !!!!!!!!!!!! 142","0")
            return self.result
            
        
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = self.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)
        
    def getErrorXml(self, descr, trace):
        errorXml = '''<Root>
                            <Header>
                                <editFlag>null</editFlag>
                            </Header>
                            <Errors>
                                <error type="E">
                                    <message><![CDATA['''+descr+''']]></message>
                                    <trace><![CDATA['''+trace+''']]></trace>
                                    <type>E</type>
                                </error>
                            </Errors>
                        </Root>'''

        return errorXml


    def getlayouttextaidata(self):
        try:
            result = {}
            final_result = {}
            mandatory = []
            finalResult = ""
            proc_api_key = ""
            ai_proc_templ = ""
            ent_name = ""
            ent_code = ""
            ent_type = ""
            OCR_Text = ""
            ai_proc_variables = ""
            
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"jsonData API openAI class::: !!!!!269 {jsonData}","0")

            if 'extract_templ' in jsonData.keys():
                given_temp_path = jsonData['extract_templ']
            
            if 'ent_code' in jsonData.keys():
                ent_code = jsonData['ent_code']
            
            if 'ent_type' in jsonData.keys():
                ent_type = jsonData['ent_type']

            if 'ent_name' in jsonData.keys():
                ent_name = jsonData['ent_name']

            if 'ai_proc_templ' in jsonData.keys():
                ai_proc_templ = jsonData['ai_proc_templ']

            if 'ai_proc_variables' in jsonData.keys():
                ai_proc_variables = jsonData['ai_proc_variables']

            if 'proc_api_key' in jsonData.keys():
                proc_api_key   = jsonData['proc_api_key']

            if 'userId' in jsonData.keys():
                userId = jsonData['userId']

            if 'objName' in jsonData.keys():
                objName = jsonData['objName']
            
            if 'proc_mtd' in jsonData.keys():
                proc_mtd = jsonData['proc_mtd']
                proc_mtd_value = proc_mtd.split("-")
            
            if 'OCR_DATA' in jsonData.keys():
                OCR_Text = jsonData['OCR_DATA']

            # if isinstance(ai_proc_variables, str):
            #     ai_proc_variable = json.loads(ai_proc_variables)

            # if ai_proc_variable:
            #     for val in ai_proc_variable["Details"]:
            #         if val['mandatory'] == 'true':
            #             mandatory.append(val['name'])


            if ai_proc_templ:
                if 'AID' in proc_mtd_value[1]:
                    finalResult = self.extractdatausing_davinci(proc_api_key=proc_api_key, OCR_Text=OCR_Text, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables)

                elif 'AIT' in proc_mtd_value[1]:
                    finalResult = self.extractdatausing_turbo(proc_api_key = proc_api_key, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables, OCR_Text = OCR_Text)
                
                ymlfilepath = "/"+(given_temp_path)+"/"+str(ent_name).strip().replace(" ","_").replace(".","")+".yml"
                
                if os.path.exists(ymlfilepath) == True:
                    os.remove(ymlfilepath)

                if ent_name and ent_code:
                    logger.log(f'\n[ Template creation Start time  305  :          {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
                    templatecreation = GenerateExtractTemplate()
                    templatecreation.generateHeaderTemplate(ymlfilepath,ent_name,ent_code,ent_type,ai_proc_variables,OCR_Text)
                    logger.log(f'\n[ Template creation End time  308  :          {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")

                result["EXTRACT_LAYOUT_DATA"] = finalResult
                final_result['status'] = 1
                final_result['result'] = result
        except Exception as ex:
            final_result['status'] = 0
            final_result['error'] = str(ex)
        logger.log(f"Return result value !!!!!!!!! 203 {final_result}","0")
        return final_result
    
    def extractdatausing_davinci(self,proc_api_key : str, OCR_Text : str , ai_proc_templ : str, ai_proc_variables : str):

        logger.log(f'\n[ Open ai starting time 131 :        {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
        openai.api_key = proc_api_key
        logger.log(f"\nai_proc_variables::::\n {ai_proc_variables}\n{type(ai_proc_variables)}","0")
        logger.log(f"\nai_proc_templ::::\n {ai_proc_templ}\n{type(ai_proc_templ)}","0")       
        logger.log(f"TYPE OF ai_proc_variables {type(ai_proc_variables)}","0")

        if isinstance(ai_proc_variables, str):
            ai_proc_variables = json.loads(ai_proc_variables)

        if ai_proc_variables:
            for val in ai_proc_variables["Details"]:
                if "<"+val["name"]+">" in ai_proc_templ:
                    ai_proc_templ = ai_proc_templ.replace("<"+val["name"]+">", val['defaultValue'])

        if '<DOCUMENT_DATA>' in ai_proc_templ:
            print(type(ai_proc_templ))
            ai_proc_templ = ai_proc_templ.replace('<DOCUMENT_DATA>',OCR_Text)
            logger.log(f'\n[ Open ai " model " Value              :      "text-davinci-003" ]', "0")
            logger.log(f'\n[ Open ai " prompt " Value             :      "{ai_proc_templ}" ]', "0")
            logger.log(f'\n[ Open ai " temperature " Value        :      "0" ]', "0")
            logger.log(f'\n[ Open ai " max_tokens " Value         :      "1800" ]', "0")
            logger.log(f'\n[ Open ai " top_p " Value              :      "1" ]', "0")
            logger.log(f'\n[ Open ai " frequency_penalty " Value  :      "0" ]', "0")
            logger.log(f'\n[ Open ai " presence_penalty " Value   :      "0" ]', "0")
            response = openai.Completion.create(
            model="text-davinci-003",
            prompt= ai_proc_templ,
            temperature=0,
            max_tokens=1800,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )

        else:

            logger.log(f'\n[ Open ai " model " Value              :      "text-davinci-003" ]', "0")
            logger.log(f'\n[ Open ai " prompt " Value             :      "{OCR_Text+ai_proc_templ}" ]', "0")
            logger.log(f'\n[ Open ai " temperature " Value        :      "0" ]', "0")
            logger.log(f'\n[ Open ai " max_tokens " Value         :      "1800" ]', "0")
            logger.log(f'\n[ Open ai " top_p " Value              :      "1" ]', "0")
            logger.log(f'\n[ Open ai " frequency_penalty " Value  :      "0" ]', "0")
            logger.log(f'\n[ Open ai " presence_penalty " Value   :      "0" ]', "0")
            response = openai.Completion.create(
            model="text-davinci-003",
            prompt= OCR_Text+'\n'+ai_proc_templ,
            temperature=0,
            max_tokens=1800,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        logger.log(f"Response openAI completion endpoint::::: {response}","0")
        finalResult=str(response["choices"][0]["text"])
        logger.log(f'\n [ Open ai completion time 171 :      {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
        logger.log(f"OpenAI completion endpoint finalResult ::::: {finalResult}","0")
        return finalResult


    def extractdatausing_turbo(self,proc_api_key: str, ai_proc_templ : str, ai_proc_variables : str, OCR_Text : str):
        logger.log(f"\nai_proc_variables::::\n {ai_proc_variables}\n{type(ai_proc_variables)}","0")
        logger.log(f"\nai_proc_templ::::\n {ai_proc_templ}\n{type(ai_proc_templ)}","0")

        if isinstance(ai_proc_variables, str):
            ai_proc_variables = json.loads(ai_proc_variables)

        if isinstance(ai_proc_templ, list):
            ai_proc_templ = json.dumps(ai_proc_templ)

        if ai_proc_variables:
            for val in ai_proc_variables["Details"]:
                if "<"+val["name"]+">" in ai_proc_templ:
                    ai_proc_templ = ai_proc_templ.replace("<"+val["name"]+">", val['defaultValue'].strip())

        openai.api_key = proc_api_key
        if '<DOCUMENT_DATA>' in ai_proc_templ:
            ai_proc_templ = ai_proc_templ.replace('<DOCUMENT_DATA>',OCR_Text).strip()
        
        # Overview call or Template creation call ai_proc_templ variable type is list and while uploading it's variable type is string
        if isinstance(ai_proc_templ, str):       
            ai_proc_templ = ai_proc_templ.replace('\n'," ")
            ai_proc_templ = json.loads(ai_proc_templ)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=ai_proc_templ,
            temperature=0.25,
            max_tokens=1800,
            top_p=0.5,
            frequency_penalty=0,
            presence_penalty=0,
            )
        finalResult = completion.choices[0]["message"]["content"]

        return finalResult

