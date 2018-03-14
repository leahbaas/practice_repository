import xlrd
file_location = "/home/leah/src/practice_sprdsht.xlsx"
workbook = xlrd.open_workbook(file_location)
sheet = workbook.sheet_by_index(0)
#print(sheet.cell_value(0, 0))

dict_mrn = {}

for row in range(0, sheet.nrows):
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

dict_code = {}

for row in range(1, sheet.nrows):
    codes = sheet.cell_value(row, 1).split(', ')
    #print(codes)
    data = [sheet.cell_value(row,0), sheet.cell_value(row,2), sheet.cell_value(row,3)]
    #print(data)
    for code in codes:
        if code in dict_code:
            dict_code[code].append(data)
        else:
            dict_code[code] = []
            dict_code[code].append(data)

print(dict_code)
