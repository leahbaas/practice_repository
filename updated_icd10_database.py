import sqlite3
import requests
import re
import string

# Step 1: Create list of Sanford ICD10 codes
with open("ICD10list_copy.txt", "r") as f1:
    lines_after_1 = f1.readlines()[1:]


lines_file = 0
icd10_dict = {}

for line in lines_after_1:

    lines_file = lines_file + 1
    result = line.split(' ') #Split each line by ' '. (Creates a list--the first item is the ICD10 code; the second item is the disease name/ number of Sanford diagnoses.)
    #print(result[0])
    result2 = line.split('\t') #Split each line by '\t'. (Creates a list --the first item is the ICD10 code/ disease name; the second item is the number of Sanford diagnoses.)
    #print(result2)
    count = result2[1].strip('\n')
    #print(count)
    result3 = re.split(r'^[\"]*[A-Z][0-9]+[.]*[0-9]*\s|\t[0-9]+[,]*[0-9]*\n*', line) #Regular expression to extract only the disease name from each line
    abbreviated_name = result3[1].strip().translate(str.maketrans('', '', string.punctuation)).lower()
    icd10_dict.update({result[0]: [count, abbreviated_name]}) #Creates a dictionary. KEY=ICD10 code; VALUE= [number of Sanford diagnoses, disease name as it appears on EDA spreadsheet]

#print(icd10_dict)

# Step 2: Create database
conn = sqlite3.connect('updated_icd10.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS ICD10_codes (
            ID TEXT PRIMARY KEY,
            name TEXT,
            count INTEGER
            )""")

url="https://clin-table-search.lhc.nlm.nih.gov/api/icd10cm/v3/search?sf=code&df=name&terms="

for key, val in icd10_dict.items():
    c.execute("SELECT * FROM ICD10_codes WHERE ID = ?", (key,)) #queries the ID column of ICD10_codes table to see if code has been added
    entry = c.fetchone()

    if entry is None: #if code is not in table...
        try:
            name = url + key #adds code to API base URL
            #print(name)
            r1 = requests.get(name) #Sends API query. Output is returned as a list of the following elments:
                                        #1)total number of results,
                                        #2)codes for each result,
                                        #3)hash of "extra" data requested via "ef" query parameter. (If no extra data is requested, returns "null".)
                                        #4)unabbreviated disease names associated with each code
            full_codename = r1.text.split('"')[3] #Extracts unabbreviated disease name from API query output
            c.execute('''INSERT INTO ICD10_codes (ID, name, count) VALUES(?,?,?)''', (key, full_codename, val[0],)) #adds code, unabbreviated disease name, and number of Sanford diagnoses to a new row in ICD10-codes table

        except IndexError: #if IndexError occurs...
            print(key + " does not exist in 2018 NCHS ICD-10-CM list")
            c.execute('''INSERT INTO ICD10_codes (ID, name, count) VALUES(?,?,?)''', (key, "(OUT-OF-DATE) " + val[1], val[0],)) #adds code, disease name as it appears in EDA spreadsheet (preceeded by the phrase "OUT-OF-DATE"),
                                                                                                                                #and number of Sanford diagnoses to a new row in table.

    else: #if code has already been added to table...
        print("Entry found")

    conn.commit()

conn.commit()
conn.close()
