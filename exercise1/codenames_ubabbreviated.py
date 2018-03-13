import requests
import json

# Step 2: Create list of Sanford ICD10 code diseases
with open("ICD10list.txt", "r") as f1:
    lines_after_1 = f1.readlines()[1:]


lines_file = 0
codes = []

for line in lines_after_1:
    lines_file = lines_file + 1
    result = line.split(' ')
    #print(result[0])
    codes.append(result[0])


#print(codes)

#print(len(lines_read))
#print(lines_file)

url="https://clin-table-search.lhc.nlm.nih.gov/api/icd10cm/v3/search?sf=code&df=name&terms="
for code in codes:
    name=url+code
    r1 = requests.get(name)
    #print(r1.status_code)
    #print(r1.text)
    full_codenames = r1.text.split('"')[3]
    print(full_codenames)

with open('full_codenames.txt', 'w') as file:
    file.write(json.dumps(full_codenames, indent=5))
