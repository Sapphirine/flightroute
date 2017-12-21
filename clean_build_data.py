import csv
import numpy as np

years = ['2012', '2013', '2014', '2015', '2016', '2017']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']


# 1) convert delay_raw data to delay_clean data (removes rows with weather delay is NULL or 0)
print('Part 1 out of 9')
for year in years:
	print(year)
	for month in months:
		print(month)
		with open('delay_raw/' + year +'-' + month + '.csv', 'r') as inp, open('delay_clean/' + year + '-' + month + '.csv', 'w') as out:
			writer = csv.writer(out)
			i = 0
			done = 0
			for row in csv.reader(inp, skipinitialspace=True):
				if not(done):
					for col in row:
						if col == 'YEAR':
							y = i
						if col == 'MONTH':
							m = i
						if col == 'DAY_OF_MONTH':
							d = i
						if col == 'ORIGIN_CITY_NAME':
							ori = i
						if col == 'DEST_CITY_NAME':
							dest = i
						if col == 'WEATHER_DELAY':
							delay = i
							done = 1
							break
						i += 1
				if not(done):
					break
				if (row[delay] !='0.00') and (row[delay] !=''):
					writer.writerow([row[y], row[m], row[d], row[ori], row[dest], row[delay]])


# 2) Append all csv files in delay_clean folder to one file
# Adds unique city id for each city record
print('Part 2 out of 9')
with open('weather_delays.csv', 'w') as out:
	city_list = ['CITY_NAME']
	writer = csv.writer(out)
	writer.writerow(('YEAR', 'MONTH', 'DAY_OF_MONTH', 'ORIGIN_CITY_ID', 'ORIGIN_CITY_NAME', 'DEST_CITY_ID', 'DEST_CITY_NAME', 'WEATHER_DELAY'))
	for year in years:
		print(year)
		for month in months:
			print(month)
			with open('delay_clean/' + year +'-' + month + '.csv', 'r') as inp:
				for row in csv.reader(inp, skipinitialspace=True):
					if row[0] != 'YEAR':  # skip headers row
						in_list_ori = 0
						in_list_des = 0
						for i in range(0, len(city_list)):
							if city_list[i] == row[3]:  # if already in cities list
								in_list_ori = 1
								break
						for j in range(0, len(city_list)):
							if city_list[j] == row[4]:  # if already in cities list
								in_list_des = 1
								break

						if not(in_list_ori) and not(in_list_des):  # if ori and des is not in cities list
							city_list.append(row[3])  # add ori to cities list
							city_list.append(row[4])  # add des to cities list
							# write row to out file with new city IDs for both
							writer.writerow((row[0], row[1], row[2], i + 1, row[3], j + 2, row[4], row[5]))
						elif in_list_ori and not(in_list_des):# if ori in cities list but des is not
							city_list.append(row[4])  # add des to cities list
							# write row to out file with new city IDs for des
							writer.writerow((row[0], row[1], row[2], i, row[3], j + 1, row[4], row[5]))
						elif not(in_list_ori) and in_list_des:
							city_list.append(row[3])  # add ori to cities list
							# write row to out file with new city IDs for ori
							writer.writerow((row[0], row[1], row[2], i + 1, row[3], j, row[4], row[5]))
						else:
							# write row to out file with current city IDs for both
							writer.writerow((row[0], row[1], row[2], i, row[3], j, row[4], row[5]))


fares = ['2017-3', '2017-4', '2017-1', '2017-2']

# 3) convert fares_raw data to fares_clean data (write only origin city, destination city and fare columns)
print('Part 3 out of 9')
for quarter in fares:
	with open('fares_raw/' + quarter + '.csv', 'r') as inp,\
		open('fares_clean/' + quarter + '.csv', 'w') as out:
		writer = csv.writer(out)
		for row in csv.reader(inp, skipinitialspace=True):
			writer.writerow((row[4], row[5], row[8]))


