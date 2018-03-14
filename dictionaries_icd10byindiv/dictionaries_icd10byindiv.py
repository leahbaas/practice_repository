import xlrd
import pickle
import json

file_location = "/home/leah/src/practice_repository/dictionaries_icd10byindiv/icd10_byindiv.xlsx"
workbook = xlrd.open_workbook(file_location)
sheet = workbook.sheet_by_index(2)
#print(sheet.cell_value(0, 0))

#Step 1a: Create dictionary in which patient data is indexed by MRN (i.e.'IDENTITY_ID').
    # Dictionary format:
    #{
    #   'IDENTITY_ID': [['CURRENT_ICD10_LIST', 'DX_DESCRIPTION', 'DX_DATE'], ['CURRENT_ICD10_LIST1', 'DX_DESCRIPTION1', 'DX_DATE1'] ...],
    #   'IDENTITY_ID2': [['CURRENT_ICD10_LIST', 'DX_DESCRIPTION', 'DX_DATE'], ['CURRENT_ICD10_LIST1', 'DX_DESCRIPTION1', 'DX_DATE1'] ... ]
    #   }
dict_mrn = {}

for row in range(1, sheet.nrows):
    mrn = sheet.cell_value(row, 0)
    data = []
    for col in range(1, sheet.ncols):
        data.append(sheet.cell_value(row,col))
    # print(data)
    if mrn in dict_mrn:
        dict_mrn[mrn].append(data)
    else:
        dict_mrn[mrn] = []
        dict_mrn[mrn].append(data)

#print(dict_mrn)

#Step 1b: Pickle dict_mrn
pickle_out = open("dict_mrn.pickle", "wb")
pickle.dump(dict_mrn, pickle_out)
pickle_out.close()

#Step 2a: Create dictionary in which patient data is indexed by icd-10 code (i.e. 'CURRENT_ICD10_lIST').
    #Dictionary format:
    #{
    #   'CURRENT_ICD10_LIST': [['IDENTITY_ID', 'DX_DESCRIPTION', 'DX_DATE'], ['IDENTITY_ID1', 'DX_DESCRIPTION1', 'DX_DATE1']...],
    #   'CURRENT_ICD10_LIST2': [['IDENTITY_ID', 'DX_DESCRIPTION', 'DX_DATE'], ['IDENTITY_ID1', 'DX_DESCRIPTION1', 'DX_DATE1']...]
    #}
dict_code = {}

for row in range(1, sheet.nrows):
    codes = str(sheet.cell_value(row, 1)).split(', ')
    #print(codes)
    data = [sheet.cell_value(row,0), sheet.cell_value(row,2), sheet.cell_value(row,3)]
    #print(data)
    for code in codes:
        if code in dict_code:
            dict_code[code].append(data)
        else:
            dict_code[code] = []
            dict_code[code].append(data)

#print(dict_code)

#Step 2b: Pickle dict_code
pickle_out = open("dict_code.pickle", "wb")
pickle.dump(dict_code, pickle_out)
pickle_out.close()

#Note: once dictionaries have been created and pickled, you can comment out the code used to create the dictionaries.

#Step 3: "Pickle_in" dictionaries
pickle_in_mrn = open("dict_mrn.pickle", "rb")
test_mrn = pickle.load(pickle_in_mrn)
#print(test_mrn)

pickle_in_code = open("dict_code.pickle", "rb")
test_code = pickle.load(pickle_in_code)
#print(test_code)

#Step 4: Write dictionaries to text files so that you can view the output
with open('dict_mrn.txt', 'w') as file:
    file.write(json.dumps(test_mrn, indent=5))

with open('dict_code.txt', 'w') as file:
    file.write(json.dumps(test_code, indent=5))

#Step 5: Sanity Checks

#   1. Check to make sure the number of unique mrns is equal to that of spreadsheet (should be 338):

# mrns = []
# for row in range(1, sheet.nrows):
#     mrn = sheet.cell_value(row, 0)
#     mrns.append(mrn)
# #print(mrns)
# unique_mrns = set(mrns)
# print(len(unique_mrns))

#   2. Check to make sure number of mrns in dict_mrn = number of unique unique_mrns (should be 338):
#print(len(dict_mrn.keys()))
