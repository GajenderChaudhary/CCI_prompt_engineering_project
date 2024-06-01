import openai
import pandas as pd
import os
import pymongo
import tiktoken
import glob
import json

corpus_directory = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/final_corpus (2010 - 2022)"

# Whole Prompt query code base lie on four class and some external input data - Request class, load class, tokenizer class, and Feature extraction class. 
# All the external input variable provide context for the text orders on which these query are run. 

# Request Class
class request():
    def __init__(self):
        import dotenv
        from dotenv import load_dotenv, find_dotenv
        _ = load_dotenv(find_dotenv()) # read local .env file
        openai.api_key  = os.environ['OPENAI_API_KEY']
        request.order_tokens = 0 # to keep track of token per each request
    def gpt_3_16k(self, messages, model = "gpt-3.5-turbo-0125"):
            response = openai.chat.completions.create(
                    model=model,
                    response_format = {"type": "json_object"},
                    messages=messages,
                    temperature=0, # this is the degree of randomness of the model's output 
                )
            self.input_tokens = response.usage.prompt_tokens 
            self.output_tokens = response.usage.completion_tokens
            self.total_tokens = response.usage.total_tokens
            print(f"GPT-3 - Input Prompt Tokens: {self.input_tokens}")
            print(f"GPT-3 - Input Prompt excluding order tokens: {self.input_tokens - request.order_tokens}")
            print(f"GPT-3 - Output Tokens: {self.output_tokens}")
            print(f"Total_tokens: {self.total_tokens}")
            return response.choices[0].message.content 
    # gpt_4 turbo-preview has rate limit of 30000tpm for a tier 1 user, I could not use it in the project. 
    # Instead I used gpt-4-1106-vision-preview
    def gpt_4(self, messages, model = "gpt-4-0125-preview"):  
            response = openai.chat.completions.create(
                model=model,
                response_format = {"type": "json_object"},
                messages=messages,
                temperature=0, # this is the degree of randomness of the model's output 
            )
            self.input_tokens = response.usage.prompt_tokens # this is giving only input tokens
            self.output_tokens = response.usage.completion_tokens
            self.total_tokens = response.usage.total_tokens
            print(f"GPT-4 - Input Prompt Tokens: {self.input_tokens}")
            print(f"GPT 4 - Output Tokens: {self.output_tokens}")
            print(f"Total_tokens: {self.total_tokens}")
            return response.choices[0].message.content 
    def any_model(self, msg):
        try:
            return self.gpt_3_16k(msg)
        except Exception as e:
            print(f"There was an exception raised in reaching out to GPT-3 16k. Moving to GPT-4")
            return self.gpt_4(msg)
        
# 2 Models are selected which should be more than enough for this exercise.

