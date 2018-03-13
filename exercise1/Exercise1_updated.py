import re
import sqlite3 as db
import json
import string
import sys
#print(sys.executable)
#print(sys.version)

# Step 1a: Create list of ACMG59-associated diseases
f = open("acmg59list.txt", "r")
ACMG59_diseases = []

for line in f.readlines():
    if line == "":
        pass
    b = line.split("\t")
    ACMG59_diseases.append(b[0])

# print(ACMG59_diseases)

# Step 1b: For each string in ACMG59_diseases: 1) remove all punctuation, 2) remove leading/trailing whitespaces, 3) make all letters lowercase, 4) split string into list of tokens, 5) remove stopwords

ACMG59_diseases_clean = []
stopwords = ['and', 'with']

for x in ACMG59_diseases:
    b = x.strip('"').translate(str.maketrans('', '', string.punctuation)).strip().lower().split()   # 2/7/2018: This line was giving an error when run w/ Python3 b/c the translate() method works differently in Python3 vs Python2. Modified to resolve error.
    for y in b:
        if y in stopwords:
            b.remove(y)

    ACMG59_diseases_clean.append(b)

#print(ACMG59_diseases_clean)

#Step 2: Create list of icd10 diagnoses (by connecting to sqlite3 database)
conn = db.connect('updated_icd10.db')
conn.row_factory = lambda cursor, row: row[0]
c = conn.cursor()

a = c.execute("SELECT name FROM ICD10_codes").fetchall() #select icd10 diagnosis names from database
icd10_diagnoses = [x.strip().translate(str.maketrans('', '', string.punctuation)).lower() for x in a] #for each item in icd10_diagnoses: 1) remove all punctuation, 2) remove leading/trailing whitespaces, 3) make all letters lowercase 
print(icd10_diagnoses)
print(len(icd10_diagnoses)) #Check to make sure icd10_diagnoses list contains 31845 items (We know there are 31845 ICD10 codes)

#Step 3:
# For each bigram in each ACMG59 disease name, see if that bigram appears in 1 or more ICD10 disease names (use icd10 database). Exclude stopwords.
# If yes, record the match in matches{} (key = ACMG59 disease name; values = ICD10 diseases containing one or bigrams in common with ACMG59 disease name).

matches = {}
temp = ""
temp2 = ""

for sublist in ACMG59_diseases_clean:
    #print(sublist)
    for index in range(len(sublist)-1):
        # Important: Make sure to initiate string before starting loop!
        temp = sublist[index] + ' ' + sublist[index+1]
        # Added to match Wilsons disease and Marfans syndrome
        temp2 = sublist[index] + "s " + sublist[index+1]
        if re.search(r'type \d', temp) or re.search(r'type \d', temp2):  # Added regex to address 'Type \d' problem
            continue
        for diagnosis in icd10_diagnoses:
            if temp in diagnosis or temp2 in diagnosis:
                entry = ' '.join(sublist)
                if entry in matches:
                    matches[entry].append(diagnosis)
                else:
                    matches[entry] = []
                    matches[entry].append(diagnosis)

print(matches)
print(len(matches.keys()))
print(sum(len(v) for v in matches.values())) # 2/7/2018: This line was giving an error when run w/ Python3 b/c itervalues() was replaced with values() in Python3. Modified code to resolve error.

with open('matches.txt', 'w') as file:
    file.write(json.dumps(matches, indent=5))

with open('TEST_icd10_diagnoses.txt', 'w') as file:
    file.write(json.dumps(icd10_diagnoses, indent=5))

with open('TEST_ACMG59_Dis_Clean', 'w') as file:
    file.write(json.dumps(ACMG59_diseases_clean, indent=5))
