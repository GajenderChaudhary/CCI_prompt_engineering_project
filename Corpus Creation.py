import pypdfium2 as pdfium
import os
import pytesseract
import glob
import shutil
import timeit
from tqdm import tqdm
import PIL
from PIL import Image

# Convert the UID pdf files to image
cci_uid_path= r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/cci_uid"

# Load the absolute path of each UID pdf file.
os.chdir(cci_uid_path)
abs_path = list() # has absolute path to all the files
for files in tqdm(glob.iglob('**/*.pdf', recursive = True)):
    file_path = os.path.join(cci_uid_path, files)
    abs_path.append(file_path)
print(abs_path)

# Generate Image 
image_path = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/cci_order_images"
for files in tqdm(abs_path):
    pdf = pdfium.PdfDocument(files)
    print(files)
    n_pages = len(pdf) # get the number of the pages in the pdf
    for page_number in range(n_pages):
        page = pdf.get_page(page_number)# get page from the pdf)
        pil_image = page.render(scale=4) # scale = 1 equals 72 dpi resolution - bitmap of page
        image = pil_image.to_pil()
        # image.show() 
        if not os.path.isdir(os.path.join(image_path,files[65:-4])): # make a directory if not exist
            os.makedirs(os.path.join(image_path,files[65:-4]))
        image.save(f"{image_path}/{files[65:-4]}/{files[65:-4]}_{page_number+1}.png")

# Text Extraction Code Pt.2

# Tesseract Engine Path
pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"

# Image path 
images_path = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/cci_order_images"
os.chdir(images_path)
all_img_path = list()
for img_path in glob.iglob("**/*.png", recursive = True):
    full_path = os.path.join(images_path,img_path)
    all_img_path.append(full_path)

# Text Output function - Input (Image) and Output - (Text file)
txt_output_path = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/cci_order_txt_files"
def write_UID_txt_file(img_path, text):
    os.chdir(txt_output_path) #output folder
    file_name = os.path.basename(img_path) # Return the final file name
    UID = f"{file_name[:-4]}.txt"
    fh = open(UID, "w", encoding = "utf=8")
    fh.write(text)
    fh.close()
    
def img_to_string(image_path):
    return pytesseract.image_to_string(Image.open(image_path)) # return string

# apply the function on each image and generate the text file
error = list()
for i, img_path in tqdm(enumerate((all_img_path))):
    log = i
    try:
        txt = img_to_string(img_path)
        write_UID_txt_file(img_path, txt)
    except Exception as e:
        error.append(e)


# Merge the text files of each order in sequence

# Load the path of text files
txt_files_path = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/cci_order_txt_files"
os.chdir(txt_files_path)
txt_files_list = list() # list of list
for txt_files in glob.iglob("**/*.txt", recursive = True):
   # txt_files.split("_") # list of all UID components -5 components - year, month, snum, onum, pagenumber with extension. For example, '2022_10_12_1_252.txt'
    txt_files_list.append(txt_files)

print(len(txt_files_list))

# 5 components of UID till here - year, month, snum, onum, pagenumber with extension. For example, '2022_10_12_1_252.txt'

same_file_dict = dict() # {UID: [all the page text collection]}
for i, file in enumerate(txt_files_list):
    comp_UID = file.split("_") # list of all UID components -5 components - year, month, snum, onum, pagenumber with extension. For example, '2022_10_12_1_252.txt'
    UID = f"{comp_UID[0]}_{comp_UID[1]}_{comp_UID[2]}_{comp_UID[3]}" # if the first four components are the same, then it belongs to the same UID. 
    if UID in same_file_dict:
        same_file_dict[UID].append(file) # send the related page text of an order identified through UID to same collection with key - UID
    else:
        same_file_dict[UID] = [file] # in case no appending has been done

# Write the function that takes in list of file names for a uid and returns a orderly arranged tuple - sort the list of pages text
def arrange_list_to_ordered_tuple(liist):
    pg_dict = dict()
    for i in liist:
        page_no = i.split("_")[4][:-4]
        pg_dict[page_no] = i
    sort_dict = dict(sorted(pg_dict.items(), key=lambda x: int(str(x[0])))) # treat the sort in int not string format
    # Make sure to convert the string to int before sorting as string would sort 1,10, 100, instead of 1,2,3,4,etc.
    ordered_tup = tuple()
    for k,v in sort_dict.items():
        ordered_tup += (v,)
    return ordered_tup

# sorted dict
arranged_file = dict()
for k,v in same_file_dict.items():
    arranged_file[k] = arrange_list_to_ordered_tuple(v)

# Output the generated Corpus
output_path = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/final_corpus (2010 - 2022)"
txt_files_path = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/cci_order_txt_files"

# Writing a folder is easy. 
for k,v in arranged_file.items():
    for i in v: # i - UID,  v - list of sorted text files associated with it.
        if f"{k}.txt" in os.listdir(output_path):
            print(i)
            fullfile_path = os.path.join(txt_files_path, i) # 
            with open(fullfile_path, 'r', encoding = "utf-8") as readfile:
                txt = readfile.read()
                readfile.close()
            with open(f'{output_path}/{k}.txt', 'a', encoding = "utf-8") as file:
                file.write(f"\n [NEW PAGE] \n {txt}")
        else: # if it is the first write
            print(f"in else block {i}")
            print(f"{output_path}/{k}.txt")
            fullfile_path = os.path.join(txt_files_path, i)
            with open(fullfile_path, 'r', encoding = "utf-8") as readfile:
                txt = readfile.read()
                readfile.close()
            with open(f'{output_path}/{k}.txt', 'a', encoding = "utf-8") as file:
                file.write(f" {txt}")

# The output is 1162 text files that is the whole corpus. 
