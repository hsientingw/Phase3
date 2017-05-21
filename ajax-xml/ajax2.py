import math
import os
import json
import csv
from collections import defaultdict

from flask import Flask, request
app = Flask(__name__, static_folder='.', static_url_path='')


def file_output(data):
    output_filename = "data/test_output.csv"
    output_file = open(output_filename, "wb")
    writer = csv.writer(output_file, delimiter=',')
    for line in data:
        writer.writerow(line)
    output_file.close()

# returns True if numeric, False if not
def is_numeric(value):
    if len(value) == 0:
        return False
    for c in value:
        if c not in "1234567890":
            return False
    return True

# returns the binned value of an int
def binned(value, bin_value):
    return (value//bin_value) * bin_value

# finds all the row/column labels
# returns list of labels and index of column
# returns False if name of row/col is not one of the columns of data
def find_labels(header, data, name, bin_value):
    # initialise row_index and row_labels
    index = -1
    labels = []
    
    # find row_index
    for i in range(len(header)):
        if header[i] == name:
            index = i
            break
    if index == -1:
        return False
    
    # find all row labels
    for i in range(len(data)):
        if isinstance(data[i][index], (int, long)):
            current = binned(data[i][index], bin_value)
        else:
            current = data[i][index]
        if current not in labels:
            labels.append(current)
            
    return (labels, index)
            

# gets info on intersect data using existing data and new value
# returns (num_of, sum, average, min, max)
def get_info(new_value, existing_data):
    new_num_of = existing_data[0] + 1
    new_sum = existing_data[1] + new_value
    new_average = 1.0 * new_sum / new_num_of
    if new_value < existing_data[3] or existing_data[3] == -1:
        new_min = new_value
    else:
        new_min = existing_data[3]
    if new_value > existing_data[4]:
        new_max = new_value
    else:
        new_max = existing_data[4]
    
    return (new_num_of, new_sum, new_average, new_min, new_max)

# returns True if value matches all filters
# filter1 and filter2 are tuples (col_name, comparison, value), or False if no filter
def filter_true(header, data_row, filter1, filter2):
    # check filter1
    if filter1 != False:
        # find column index for filter21
        for i in range(len(header)):
            if header[i] == filter1[0]:
                f1_index = i
                break
        if filter1[1] == "less_than":
            if data_row[f1_index] > filter1[2]:
                return False
        elif filter1[1] == "greater_than":
            if data_row[f1_index] < filter1[2]:
                return False
        else:
            if data_row[f1_index] not in filter1[2]:
                return False
    
    # check filter2
    if filter2 != False:
        # find column index for filter2
        for i in range(len(header)):
            if header[i] == filter2[0]:
                f2_index = i
                break
        if filter2[1] == "less_than":
            if data_row[f2_index] > filter2[2]:
                return False
        elif filter2[1] == "greater_than":
            if data_row[f2_index] < filter2[2]:
                return False
        else:
            if data_row[f2_index] not in filter2[2]:
                return False
    
    return True

	
def color(num, min_val, max_val):
	# 1 green 00ff00
    n = float(num - min_val)/float(max_val-min_val) # make it 0 - 1
    greeness = '%02x' % int((1-n)*255)
    return '#' + greeness + 'ff' + greeness
	
# converts table to json format
def list_to_json(mylist):
	width = len(mylist[0])
	json_string = '''[{"success": "success", "width":''' + str(width)+'''}'''
	max_val = 0
	min_val = 17000
	for line in mylist:
		num_list = [num for num in line[1:] if type(num)!=str]
		if num_list != []:
			temp_max = max(num_list)
			temp_min = min(num_list)
			if max_val < temp_max:
				max_val = temp_max
			if temp_min < min_val:
				min_val = temp_min
	if max_val == min_val:
		max_val = min_val+1
	for row in mylist:
		json_string += ',{"content":['
		for i in range(width):
			if i != 0:
				json_string += ","
			if type(row[i]) == float:
				added_str = '''"{:.2f}", "{}"'''.format(row[i], color(row[i], min_val, max_val))
			elif type(row[i]) == int:
				added_str = '"'+str(row[i])+'","{}"'.format(color(row[i], min_val, max_val))
			else:
				added_str = '"'+str(row[i])+'","{}"'.format("#cccccc")
			json_string += added_str
		json_string += "]}"
	json_string += "]"
	json_string = json_string[:23]+'''"vals": [{}, {}],'''.format(max_val, min_val) +json_string[23:]
	return json_string

# main pivot function
# row - name of column of data to be used for row labels
# row_d - if true, sort descending, if false, sort ascending
# row_bin - how to bin row data if numerical (1-10), -1 if non-numeric data
# col - name of column of data to be used for column lables
# col_d - if true, sort descending, if false, sort ascending
# col_bin - how to bin column data if numerical (1-10), -1 if non-numeric data
# inter - column of data to be used in the main table
# inter_format - what format to use for numerical intersect data (num_of, sum, average, min, max)
# inter_f1 - filter 1 for intersect data in form (col_name, comparison, value), where comparison is (less_than, greater_than, or equal_to)
# inter_f2 - filter 2 for intersect data in form (col_name, comparison, value), where comparison is (less_than, greater_than, or equal_to)
def pivot(row, row_d, row_bin, col, col_d, col_bin, inter, inter_format, filter1, filter2):
    # open file
    filename = "data.csv"
    f = open(filename)
    
    # get data
    reader = csv.reader(f)
    header = reader.next()
    data = list(reader)
    
    # close file
    f.close()
    
    # convert numeric data into integers
    for i in range(len(data)):
        for j in range(len(data[i])):
            if is_numeric(data[i][j]):
                data[i][j] = int(data[i][j])
    
    # find row labels
    row_labels_pre = find_labels(header, data, row, row_bin)
    row_labels = row_labels_pre[0]
    row_index = row_labels_pre[1]
    
    # sort row labels
    row_labels.sort(reverse=row_d)
    
    # create dictionary from row labels
    row_dict = defaultdict(int)
    for i in range(len(row_labels)):
        row_dict[row_labels[i]] = i+1
                
    # find column labels
    col_labels_pre = find_labels(header, data, col, col_bin)
    col_labels = col_labels_pre[0]
    col_index = col_labels_pre[1]
    
    # sort column labels
    col_labels.sort(reverse=col_d)
    
    # create dictionary from column labels
    col_dict = defaultdict(int)
    for i in range(len(col_labels)):
        col_dict[col_labels[i]] = i+1
                
    
    # create data table
    new_data = []
    for i in range(len(row_labels) + 1):
        new_data.append([])
        for j in range(len(col_labels) + 1):
            new_data[i].append((0, 0, -1, -1, -1))
            
    # add labels
    new_data[0][0] = ''
    for i in range(len(row_labels)):
        new_data[i+1][0] = row_labels[i]
    for i in range(len(col_labels)):
        new_data[0][i+1] = col_labels[i]
        
    # find intersect data column index
    inter_index = -1
    for i in range(len(header)):
        if header[i] == inter:
            inter_index = i
            break
    if inter_index == -1:
        return False
    
    # add intersect data
    for i in range(len(data)):
        if filter_true(header, data[i], filter1, filter2):
            current = data[i][inter_index]
            if(isinstance(data[i][row_index], (int, long))):
                current_row_index = row_dict[binned(data[i][row_index], row_bin)]
            else:
                current_row_index = row_dict[data[i][row_index]]
            if(isinstance(data[i][col_index], (int, long))):
                current_col_index = col_dict[binned(data[i][col_index], col_bin)]
            else:
                current_col_index = col_dict[data[i][col_index]]
            new_data[current_row_index][current_col_index] = get_info(current, new_data[current_row_index][current_col_index])
    
    # get correct format
    format_dict = {"num_of": 0, "sum": 1, "average": 2, "min": 3, "max": 4}
    print("here")
    print(new_data[0])
    for i in range(1, len(new_data)):
        for j in range(1, len(new_data[i])):
            if (new_data[i][j])[format_dict[inter_format]] == -1:
                new_data[i][j] = "-"
            else:
                new_data[i][j] = (new_data[i][j])[format_dict[inter_format]]
    

    if type(new_data[1][0])==int:
		for row in new_data[1:]:
			row[0] = str(row[0]) +"-"+str(row[0]+row_bin-1)
	
    print(new_data[0])
    if type(new_data[0][1])==int:
		print("something")
		for i in range(1,len(new_data[0])):
			print("something2")
			new_data[0][i] = str(new_data[0][i]) + "-"+str(new_data[0][i] + col_bin-1)
	# testing code, write to file for readability
    #print(new_data)
    #file_output(new_data)
    #print("done")
    return list_to_json(new_data)
  

@app.route('/ajax-handler', methods=['POST'])
def handler():
    payload = request.data
    json_request = json.loads(payload)
    my_input = json_request['expression'] or '1+1' # default expression is 1+1
    
    # failure output
    failure = json.dumps(json.loads('''[{
			"success": "error"}]'''))
    # interpret input
    split_input = my_input.split('+')
    print(split_input)
    # row
    row = split_input[0]
    # row_d
    if split_input[1] == 'Ascending':
        row_d = False
    else:
        row_d = True
    # row_bin
    row_bin = int(split_input[2])
        
    # col
    col = split_input[3]
    
    # cold_d
    if split_input[4] == 'Ascending':
        col_d = False
    else:
        col_d = True
        
    # col_bin
    if split_input[5] == '0':
        col_bin = -1
    else:
        col_bin = int(split_input[5])
        
    # inter
    inter = split_input[6]
    
    # inter_format
    if split_input[7] == 'count':
        inter_format = 'num_of'
    else:
        inter_format = split_input[7]
        
    # filter1
    if split_input[8] == 'No Filter':
        filter1 = False
    else:
        filter1 = ['','','']
        filter1[0] = split_input[8]
        if split_input[9] == '<=':
            filter1[1] = "less_than"
        elif split_input[9] == '>=':
            filter1[1] = "greater_than"
        elif split_input[9] == "includes":
            filter1[1] = "includes"
        else:
			filter1[1] = "equal_to"
        if len(split_input[10].split(',')) == 1:
			filter1[2] = [split_input[10]]
        else:
			filter1_values = []
			for value in split_input[10].split(','):
				if is_numeric(value):
					filter1_values.append(int(value))
				else:
					filter1_values.append(value)
			value_type1 = type(filter1_values[0])
			for element in filter1_values:
				if type(element) != value_type1:
					return failure
			filter1[2] = filter1_values
			
		    
    # filter2
    if split_input[11] == 'No Filter':
        filter2 = False
    else:
        filter2 = ['','','']
        filter2[0] = split_input[11]
        if split_input[12] == '<=':
            filter2[1] = "less_than"
        elif split_input[12] == '>=':
            filter2[1] = "greater_than"
        elif split_input[12] == "includes":
            filter2[1] = "includes"
        else:
            filter2[1] = "equal_to"
        if len(split_input[13].split(',')) == 1:
			filter2[2] = [split_input[13]]
        else:
			filter2_values = []
			for value in split_input[13].split(','):
				if is_numeric(value):
					filter2_values.append(int(value))
				else:
					filter2_values.append(value)
			value_type2 = type(filter2_values[0])
			for element in filter2_values:
				if type(element) != value_type2:
					return failure
			filter2[2] = filter2_values
			
	
	
	if (filter1 != False):
	    if (filter1[1] != "includes" and len(filter1[2]) > 1):
		    return failure
			
	if (filter2 == False):
		if filter2[1] != "includes" and len(filter2[2]) > 1:
		    return failure
    #print(pivot("Nationality", False, 4, "Rating", True, 10, "Dribbling", "average", ("Weight", "less_than", 80), False))
    print(row, row_d, row_bin, col, col_d, col_bin, inter, inter_format, filter1, filter2)
    result=pivot(row, row_d, row_bin, col, col_d, col_bin, inter, inter_format, filter1, filter2)
    print(result)
    return json.dumps(json.loads(result)), 200, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8766)