# To calculate the tokens
class tokenizer:
    def __init__(self):
        import tiktoken
        self.initial_encoding = "cl100k_base" # encoding most openai models use
    # Token count by base model
    def count_token_cl100k_base(self, text_input: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        token_integer_list = encoding.encode(text_input)
        num_tokens = len(token_integer_list)
        return num_tokens
    # token count by input model
    def count_token_by_model(self, text_input: str, encoding_model: str) -> int: # set a default encoding model as gpt-3.5-turbo
        try:
            encoding = tiktoken.encoding_by_model(encoding_model)
        except:
            encoding = tiktoken.get_encoding("cl100k_base")
        token_integer_list = encoding.encode(text_input)
        num_tokens = len(token_integer_list)
        return num_tokens
   # Token chunking
    def token_chunks(self, text_input, encoding_model):
        try:
            encoding = tiktoken.encoding_by_model(encoding_model)
        except:
            encoding = tiktoken.get_encoding("cl100k_base")
        token_integer_list = encoding.encode(text_input)
        token_chunks = [encoding.decode_single_token_bytes(token) for token in token_integer_list]
        return token_chunks

# Read the text file in an object and keep the general token count. 
class load(tokenizer):
    def __init__(self, txt_file_name):
        super().__init__() # inherit the tokenizer class
        # Path where all your files are stored.(New path will be set as more files are included and refined within th
        self.corpus_path = r"/Users/gajenderchaudhary/Work/phd_work/Jan-May 2024/final_corpus (2010 - 2022)"
        if os.getcwd() not in self.corpus_path:
            os.chdir(self.corpus_path)
            print(f"Directory Changed from {os.getcwd()} to {self.corpus_path}")
        with open(txt_file_name, 'r', encoding = "utf-8") as file:
            self.text = file.read() 
        #Count the tokens using tiktoken encoding
        self.length_token_cl100k_base = self.count_token_cl100k_base(self.text) # you are keeping the general token count at the initialization.

# Feature Extraction Class

## Input Variables and Data

dispute = """

CHAPTER II PROHIBITION OF CERTAIN AGREEMENTS, ABUSE OF DOMINANT POSITION AND REGULATION OF COMBINATIONS 

Prohibition of agreements Anti-competitive agreements

Section 3. 
(1) No enterprise or association of enterprises or person or association of persons shall enter into any agreement in respect of production, supply, distribution, storage, acquisition or control of goods or provision of services, which causes or is likely to cause an appreciable adverse effect on competition within India. 
(2) Any agreement entered into in contravention of the provisions contained in subsection (1) shall be void. 
(3) Any agreement entered into between enterprises or associations of enterprises or persons or associations of persons or between any person and enterprise or practice carried on, or decision taken by, any association of enterprises or association of persons, including cartels, engaged in identical or similar trade of goods or provision of services, which— (a) directly or indirectly determines purchase or sale prices; (b) limits or controls production, supply, markets, technical development, investment or provision of services; (c) shares the market or source of production or provision of services by way of allocation of geographical area of market, or type of goods or services, or number of customers in the market or any other similar way; (d) directly or indirectly results in bid rigging or collusive bidding, shall be presumed to have an appreciable adverse effect on competition: Provided that nothing contained in this sub-section shall apply to any agreement entered into by way of joint ventures if such agreement increases efficiency in production, supply, distribution, storage, acquisition or control of goods or provision of services. 

Explanation.—For the purposes of this sub-section, “bid rigging” means any agreement, between enterprises or persons referred to in sub-section (3) engaged in identical or similar production or trading of goods or provision of services, which has the effect of eliminating or reducing competition for bids or adversely affecting or manipulating the process for bidding 

(4) Any agreement amongst enterprises or persons at different stages or levels of the production chain in different markets, in respect of production, supply, distribution, storage, sale or price of, or trade in goods or provision of services, including— (6) (a) tie-in arrangement; (b) exclusive supply agreement; (c) exclusive distribution agreement; (d) refusal to deal; (e) resale price maintenance, shall be an agreement in contravention of sub-section (1) if such agreement causes or is likely to cause an appreciable adverse effect on competition in India. Explanation.—For the purposes of this sub-section,— (a) “tie-in arrangement” includes any agreement requiring a purchaser of goods, as a condition of such purchase, to purchase some other goods; (b) “exclusive supply agreement” includes any agreement restricting in any manner the purchaser in the course of his trade from acquiring or otherwise dealing in any goods other than those of the seller or any other person; (c) “exclusive distribution agreement” includes any agreement to limit, restrict or withhold the output or supply of any goods or allocate any area or market for the disposal or sale of the goods; (d) “refusal to deal” includes any agreement which restricts, or is likely to restrict, by any method the persons or classes of persons to whom goods are sold or from whom goods are bought; (e) “resale price maintenance” includes any agreement to sell goods on condition that the prices to be charged on the resale by the purchaser shall be the prices stipulated by the seller unless it is clearly stated that prices lower than those prices may be charged. 

(5) Nothing contained in this section shall restrict— (i) the right of any person to restrain any infringement of, or to impose reasonable conditions, as may be necessary for protecting any of his rights which have been or may be conferred upon him under— (a) the Copyright Act, 1957 (14 of 1957); (b) the Patents Act, 1970 (39 of 1970); (c) the Trade and Merchandise Marks Act, 1958 (43 of 1958) or the Trade Marks Act, 1999 (47 of 1999); (d) the Geographical Indications of Goods (Registration and Protection) Act, 1999 (48 of 1999); (e) the Designs Act, 2000 (16 of 2000); (f) the Semi-conductor Integrated Circuits Layout-Design Act, 2000 (37 of 2000); (ii) the right of any person to export goods from India to the extent to which the agreement relates exclusively to the production, supply, distribution or control of goods or provision of services for such export.

Prohibition of abuse of dominant position 

Abuse of dominant position 
Section 4. 
(1) No enterprise or group shall abuse its dominant position. 
(2) There shall be an abuse of dominant position under sub-section (1), if an enterprise or a group.—- (a) directly or indirectly, imposes unfair or discriminatory— (i) condition in purchase or sale of goods or service; or (ii) price in purchase or sale (including predatory price) of goods or service. 

Explanation.— For the purposes of this clause, the unfair or discriminatory condition in purchase or sale of goods or service referred to in sub-clause (i) and unfair or discriminatory price in purchase or sale of goods (including predatory price) or service referred to in sub-clause (ii) shall not include such discriminatory condition or price which may be adopted to meet the competition; or (b) limits or restricts— (i) production of goods or provision of services or market therefor; or (ii) technical or scientific development relating to goods or services to the prejudice of consumers; or (c) indulges in practice or practices resulting in denial of market access  in any manner; or (d) makes conclusion of contracts subject to acceptance by other parties of supplementary obligations which, by their nature or according to commercial usage, have no connection with the subject of such contracts; or (e) uses its dominant position in one relevant market to enter into, or protect, other relevant market. 

Explanation.—For the purposes of this section, the expression— (a) “dominant position” means a position of strength, enjoyed by an enterprise, in the relevant market, in India, which enables it to— (i) operate independently of competitive forces prevailing in the relevant market; or (ii) affect its competitors or consumers or the relevant market in its favour. (b) “predatory price” means the sale of goods or provision of services, at a. price which is below the cost, as may be determined by regulations, of production of the goods or provision of services, with a view to reduce competition or eliminate the competitors. (c)“group” shall have the same meaning as assigned to it in clause (b) of the Explanation to section 5.] 

"""

legal_procedure = """

Procedure for inquiry under section 19 

26. (1) On receipt of a reference from the Central Government or a State Government or a statutory authority or on its own knowledge or information received under section 19, if the Commission is of the opinion that there exists a prima facie case, it shall direct the Director General to cause an investigation to be made into the matter: Provided that if the subject matter of an information received is, in the opinion of the Commission, substantially the same as or has been covered by any previous information received, then the new information may be clubbed with the previous information. 
26. (2) Where on receipt of a reference from the Central Government or a State Government or a statutory authority or information received under section 19, the Commission is of the opinion that there exists no prima facie case, it shall close the matter forthwith and pass such orders as it deems fit and send a copy of its order to the Central Government or the State Government or the statutory authority or the parties concerned, as the case may be. 
26. (3) The Director General shall, on receipt of direction under sub-section (1), submit a report on his findings within such period as may be specified by the Commission. 
26. (4) The Commission may forward a copy of the report referred to in sub section(3) to the parties concerned: Provided that in case the investigation is caused to be made based on reference received from the Central Government or the State Government or the statutory authority, the Commission shall forward a copy of the report referred to in sub- section (3) to the Central Government or the State Government or the statutory authority, as the case may be. 
26. (5) If the report of the Director General referred to in sub-section (3) recomends that there is no contravention of the provisions of this Act, the Commission shall invite objections or suggestions from the Central Government or the State Government or the statutory authority or the parties concerned, as the case may be, on such report of the Director General. 
26. (6) If, after consideration of the objections and suggestions referred to in sub section (5), if any, the Commission agrees with the recommendation of the Director General, it shall close the matter forthwith and pass such orders as it deems fit and communicate its order to the Central Government or the State Government or the statutory authority or the parties concerned, as the case may be. 
26. (7) If, after consideration of the objections or suggestions referred to in sub section (5), if any, the Commission is of the opinion that further investigations is called for, it may direct further investigation in the matter by the Director General or cause further inquiriy to be made by in the matter or itself proceed with further inquiry in the matter in accordance with the provisions of this Act. 
26. (8) If the report of the Director General referred to in sub-section (3) recommends that there is contravention of any of the provisions of this Act, and the Commission is of the opinion that further inquiry is called for, it shall inquire into such contravention in accordance with the provisions of this Act.]

Section 27 - Orders by Commission after inquiry into agreements or abuse of dominant position. 

Section 27

Where after inquiry the Commission finds that any agreement referred to in section 3 or action of an enterprise in a dominant position, is in contravention of section 3 or section 4, as the case may be, it may pass all or any of the following orders, namely:— 

(a) direct any enterprise or association of enterprises or person or association of persons, as the case may be, involved in such agreement, or abuse of dominant position, to discontinue and not to re-enter such agreement or discontinue such abuse of dominant position, as the case may be; 

(b) impose such penalty, as it may deem fit which shall be not more than ten percent of the average of the turnover for the last three preceding financial years, upon each of such person or enterprises which are parties to such agreements or abuse: Provided that in case any agreement referred to in section 3 has been entered into by a cartel, the Commission may impose upon each producer, seller, distributor, trader or service provider included in that cartel, a penalty of up to three times of its profit for each year of the continuance of such agreement or ten percent. of its turnover for each year of the continuance of such agreement, whichever is higher. 

(c) Omitted by Competition (Amendment) Act, 2007] 

(d) direct that the agreements shall stand modified to the extent and in the manner as may be specified in the order by the Commission; 

(e) direct the enterprises concerned to abide by such other orders as the Commission may pass and comply with the directions, including payment of costs, if any;

(f) Omitted by Competition (Amendment) Act, 2007

(g) pass such other order or issue such directions as it may deem fit. Provided that while passing orders under this section, if the Commission comes to a finding, that an enterprise in contravention to section 3 or section 4 of the Act is a member of a group as defined in clause (b) of the Explanation to section 5 of the Act, and other members of such a group are also responsible for, or have contributed to, such a contravention, then it may pass orders, under this section, against such members of the group.
"""

legal_category = ["26(1)", "26(2)", "26(3)", "26(4)", "26(5)", "26(6)", "26(7)", "26(8)", "27"]


indian_regions = {
    'North': ['Jammu and Kashmir', 'Himachal Pradesh', 'Punjab', 'Uttarakhand', 'Haryana', 'Uttar Pradesh', 'Delhi'],
    'South': ['Andhra Pradesh', 'Telangana', 'Karnataka', 'Tamil Nadu', 'Kerala'],
    'East': ['West Bengal', 'Odisha', 'Jharkhand', 'Bihar', 'Sikkim', 'Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Tripura'],
    'West': ['Rajasthan', 'Gujarat', 'Maharashtra', 'Goa'],
    'Central': ['Madhya Pradesh', 'Chhattisgarh'],
    'Northeast': ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Tripura', 'Sikkim'],
}

query = f"""

Question1. When did this order passed? Return date in the following format: DD-MM-YYYY

Question2. Return the case number of the order.

Question3. Who is/are the informant and opposite party/s in this case? Return names in the following format: 
\ Informant: [Name/s], Opposite Party: [Name/s]

Question4. Who were the members (Judges) that presided over this order? Return their names.

Question5. Under which of the following legal procedure {legal_category} context of which is provided in the system guideline this order belongs to. Return relevant section and supporting evidence for this cla

Question5. "Were there any precedents cited in the order?

Question6. Is there a Penalty imposed on the parties? Return No if there is no penalty. \
If yes then return penalty amount associated with a party name. Return empty if not sure

Question7. "What are the specific allegations made by the informant?" 

Question8. "What is the defense argument in favour of the opposite party?".

Question9. What are economic arguments used in the Judgement. Return Nil if no such arguments present.  

Question11. Which region would you assign to the order from the following category delimited by $$$. $$${indian_regions}$$$? Return both the broad region, sub-region and rationale.

Question12. Which broad industrial Categories this order belongs to? Return both the broad category, sub-categories if needed and rationale.

Question13. Which of the following dispute {dispute} does this order belongs to? Return answer and rationale.  

Question14. Is it a Private vs Government, Government vs Government, or private vs private case. Provide answer by each party ownership status and separate rationale.

Question15. Provide summary of the order as elaborative as required.

Question16. Provide extractive summarization of the order. Collect relevant extracts from this order in a list.

Question17. Is there any interesting worth highlighting from this order. Return nil if there is none. 

"""

# Feature extraction class

class feature_extraction(request, load):
    def __init__(self, txt_file_name: str):
        request.__init__(self)
        load.__init__(self, txt_file_name)
        request.order_tokens = self.length_token_cl100k_base # updating the order token length in the request class.
        print(f"Tokens in the order: {self.length_token_cl100k_base}")
        self.system_guideline = f"""You are an assistant who is looking at the orders \
        passed by competition commission of India. You are supposed to extract \
        relevant information from the input orders in a valid json output.\ 
        The further legal background of relevant sections are delimited by triple hash. \
        ### {dispute} ### {legal_procedure} ###"""
        self.del1 = "####"
        self.del2 = "****"
        self.uniqueID= txt_file_name
    def general_extraction(self):
        # This prompt responds based on the questions articulated above. 
        prompt = f"""Go through the order delimited by {self.del2} and answer the \
        following questions which is delimited by {self.del1}. Return the output in the \
        valid json format which can further processed downstream with corresponding question number as key and value as answer. 
        {self.del1}
        {query}
        {self.del1}
        {self.del2}
        {self.text}
        {self.del2}
        """
        messages = [{"role": "system", "content": self.system_guideline},
                    {"role": "user", "content": prompt}]
        msg_tok_calc = "role system content role user content" + f" {self.system_guideline}" + f" {prompt}"
        message_token_count = tokenizer.count_token_cl100k_base(self, msg_tok_calc) #- This is giving wrong calculation
        print(f"Calculated Message token length: {message_token_count}")
        # Use input token count to direct the request.
        gen_answer = request.any_model(self, messages)
        print(gen_answer)
        self.prompt = prompt
        import json
        try: 
            json_ans = json.loads(gen_answer) # CONVERT JSON STRING TO DICT
            json_ans["_id"] = self.uniqueID
            json_ans["Input Tokens"] = self.input_tokens
            json_ans["Total Tokens"] = self.total_tokens
            json_ans["Output Tokens"] = self.output_tokens
            print("successful json conversion of the output!")
            return json_ans
        except:
            try:
                guideline = f"""You are supposed to correct the error in a json string for it to be transformed into json dict format using python json library."""
                json_query = f"""Following delimited by {self.del1} is the json response which is throwing the error. Correct it and provide the valid json output.\
                {self.del1} {gen_answer[0]} {self.del1} """
                msg = [{"role": "system", "content": guideline},
                    {"role": "user", "content": json_query}]
                ans_json = request.any_model(self, msg)
                json_ans_new = json.loads(gen_answer)
                json_ans_new["_id"] = self.uniqueID
                json_ans["Input Tokens"] = self.input_tokens
                json_ans["Total Tokens"] = self.total_tokens
                json_ans["Output Tokens"] = self.output_tokens
            except Exception as e:
                print(e)
                print("error retrieving json output")
                nil = {}
                return nil 
    def custom_prompt(self, system_guideline, prompt):
        msg = [{"role": "system", "content": system_guideline},
                    {"role": "user", "content": prompt}]
        ans = request.any_model(self, msg)
        return ans


# Batch wise processing

def create_batches(input_list, batch_size):
    return [input_list[i:i + batch_size] for i in range(0, len(input_list), batch_size)]

batches = create_batches(sorted(os.listdir(corpus_directory)), 100)
print(len(batches)) # Total 12 batches

# Iterate over each batch the following code and store the answer

# store the response in Mongo Database
client = pymongo.MongoClient("mongodb://localhost:27017/")  
db = client["cci_orders"]
collection = db["cci_v2_May2024_batch12"]
answer_batch12 = list()
error_log_batch12 = dict()
for i, file in tqdm(enumerate(batches[11])): # Manually iterated over each batch and supervised the performance for error and debugging purposes.
    try:
        print(file)
        file_instance = feature_extraction(file)
        ans = file_instance.general_extraction()
        result = collection.insert_one(ans)
        answer_batch12.append(result)
    except Exception as e:
        print(e)
        error_log_batch12[file] = e
    time.sleep(10)

# once the responses are stored for each batch. I manually supervised the excluded and missing responses where the error might have occurred and rerun the query for them. 
# At the end of all this, answers for the 3 orders could not be retrieved as the context window for those orders exceeds 128k length.  
