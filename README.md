# CCI_prompt_engineering_project

Author: Gajender Chaudhary

Mail: gajenderchaudhary@protonmail.com, gajender.chaudhary@sopp.iitd.ac.in

## Project Details

This project is a sub-part of a Ph.D. thesis at School of Public Policy, IIT Delhi, that maps out the evolution of competition policy in India through primary analysis of Competition
Commission of India and its interaction with global trends. This is a work in progress undergoing a trial-and-error approach where different computational techniques are being explored to optimize the relevant information that can be extracted from the available CCI orders and its linking with the larger political economy trends in India. The orders passed by the Competition Commission of India are downloaded from the Competition Commission of India website and have been queried using prominent OpenAI Models like GPT-3.5 Turbo, and GPT-4.

Till now in this project (May 2024), various prompts have been tested on the CCI orders to create a performance assessment of these models on such publicly available documents. There are several lessons learned in this project till now and scope for improvement has been identified. However, the code and workflow shared in this repository can serve as useful guide for others to pursue such engagements of their own.  

## Data Description

The orders downloaded from the Competition Commission of India website are referred to as antitrust orders, as they are meant to address the issue of anti-competitive agreements under section 3 of the CCI Act, 2002, and abuse of dominant position under section 4 of CCI Act, 2002. 

There are a total of **1162** CCI documents for the period of 2010 to 2022 which are mainly composed of the following sections: Section 26(1), Section 26(2), Section 26(6), and Section 27 which represent different stages of the case progression and the outlook of the judgment. 

- orders under section 27 acknowledge some violations of the CCI Act after an internal investigation by Director General and hence are labelled as Guilty Orders,

- while orders under section 26(1) represent a prima facie acceptance of the case for further investigation by the Director General with a decision to be taken after an internal investigation,

- Section 26(2) is the order that does not accept the prima facie merit of the case to be considered for the violation of the CCI Act. 

- Section 26(6) is the closure of the case without a guilty verdict after an internal investigation by the Director General has been carried out. 

Apart from these four major types of documents, there are other orders present in the total set of documents, which include Dissent Judgements, Orders under section 26(8), Supplementary orders under section 33, and section 48 of the act. 


## Project Workflow

Till now, this project has gone through the following stages: 1) Unique ID assignment to each order and overall Corpus Creation through OCR, 2) Query Design and General Information Extraction from these orders, and 3) further processing of this information to classify the Orders and generate various trends. Following is the elaboration of the workflow employed in this project. 

### 1.1. Organization of the CCI orders PDF files

Each order passed under section 3 and section 4 of the CCI ACt, 2002 has been downloaded from the website and organized based on the month and year in which it is passed. For example, the order passed in July month of 2014 will be kept in the July folder of 2014. The majority of the CCI orders are organized like this within the parent directory. 

In case, when there are two or more documents associated with each order such as dissent judgment or supplementary order. A directory(folder) is created to keep the collection together in the folder. 

### 1.2. Unique ID assignment

To keep track of the documents during the project workflow, each document has been assigned a Unique ID which overlaps with the organization of the pdf files and keep the unique nature of each document. The general format for unique ID assignment is (Year_Month_SerialNumber_OrderNumber).pdf. Such a unique ID assignment has four sub-identifiers which is best explained through two examples (fictional). 

Example 1 - A single order which has been passed in July of 2014 with Unique ID **2014_7_11_1.pdf**

This order was passed in July of 2014, hence 2014_7 in the first two identifiers represents the year and month. 

The third Identifier is the serial number assigned to the order which means that out of all the orders that were passed in July month of 2014. This order was assigned the 11th serial position during the Unique ID Assignment. 

The Fourth Identifier is supposed to handle a scenario where there is more than one document associated with a particular order. The Default value for this identifier is 1 which means the single document associated with that given order. In a scenario, when the number of documents in the folder exceeds one. The unique ID assignment will account for that. 

Example 2 - A document in 2017 month of April has 3 Documents. Then Unique ID of each document should be - 

2017_4_4_1.pdf,  2017_4_4_2.pdf,  2017_4_4_3.pdf.


### 1.3. Creation of Text Corpus out of CCI orders

Once each PDF file of CCI documents has been assigned a unique ID, the text within the document has been extracted through Optical Character Recognition which is two-stage process: 

1) Conversion of each page of the document to a High Pixel image.
2) Extract text from that image using Tesseract engine installed in the system.
3) Merge the text extracted from each page image of an order to create one text file of that given order.


#### 1.3.1. Conversion of PDF file pages to PNG images 

Each document page is converted to an image using the PyPDFium2 library. Documentation is available at the following link: https://pypi.org/project/pypdfium2/

Each page of the document further adds a page identifier to the unique ID in the output. For example, if a document has 3 pages. Each page would have the following Unique ID - 
2014_7_11_1_1.png,  2014_7_11_1_2.png,  2014_7_11_1_3.png

The page number at the end helps in reassembling the text file together at the end of this process in the sequence of the original PDF file.

In the render method of image generation of the pypdfium2 library, the scale is kept at 4 i.e., 288 dpi resolution. This value results in high resolution image with not much bigger file size to serve the text extraction purpose. 


#### 1.3.2. Extract text from the generated image

The Tesseract engine (version 5.3.4) is installed on the system path environment. Further, the Pytesseract library is employed to interact with the tesseract engine and extract the text from the PNG file. Documentation is available at the following link: 

1) Tesseract Engine - https://github.com/tesseract-ocr/tessdoc

2) Pytesseract - https://pypi.org/project/pytesseract/

#### 1.3.3. Merge the text files generated from each page

Once the text is extracted from a page image file for a given order and is available in the format: (YYYY_MM_Snum_Onum_page.txt). Each page text file of an order is assembled back together to create a single order text file.

### 2.1. Prompt Engineering Design and Process

Once the corpus is ready, it is open for interaction with the OpenAI Models like GPT-3.5 Turbo and GPT 4. Hence, the first step is to identify indicators and queries of interest that can be employed on such text files. For this set of orders, the following dimensions were identified: Descriptive Information (Date of the order, Case No., Informant and Opposite Party, Section No., CCI members who presided over that order, Penalty amount), Inferential Information (Industrial Category to which the order belongs, Regional Representation), General Summarization Task, Extractive Information Task (relevant quotes from the order). 

Based on the above-identified dimension, prompts were developed and refined to extract the desired output while keeping in mind the guidelines provided in the prompt engineering practice which prevents a check for Hallucination and nudge the performance of a model in a desired direction. 

#### Prerequisite for further process

- An OpenAI API key
- Intermediate Python
- Familiarity with MongoDB and JSON Schema
- Familiarity with OpenAI Chat Completion Function

### 2.2. Prompt Development and Function Code interaction

### 2.3.

### Full Workflow


## Success and Failures

### Results Review


## Remaining Work
