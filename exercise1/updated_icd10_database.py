import sqlite3
import requests
import re
import string

# Step 1: Create list of Sanford ICD10 codes
with open("ICD10list_copy.txt", "r") as f1:
    lines_after_1 = f1.readlines()[1:]


lines_file = 0
icd10_dict = {}
patient_counts = [] #Will use this list for sanity check

for line in lines_after_1:

    lines_file = lines_file + 1

    result = line.split(' ') #Split each line by ' '. (Creates a list--the first item is the ICD10 code; the second item is the disease name/ number of Sanford diagnoses.)
    #print(result[0])

    result2 = line.split('\t') #Split each line by '\t'. (Creates a list --the first item is the ICD10 code/ disease name; the second item is the number of Sanford diagnoses.)
    #print(result2)

    count = result2[1].strip('\n') #Extracts only the number of Sanford diagnoses from result2[]
    #print(count)
    # def is_number(count): #Function checks to make sure that each count extracted is actually an integer. (A sanity check to ensure that my code is running the way I think it is)
    #     try:
    #         int(count.replace(',' , ''))
    #     except ValueError:
    #         print("False")
    # is_number(count)

    result3 = re.split(r'^[\"]*[A-Z][0-9]*[A-Z]*[.]*[0-9]*[A-Z]*[0-9]*[A-Z]*\s|\t[0-9]+[,]*[0-9]*\n*', line) #Regular expression to extract only the disease name from each line.
                                                                                                         #2/21/2018: detected problem with regex. Fixed and defined function to check.
    #print(result3)
    # def check_regex(result3): #Function checks to make sure that regex functioned as expected
    #     if result3[0] != '':
    #         print(result3[0])
    # check_regex(result3)

    abbreviated_name = result3[1].strip().translate(str.maketrans('', '', string.punctuation)).lower()
    # def check_name(abbreviated_name): #Function checks to make sure that abbreviated name is not an empty string.
    #     if abbreviated_name == '':
    #         print('failed')

    icd10_dict.update({result[0]: [count, abbreviated_name]}) #Creates a dictionary. KEY=ICD10 code; VALUE= [number of Sanford diagnoses, disease name as it appears on EDA spreadsheet]

#print(icd10_dict)
# for key, val in icd10_dict.items(): #Double check dictionary to make sure that val[1] (i.e. abbreviated_name) is not an empty string.
#     if val[1] == '':
#         print('failed')

# Step 2: Create database
conn = sqlite3.connect('updated_icd10.db')
c = conn.cursor()
#
# c.execute("""CREATE TABLE IF NOT EXISTS ICD10_codes (
#             ID TEXT PRIMARY KEY,
#             name TEXT,
#             count INTEGER
#             )""")
#
# url="https://clin-table-search.lhc.nlm.nih.gov/api/icd10cm/v3/search?sf=code&df=name&terms="
#
# for key, val in icd10_dict.items():
#     c.execute("SELECT * FROM ICD10_codes WHERE ID = ?", (key,)) #queries the ID column of ICD10_codes table to see if code has been added
#     entry = c.fetchone()
#
#     if entry is None: #if code is not in table...
#         try:
#             name = url + key #adds code to API base URL
#             #print(name)
#             r1 = requests.get(name) #Sends API query. Output is returned as a list of the following elments:
#                                         #1)total number of results,
#                                         #2)codes for each result,
#                                         #3)hash of "extra" data requested via "ef" query parameter. (If no extra data is requested, returns "null".)
#                                         #4)unabbreviated disease names associated with each code
#             full_codename = r1.text.split('"')[3] #Extracts unabbreviated disease name from API query output
#             c.execute('''INSERT INTO ICD10_codes (ID, name, count) VALUES(?,?,?)''', (key, full_codename, val[0],)) #adds code, unabbreviated disease name, and number of Sanford diagnoses to a new row in ICD10-codes table
#
#         except IndexError: #if IndexError occurs...
#             print(key + " does not exist in 2018 NCHS ICD-10-CM list")
#             c.execute('''INSERT INTO ICD10_codes (ID, name, count) VALUES(?,?,?)''', (key, "(OUT-OF-DATE) " + val[1], val[0],)) #adds code (key), disease name as listed in EDA spreadsheet (val[1]) (preceeded by the phrase "OUT-OF-DATE"),
#                                                                                                                                 #and number of Sanford diagnoses (val[0]) to a new row in table.
#                                                                                                                                 #Note: because of the mistake in the regular expression (identified on 2/21--see step 1), the disease name (val[1])
#                                                                                                                                 #was not properly added to the database for several cases. In order to avoid having to re-run the entire program,
#                                                                                                                                 #the affected cases will be corrected by updating the database in a separate step (see step 3).
#
#     else: #if code has already been added to table...
#         print("Entry found")
#
#     conn.commit()

#Step 3: Update database -- add disease name (abbreviated version from EDA spreadsheet) to table entries affected by regex mistake (see step 1).

c.execute("SELECT * FROM ICD10_codes WHERE name = '(OUT-OF-DATE) '") #Select affected entries from ICD10_codes table. I know that, for all affected entries, name = '(OUT-OF-DATE) '.
fix_list = (c.fetchall()) #Creates list of affected entries.
#print(fix_list)
#print(len(fix_list)) #Determine number of items in list. There are 92.

check_matches = []

for item in fix_list: #For each affected entry in ICD10_codes table...
    code = item[0] #ICD10 code
    fix_name = item[1] #disease name (needs to be changed from '(OUT-OF-DATE)' TO '(OUT-OF-DATE) + disease name from EDA spreadsheet')
    for key, val in icd10_dict.items(): #For each entry in icd10_dict...
        if code == key: #If the ICD10 code from fix_list matches the ICD10 code in the icd10_dict entry...
#             print(key)
#             check_matches.append(key) #there should be 92 matches
            correction = fix_name + val[1] #Correct fix_name by concatening the appropriate disease name
            # print(correction)
            c.execute("UPDATE ICD10_codes SET name = ? WHERE id = ?", (correction, code)) #update entry in ICD10_codes table. 

            conn.commit()

# print(len(check_matches)) #check to make sure there are 92 matches


conn.commit()
conn.close()
