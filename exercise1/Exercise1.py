import re
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

print(ACMG59_diseases_clean)


# Step 2: Create list of Sanford ICD10 code diseases
with open("ICD10list.txt", "r") as f1:
    lines_after_1 = f1.readlines()[1:] #Skips first line in file (first line contains headings, not ICD10 information)

lines_file = 0
lines_read = []
Sanford_diseases = []

for line in lines_after_1:
    lines_file = lines_file + 1

    result = re.split(r'^[\"]*[A-Z][0-9]*[A-Z]*[.]*[0-9]*[A-Z]*[0-9]*[A-Z]*\s|\t[0-9]+[,]*[0-9]*\n*', line) #2/21/2018: detected problem with regex. Fixed and defined function to check.
    lines_read.append(result)
    # print(result)
    def check_regex(result3): #Function checks to make sure that regex functioned as expected
        if result[0] != '':
            print(result[0])
    check_regex(result)

    Sanford_diseases.extend(result)

#print(len(lines_read))
#print(lines_file)
#print(Sanford_diseases)


# Step 3a: Clean up Sanford_diseases list by removing ''

def remove_all(elements, list):
    return filter(lambda x: x not in elements, list)

Sanford_diseases1 = remove_all((''), Sanford_diseases)
#print(Sanford_diseases1)

# Step 3b: Remove punctuation and trailing/leading whitespaces from elements in Sanford_diseases_clean, and make all letters lowercase.
Sanford_diseases_clean = [x.strip().translate(str.maketrans('', '', string.punctuation)).lower()
                          for x in Sanford_diseases1]  # 2/7/2018: This line was giving an error when run w/ Python3 b/c the translate() method works differently in Python3 vs Python2. Modified to resolve error.
print(Sanford_diseases_clean)


# Step 4:
# For each bigram in each ACMG59 disease name, see if that bigram appears in 1 or more ICD10 disease names. Exclude stopwords.
# If yes, record the match in matches{} (key = ACMG59 disease name; values = ICD10 diseases containing one or bigrams in common with ACMG59 disease name).

matches = {}
temp = ""
temp2 = ""

for sublist in ACMG59_diseases_clean:
    for index in range(len(sublist)-1):
        # Important: Make sure to initiate string before starting loop!
        temp = sublist[index] + ' ' + sublist[index+1]
        # Added to match Wilsons disease and Marfans syndrome
        temp2 = sublist[index] + "s " + sublist[index+1]
        if re.search(r'type \d', temp) or re.search(r'type \d', temp2):  # Added regex to address 'Type \d' problem
            continue
        for disease in Sanford_diseases_clean:
            if temp in disease or temp2 in disease:
                entry = ' '.join(sublist)
                if entry in matches:
                    matches[entry].append(disease)
                else:
                    matches[entry] = []
                    matches[entry].append(disease)

print(matches)
# 2/7/2018: This line was giving an error when run w/ Python3 b/c itervalues() was replaced with values() in Python3. Modified code to resolve error.
print(sum(len(v) for v in matches.values()))

with open('matches.txt', 'w') as file:
    file.write(json.dumps(matches, indent=5))

with open('TEST_Sanf_Dis_Clean.txt', 'w') as file:
    file.write(json.dumps(Sanford_diseases_clean, indent=5))

with open('TEST_ACMG59_Dis_Clean', 'w') as file:
    file.write(json.dumps(ACMG59_diseases_clean, indent=5))