# 4) Make a list of cities from all Consumer_Airfare_Report.csv files with fare column for each quarter file 
print('Part 4 out of 9')
with open('list_fares.csv', 'w') as out:
	writer = csv.writer(out)
	q_count = 2
	fare_list = [['city1', 'city2', '17q2', '17q1', '17q4', '17q3']]
	for quarter in ['2017_Q2', '2017_Q1', '2017_Q4', '2017_Q3']:
		with open('fares_clean/' + quarter + '_Consumer_Airfare_Report_clean.csv', 'r') as inp:
			for row in csv.reader(inp, skipinitialspace=True):
				in_list = 0
				for i in range(0, len(fare_list)):
					if row[0] == 'city1': break
					if row[0] == fare_list[i][0] and row[1] == fare_list[i][1]:
						in_list = 1
						fare_list[i][q_count] = row[2][1:]
						break
				if not(in_list) and row[0] != 'city1':
					if row[0][-20:] == ' (Metropolitan Area)':
						row[0] = row[0][:-20]
					if row[1][-20:] == ' (Metropolitan Area)':
						row[1] = row[1][:-20]
					if row[0][:11] == 'Minneapolis':
						row[0] = 'Minneapolis, MN'
					if row[1][:11] == 'Minneapolis':
						row[1] = 'Minneapolis, MN'
					if row[0][:13] == 'New York City':
						row[0] = 'New York, NY'
					if row[1][:13] == 'New York City':
						row[1] = 'New York, NY'
					if row[0][:7] == 'Salinas':
						row[0] = 'Monterey, CA'
					if row[1][:7] == 'Salinas':
						row[1] = 'Monterey, CA'

					if q_count == 2:
						fare_list.append([row[0], row[1], row[2][1:], 0, 0, 0])
					if q_count == 3:
						fare_list.append([row[0], row[1], 0, row[2][1:], 0, 0])
					if q_count == 4:
						fare_list.append([row[0], row[1], 0, 0, row[2][1:], 0])
					if q_count == 5:
						fare_list.append([row[0], row[1], 0, 0, 0, row[2][1:]])

		q_count += 1

	for i in range(0, len(fare_list)):
		writer.writerow(fare_list[i])


# 5) Make a vertices file of all the origin cities in weather_delays.csv
print('Part 5 out of 9')
with open('weather_delays.csv', 'r') as inp, open('vertices_delays_origin.csv', 'w') as out:
	writer = csv.writer(out)
	ori_city_list = ['ORIGIN_CITY_NAME']
	ori_id_list = ['ORIGIN_CITY_ID']
	count = 0
	for row in csv.reader(inp, skipinitialspace=True):
		count += 1
		if count % 10000 == 0:
			print(count)
		in_list = 0
		for city in ori_city_list:
			if row[4] == city:
				in_list = 1
				break
		if not(in_list):
			ori_city_list.append(row[4])
			ori_id_list.append(row[3])

	for i in range(0, len(ori_city_list)):
		writer.writerow([ori_city_list[i], ori_id_list[i]])


# 6) Make a vertices file of all the destination cities in weather_delays.csv
print('Part 6 out of 9')
with open('weather_delays.csv', 'r') as inp, open('vertices_delays_dest.csv', 'w') as out:
	writer = csv.writer(out)
	des_city_list = ['DEST_CITY_NAME']
	des_id_list = ['DEST_CITY_ID']
	count = 0
	for row in csv.reader(inp, skipinitialspace=True):
		count += 1
		if count % 10000 == 0:
			print(count)
		in_list = 0
		for city in des_city_list:
			if row[6] == city:
				in_list = 1
				break
		if not(in_list):
			des_city_list.append(row[6])
			des_id_list.append(row[5])

	for i in range(0, len(des_city_list)):
		writer.writerow([des_city_list[i], des_id_list[i]])


# 7) calculate weather delay average per day
# build two lists
# 1. sum of delays for each day of the year for each cities pairs
# 2. count of the records for each day of the year for each cities pairs
print('Part 7 out of 9')
day_rng = 5
cities_num = 330
cities_num = cities_num + 1
with open('weather_delays.csv', 'r') as inp:
	wd_sum = np.zeros((13, 32, cities_num, cities_num))
	wd_ind = np.zeros((13, 32, cities_num, cities_num))
	count = 0
	for row in csv.reader(inp, skipinitialspace=True):
		count += 1
		if count % 10000 == 0:
			print(count)
		# if count == 10000: break
		if row[0] != 'YEAR':
			for month in range(1, 13):
				if int(row[1]) == month:
					for day in range(1, 32):
						if int(row[2]) == day:
							for city_o in range(1, cities_num):
								if int(row[3]) == city_o:
									for city_d in range(1, cities_num):
										if int(row[5]) == city_d:
											wd_sum[month, day, city_o, city_d] += float(row[7])
											wd_ind[month, day, city_o, city_d] += 1

# part of 7)
# make a list of city pairs (ori-des)
# each city-pair is a list of[month, day, city_o, city_d, weather_delay_sum, weather_ind_sum]
pairs_list = []
for city_o in range(1, cities_num):
	if city_o % 1000 == 0:
		print(city_o)
	for city_d in range(1, cities_num):
		wd_list = []
		for month in range(1, 13):
			for day in range(1, 32):
				if wd_ind[month, day, city_o, city_d]:
					weather_delay_sum = wd_sum[month, day, city_o, city_d]
					weather_ind_sum = wd_ind[month, day, city_o, city_d]
					wd_list.append([month, day, city_o, city_d, weather_delay_sum, weather_ind_sum, 0, 0, 0])
		pairs_list.append(wd_list)

