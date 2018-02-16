import sqlite3
import requests

# Step 1: Create list of Sanford ICD10 codes
with open("ICD10list_copy.txt", "r") as f1:
    lines_after_1 = f1.readlines()[1:]


lines_file = 0
mydict = {}

for line in lines_after_1:

    lines_file = lines_file + 1
    result = line.split(' ')
    #print(result[0])
    result2 = line.split('\t')
    #print(result2[1])
    mydict.update({result[0]: result2[1]})

conn = sqlite3.connect('icd10.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS ICD10_codes (
            ID TEXT PRIMARY KEY,
            name TEXT,
            count INTEGER
            )""")

url="https://clin-table-search.lhc.nlm.nih.gov/api/icd10cm/v3/search?sf=code&df=name&terms="

for key, val in mydict.items():
    c.execute("SELECT * FROM ICD10_codes WHERE ID = ?", (key,))
    entry = c.fetchone()

    if entry is None:
         name = url + key
         #print(name)
         r1 = requests.get(name)
         full_codename = r1.text.split('"')[3]
         c.execute('''INSERT INTO ICD10_codes (ID, name, count) VALUES(?,?,?)''', (key, full_codename, val,))
    else:
        print("Entry found")

    conn.commit()

conn.commit()
conn.close()