# part of 7)
# calculate avg delay for +-5 days with each city pair
for pair in range(0, len(pairs_list)):
	if pair % 1000 == 0:
		print(pair)
	for date in range(0, len(pairs_list[pair])):
		del_sum = 0
		count = 0
		i = 0
		while date + i < len(pairs_list[pair]) and pairs_list[pair][date + i][1] <= pairs_list[pair][date][1] + day_rng:
			if pairs_list[pair][date + i][0] == pairs_list[pair][date][0]:  # same month
				del_sum += pairs_list[pair][date + i][4]
				count += pairs_list[pair][date + i][5]
			i += 1
		i = 1
		while date - i > 0 and pairs_list[pair][date - i][1] >= pairs_list[pair][date][1] - day_rng:
			if pairs_list[pair][date - i][0] == pairs_list[pair][date][0]:  # same month
				del_sum += pairs_list[pair][date - i][4]
				count += pairs_list[pair][date - i][5]
			i += 1

		pairs_list[pair][date][6] = del_sum
		pairs_list[pair][date][7] = count
		pairs_list[pair][date][8] = del_sum / count

# part of 7)
# write pairs_list to a file
with open('calc_weather_delays.csv', 'w') as out:
	writer = csv.writer(out)
	writer.writerow(['MONTH', 'DAY_OF_MONTH', 'ORIGIN_CITY_ID', 'DEST_CITY_ID',
		'DAY_WEATHER_DELAY', 'DAY_RECORDS_COUNT', 'RANGE_WEATHER_DELAY', 'RANGE_RECORDS_COUNT', 'AVG_WEATHER_DELAY'])
	for od_pair in pairs_list:
		for od_date in od_pair:
			writer.writerow(od_date)


# 8) add cities ids to fare data in list_fares_id.csv
print('Part 8 out of 9')
with open('list_fares.csv', 'r') as f_inp, open('list_fares_id.csv', 'w') as out:
	writer = csv.writer(out)
	writer.writerow(['city1', 'city2', '17q2', '17q1', '16q4', '16q3', 'city1_id', 'city2_id'])
	for f_row in csv.reader(f_inp, skipinitialspace=True):
		if f_row[0] == 'city1':
			continue

		f_ori_id = 0
		with open('vertices_delays_origin.csv', 'r') as delay_o:
			for row in csv.reader(delay_o, skipinitialspace=True):
				if f_row[0] == row[0]:
					f_ori_id = row[1]
					break

		f_dest_id = 0
		with open('vertices_delays_dest.csv', 'r') as delay_d:
				for row in csv.reader(delay_d, skipinitialspace=True):
					if f_row[1] == row[0]:
						f_dest_id = row[1]
						break

		writer.writerow(f_row + [f_ori_id, f_dest_id])


# 9) Make a nodes file by adding the fare data to the calc_weather_delays.csv file
# Also, reduce resolution of weather delay to x min in a new column
print('Part 9 out of 9')
with open('nodes_flight.csv', 'w') as out, open('calc_weather_delays.csv', 'r') as d_inp:
	writer = csv.writer(out)
	writer.writerow(['MONTH', 'DAY_OF_MONTH', 'ORIGIN_CITY_ID', 'DEST_CITY_ID', 'DAY_WEATHER_DELAY', 'DAY_RECORDS_COUNT',
		'RANGE_WEATHER_DELAY', 'RANGE_RECORDS_COUNT', 'AVG_WEATHER_DELAY', 'AVG_WEATHER_DELAY_RE', 'FARE'])
	count = 0
	d_res = 1
	for d_row in csv.reader(d_inp, skipinitialspace=True):
		if d_row[0] != 'MONTH':
			# reduce resolution of weather delay
			delay = float(d_row[8])
			delay_re = int((delay - (delay % d_res)) / d_res)
		found = 0
		with open('list_fares_id.csv', 'r') as f_inp:
			for f_row in csv.reader(f_inp, skipinitialspace=True):
				# if ORIGIN_CITY_ID in weather == city1/2 and DEST_CITY_ID in weather == city2/1 in fares
				if (d_row[2] == f_row[6] and d_row[3] == f_row[7]) or (d_row[2] == f_row[7] and d_row[3] == f_row[6]):
					if int(d_row[0]) <= 3:  # checks if the record is in Q1 of the year (month=1,2,3)
						if float(f_row[3]) != 0:
							found = 1
							writer.writerow(d_row + [delay_re] + [f_row[3]])
							break
					elif int(d_row[0]) <= 6:  # checks if the record is in Q2 of the year (month=4,5,6)
						if float(f_row[2]) != 0:
							found = 1
							writer.writerow(d_row + [delay_re] + [f_row[2]])
							break
					elif int(d_row[0]) <= 9:  # checks if the record is in Q3 of the year (month=7,8,9)
						if float(f_row[5]) != 0:
							found = 1
							writer.writerow(d_row + [delay_re] + [f_row[5]])
							break
					else:  # record is in Q4 of the year (month=10,11,12)
						if float(f_row[4]) != 0:
							found = 1
							writer.writerow(d_row + [delay_re] + [f_row[4]])
							break

		if not(found) and d_row[0] != 'MONTH':
			writer.writerow(d_row + [delay_re] + [0])
		count += 1
		if count % 500 == 0:
			print(count)

print('Done building the database!')
