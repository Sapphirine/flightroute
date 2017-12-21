import graphdb_client
import json
import itertools
from Tkinter import *
from PIL import ImageTk, Image

g = graphdb_client.gc(host='http://localhost:8010')


def main(ori_name, dest_names, start_month, start_day, end_month, end_day, days):

    names = [ori_name] + dest_names

    start_month = start_month
    start_day = start_day
    stop_month = end_month
    stop_day = end_day

    c_days = []
    for i in range(0, len(days)):
        c_days.append(days[i])

    ids = names2ids(names)

    dest_days = []
    for i in range(1, len(names)):
        dest_days.append([ids[i], int(c_days[i - 1])])

    all_pos_routes = gen_routes(ids)

    global STRING
    STRING = '\n\n\n\nThere are ' + str(len(all_pos_routes)) + ' possible routes'
    RES.set(STRING)
    root.update_idletasks()

    delay_sum, pairs, dates, delays, recs, fares = find_best_route(all_pos_routes, dest_days, start_month, start_day, stop_month, stop_day)
    # delay_sum = 98, pairs[0] = [c1, c2], dates[0] = [M, D], delays[0] = 27, recs[0] = 11, fares[0] = 230.0

    print_results(names, ids, delay_sum, pairs, dates, delays, recs, fares)


def names2ids(names):
    ids = []

    ori_label = 'ORI'
    dest_label = 'DEST'
    ori_list = g.get_vertex(vertex_label=[ori_label])
    ori_list = json.loads(ori_list)['data']['vertices']
    dest_list = g.get_vertex(vertex_label=[dest_label])
    dest_list = json.loads(dest_list)['data']['vertices']

    for name in names:
        found = 0
        # get origin city id
        for ori in ori_list:
            if ori['properties'][0]['name'] == name:
                ids.append(ori['id'])
                found = 1
                break
        if not(found):
            # get destination city id
            for dest in dest_list:
                if dest['properties'][0]['name'] == name:
                    ids.append(dest['id'])
                    found = 1
                    break
        if not(found):
            ids.append(-1)
            global STRING
            STRING = '\n\n\n\nError: (' + str(name) + ') is not in the database!\n'
            RES.set(STRING)
            root.update_idletasks()

    return ids


def gen_routes(ids):
    size = len(ids)
    routes = []
    for per in itertools.permutations(range(1, size), size - 1):
        route = [ids[0]]
        for i in range(0, size - 1):
            route.append(ids[per[i]])
        route.append(ids[0])
        routes.append(route)

    return routes


def find_best_route(all_pos_routes, dest_days, start_month, start_day, stop_month, stop_day):

    global STRING
    t_delay_sum = -1; t_res_sum = 0; t_fare_sum = 0; t_skips = 0
    count = 1; first = 1
    for route in all_pos_routes:
        temp_string = STRING
        STRING = STRING + '\n\n\n\nSearching dates for route ' + str(count) + '\n'
        RES.set(STRING)
        root.update_idletasks()
        delay_sum, res_sum, fare_sum, skips, pairs, dates, delays, recs, fares = find_best_dates(route, dest_days, start_month, start_day, stop_month, stop_day)
        # delay_sum = 98, res_sum = 6.25, fare_sum = 306, pairs[0] = [c1, c2], dates[0] = [M, D], delays[0] = 27, recs[0] = 11, fares[0] = 230.0

        if first:
            t_delay_sum, t_res_sum, t_fare_sum, t_skips, = delay_sum, res_sum, fare_sum, skips
            t_pairs, t_dates, t_delays, t_recs, t_fares = pairs, dates, delays, recs, fares
            first = 0

        elif delay_sum != -1 and res_sum < t_res_sum and skips <= t_skips:
            t_delay_sum, t_res_sum, t_fare_sum, t_skips, = delay_sum, res_sum, fare_sum, skips
            t_pairs, t_dates, t_delays, t_recs, t_fares = pairs, dates, delays, recs, fares

        elif delay_sum != -1 and res_sum == t_res_sum and skips == t_skips and fare_sum < t_fare_sum:
            t_delay_sum, t_res_sum, t_fare_sum, t_skips, = delay_sum, res_sum, fare_sum, skips
            t_pairs, t_dates, t_delays, t_recs, t_fares = pairs, dates, delays, recs, fares

        count += 1
        STRING = STRING + '\ndone'
        RES.set(STRING)
        root.update_idletasks()
        STRING = temp_string

    return t_delay_sum, t_pairs, t_dates, t_delays, t_recs, t_fares


def find_best_dates(route, dest_days, start_month, start_day, stop_month, stop_day):
    global STRING

    pairs = get_pairs(route)
    # pairs = [[2,3], [3,5], [5,1], [1,10], [10,2]]

    pairs_num = len(pairs)
    pairs_dates = get_pairs_dates(pairs_num, start_month, start_day, stop_month, stop_day)
    # pairs_dates[0] = [[start_month, start_day], [M1, D1], [M2, D2], [M3, D3], [stop_month, stop_day]]

    best_delay_sum = -1; best_res_sum = -1; best_fare_sum = -1; best_skips = -1; count = 1
    best_dates = []; best_delays = []; best_recs = []; best_fares = []

    temp_string1 = STRING
    len_pairs_dates = len(pairs_dates)
    for dates in pairs_dates:
        if count % 10 == 0:
            prec = 100 * count / len_pairs_dates

            temp_string2 = STRING
            STRING = STRING + str('\n{}%'.format(prec))
            RES.set(STRING)
            root.update_idletasks()
            STRING = temp_string2

        good_dates = check_dates(route, dest_days, dates)
        if not(good_dates):
            continue

        delays, recs, fares = [], [], []
        delay_sum = -1; recs_sum = -1; res_sum = -1; fare_sum = -1; skips = 0
        for pair in range(0, pairs_num):
            d, r, f = find_flight(pairs[pair][0], pairs[pair][1], dates[pair][0], dates[pair][1])
            delays.append(d); recs.append(r); fares.append(f)
            if d != -1:
                if delay_sum == -1:
                    delay_sum = d
                    recs_sum = r
                    res_sum = d / r
                    fare_sum = f
                else:
                    delay_sum += d
                    recs_sum += r
                    res_sum += d / r
                    fare_sum += f
            else: skips += 1

        first = 1
        if first:
            best_skips = skips
            best_res_sum = res_sum
            best_delay_sum = delay_sum
            best_fare_sum = fare_sum
            best_dates = dates
            best_delays, best_recs, best_fares = delays, recs, fares
            first = 0

        elif delay_sum != -1 and res_sum < best_res_sum and skips <= best_skips:
            best_skips = skips
            best_res_sum = res_sum
            best_delay_sum = delay_sum
            best_fare_sum = fare_sum
            best_dates = dates
            best_delays, best_recs, best_fares = delays, recs, fares

        elif delay_sum != -1 and res_sum == best_res_sum and skips == best_skips and fare_sum < best_fare_sum:
            best_skips = skips
            best_res_sum = res_sum
            best_delay_sum = delay_sum
            best_fare_sum = fare_sum
            best_dates = dates
            best_delays, best_recs, best_fares = delays, recs, fares

        count += 1
    STRING = STRING + str('\n100%')
    RES.set(STRING)
    root.update_idletasks()
    STRING = temp_string1

    return best_delay_sum, best_res_sum, best_fare_sum, best_skips, pairs, best_dates, best_delays, best_recs, best_fares


def get_pairs(route):
    pairs = []

    num = len(route) - 1
    for i in range(0, num):
        pairs.append([route[i], route[i + 1]])

    return pairs


def get_pairs_dates(pairs_num, start_month, start_day, stop_month, stop_day):

    list_all_dates = gen_all_dates(start_month, start_day, stop_month, stop_day)
    num_dates = len(list_all_dates)
    dates_pos = gen_all_dates_pos(num_dates, pairs_num)
    # [0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 2, 3, 1], [0, 3, 1, 2], [0, 3, 2, 1]
    # [1, 0, 2, 3], [1, 0, 3, 2], [1, 2, 0, 3], [1, 2, 3, 0], [1, 3, 0, 2], [1, 3, 2, 0]
    # [2, 0, 1, 3], [2, 0, 3, 1], [2, 1, 0, 3], [2, 1, 3, 0], [2, 3, 0, 1], [2, 3, 1, 0]
    # [3, 0, 2, 3], [3, 0, 3, 2], [3, 1, 0, 2], [3, 1, 2, 0], [3, 2, 0, 1], [3, 2, 1, 0]

    good_list = []
    for pos in dates_pos:
        if pos[0] != 0:  # left with [0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 2, 3, 1], [0, 3, 1, 2], [0, 3, 2, 1]
            continue
        if pos[pairs_num - 1] != num_dates - 1:   # left with [0, 1, 2, 3], [0, 2, 1, 3]
            continue
        bad = 0
        for i in range(1, pairs_num - 2):   # left with [0, 1, 2, 3]
            if pos[i] >= pos[i + 1]:
                bad = 1
                break
        if bad:
            continue

        good_list.append(pos)

    pairs_dates = []

    for item in good_list:
        pd = []
        for i in range(0, pairs_num):
            pd.append(list_all_dates[item[i]])

        pairs_dates.append(pd)

    return pairs_dates


def gen_all_dates(start_month, start_day, stop_month, stop_day):
    list_dates = []

    d = start_day
    m = start_month

    done = 0
    while not(done):
        list_dates.append([m, d])
        if d == 31:
            d = 1
            if m == 12:
                m = 1
            else:
                m += 1
        else:
            d += 1
        if d == stop_day and m == stop_month:
            done = 1

    list_dates.append([stop_month, stop_day])

    return list_dates


def gen_all_dates_pos(num_dates, pairs_num):
    dates_pos = []
    for per in itertools.permutations(range(0, num_dates), pairs_num):
        dates_pos.append(per)

    return dates_pos


def check_dates(route, dest_days, dates):
    # route = [11, 5, 2, 3, 4, 11]
    # dest_days = [[2, c2_days], [3, c3_days], [4, c4_days], [5, c5_days]]
    # dates[0] = [[start_month, start_day], [M1, D1], [M2, D2], [M3, D3], [stop_month, stop_day]]

    for i in range(1, len(route) - 1):
        for dest in dest_days:
            if route[i] == dest[0]:
                days = dest[1]
                break

        calc_d = calc_days(dates[i - 1], dates[i])

        if calc_d < days:
            return 0

    return 1


def calc_days(date_1, date_2):

    if date_2[0] == date_1[0]:  # month2 = month1
        days = date_2[1] - date_1[1]

    elif date_2[0] > date_1[0]:  # month2 > month1
        months = date_2[0] - date_1[0]
        days = date_2[1] + months * 31 - date_1[1]

    else:  # month2 < month1
        months = date_2[0] + 12 - date_1[0]
        days = date_2[1] + months * 31 - date_1[1]

    return days


def find_flight(ori, dest, month, day):
    ori_label = 'ORI'
    dest_label = 'DEST'

    # get flight information
    flights = g.get_edge(source_id=ori, source_label=ori_label, target_id=dest, target_label=dest_label, edge_id='', edge_label=[], prop=[])

    if json.loads(flights)['status'] == 'failure':
        return -1, -1, -1
    flights = json.loads(flights)['data']['edges']

    found = 0
    for flight in flights:
        if flight['properties'][0]['month'] == month:
            if flight['properties'][1]['day'] == day:
                delay = flight['properties'][7]['avg_delay']
                recs = flight['properties'][5]['records_count']
                fare = flight['properties'][8]['fare']
                found = 1
                break

    if not(found):
        for i in range(1, 5):  # search closest day delay
            if day + i > 31:
                d = day + i - 31
                if month == 12:
                    m = 1
                else:
                    m = month + 1
            else:
                d = day + i
                m = month

            for flight in flights:
                if flight['properties'][0]['month'] == m:
                    if flight['properties'][1]['day'] == d:
                        delay = flight['properties'][7]['avg_delay']
                        recs = flight['properties'][5]['records_count']
                        fare = flight['properties'][8]['fare']
                        found = 1
                        break
            if found: break

            if day - i < 1:
                d = day - i + 31
                if month == 1:
                    m = 12
                else:
                    m = month - 1
            else:
                d = day - i
                m = month

            for flight in flights:
                if flight['properties'][0]['month'] == m:
                    if flight['properties'][1]['day'] == d:
                        delay = flight['properties'][7]['avg_delay']
                        recs = flight['properties'][5]['records_count']
                        fare = flight['properties'][8]['fare']
                        found = 1
                        break
            if found: break

    if not(found):
        return -1, -1, -1

    return delay, recs, fare


def print_results(names, ids, delay_sum, pairs, dates, delays, recs, fares):

    global STRING

    print '\n'
    if dates == []:
        STRING = '\n\n\n\nNo possible routes'
        RES.set(STRING)
        root.update_idletasks()
        return

    if delay_sum == -1:
        STRING = '\n\n\n\nNo information on best possible route\n\nSuggesting route with unknown delay:\n\n\n\n'

    else:
        STRING = '\n\n\n\nThe best route has avg delay of ' + str(delay_sum) + ' minutes:\n\n\n\n'

    for i in range(0, len(pairs)):
        STRING = STRING + str(names[ids.index(pairs[i][0])]) + ' ---> ' + str(names[ids.index(pairs[i][1])]) + \
            ' @ ' + str(dates[i][0]) + '/' + str(dates[i][1]) + '\n'
        if delays[i] == -1:
            STRING = STRING + 'The delay is unknown\n'
        else:
            STRING = STRING + 'The avg delay is ' + str(delays[i]) + ' (' + str(recs[i]) + ' reports)\n'

        if fares[i] <= 0:
            STRING = STRING + 'The fare is unknown\n\n'
        else:
            STRING = STRING + 'The fare is ' + str(fares[i]) + '$\n\n'

    RES.set(STRING)
    root.update_idletasks()


def load_graph(name):
    new_graph_name = name  # 'flights_graph'

    g.create_graph(graph_name=new_graph_name)

    g.set_current_graph(new_graph_name)

    load_origin_vertex()
    load_destination_vertex()
    load_flight_edge()


# Load header vertex file which file is locate on the user machine
def load_origin_vertex():
    vertex_file_path = 'vertices_delays_origin.csv'
    has_header = 1
    column_delimiter = ','
    default_vertex_label = "ORI"
    #in the content_type {"aaa":['aa','INT']}  
    #'aa' is the column name in the csv's header, 'aaa' is the property name you want to call in your graph

    content_type = [{"name": ['ORIGIN_CITY_NAME', "STRING"]}]

    column_header_map = {
                "vertex_id": "ORIGIN_CITY_ID",
                "properties": content_type}

    rc = g.load_table_vertex(file_path = vertex_file_path,
                        has_header = has_header,
                        column_delimiter = column_delimiter,
                        default_vertex_label = default_vertex_label,
                        column_header_map = column_header_map,
                        column_number_map=[{}],
                        content_type = content_type,
                        data_row_start = -1,
                        data_row_end = -1)
    print (rc)


def load_destination_vertex():
    vertex_file_path = 'vertices_delays_dest.csv'
    has_header = 1
    column_delimiter = ','
    default_vertex_label = "DEST"
    content_type = [{"name": ['DEST_CITY_NAME', "STRING"]}]

    column_header_map = {
                "vertex_id": "DEST_CITY_ID",
                "properties": content_type}

    rc = g.load_table_vertex(file_path = vertex_file_path,
                        has_header = has_header,
                        column_delimiter = column_delimiter,
                        default_vertex_label = default_vertex_label,
                        column_header_map = column_header_map,
                        column_number_map=[{}],
                        content_type = content_type,
                        data_row_start = -1,
                        data_row_end = -1)
    print (rc)


# Load header edge file which file is locate on local machine
def load_flight_edge():
    edge_file_path = 'nodes_flight.csv'
    has_header = 1
    column_delimiter = ','

    default_source_label = "ORI"
    default_target_label = "DEST"
    default_edge_label = 'FLIGHT'
    content_type = [{"month": ['MONTH', "INT"]}, {"day": ['DAY_OF_MONTH', "INT"]}, {"avg_delay": ['AVG_WEATHER_DELAY_RE', "INT"]},
        {"records_count": ['RANGE_RECORDS_COUNT', "DOUBLE"]}, {"fare": ['FARE', "DOUBLE"]}]
    edge_column_header_map = {
                "source_id": "ORIGIN_CITY_ID",
                "target_id": "DEST_CITY_ID",
                "properties": content_type}

    rc = g.load_table_edge(file_path = edge_file_path,
                      has_header = has_header,
                      column_delimiter= column_delimiter,
                      default_source_label = default_source_label,
                      default_target_label = default_target_label,
                      default_edge_label = default_edge_label,
                      column_header_map = edge_column_header_map,
                      column_number_map=[{}],
                      data_row_start= -1,
                      data_row_end= -1)
    print (rc)


def init():

    global root
    root = Tk()
    root.title("Flight Route")
    w, h, x, y = 1000, 900, 0, 0 
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    global RES
    global STRING
    RES = StringVar()
    res_label = Label(root, textvariable=RES)
    res_label.grid(row=2, column=8, columnspan=50, sticky=N)
    STRING = '\n\nLoading Database\n\n\n\nPlease Wait...'
    RES.set(STRING)

    label_ori = Label(root, text='Origin City')
    label_ori.grid(row=1, column=0)
    label_s_month = Label(root, text='Start\nMonth')
    label_s_month.grid(row=1, column=2)
    label_s_day = Label(root, text='Start\nDay')
    label_s_day.grid(row=1, column=3)
    label_dest = Label(root, text='Destination Cities')
    label_dest.grid(row=1, column=4)
    label_e_month = Label(root, text='End\nMonth')
    label_e_month.grid(row=1, column=6)
    label_e_day = Label(root, text='End\nDay')
    label_e_day.grid(row=1, column=7)

    global listbox_ori; global listbox_dest; global listbox_s_month
    global listbox_s_day; global listbox_e_month; global listbox_e_day
    listbox_ori = Listbox(root, exportselection=0, width=30, height=55)
    listbox_ori.grid(row=2, column=0)
    listbox_s_month = Listbox(root, exportselection=0, width=5, height=55)
    listbox_s_month.grid(row=2, column=2)
    listbox_s_day = Listbox(root, exportselection=0, width=5, height=55)
    listbox_s_day.grid(row=2, column=3)
    listbox_dest = Listbox(root, selectmode=MULTIPLE, exportselection=0, width=30, height=55)
    listbox_dest.grid(row=2, column=4)
    listbox_e_month = Listbox(root, exportselection=0, width=5, height=55)
    listbox_e_month.grid(row=2, column=6)
    listbox_e_day = Listbox(root, exportselection=0, width=5, height=55)
    listbox_e_day.grid(row=2, column=7)

    graph_name = 'flights_graph'

    graphs = g.list_graphs()
    if json.loads(graphs)['status'] != 'success':
        # print 'Error!'
        STRING = 'Error Loading Graph From Database!'
        RES.set(STRING)
        exit(1)

    loaded = 0
    graphs = json.loads(graphs)['data']['graphs']
    for graph in graphs:
        if graph == graph_name:
            loaded = 1

    if not(loaded):
        load_graph('flights_graph')

    g.set_current_graph(graph_name)

    ori_label = 'ORI'
    dest_label = 'DEST'
    ori_list = g.get_vertex(vertex_label=[ori_label])
    ori_list = json.loads(ori_list)['data']['vertices']
    dest_list = g.get_vertex(vertex_label=[dest_label])
    dest_list = json.loads(dest_list)['data']['vertices']

    global ori_sort
    ori_sort = []
    for ori in ori_list:
        ori_sort.append(ori['properties'][0]['name'])
    ori_sort.sort()

    global dest_sort
    dest_sort = []
    for dest in dest_list:
        dest_sort.append(dest['properties'][0]['name'])
    dest_sort.sort()

    listbox_ori.delete(0, END)
    listbox_dest.delete(0, END)

    for ori in ori_sort:
        listbox_ori.insert(END, ori)
    for dest in dest_sort:
        listbox_dest.insert(END, dest)

    for i in range(1, 13):
            listbox_s_month.insert(END, str(i))
            listbox_e_month.insert(END, str(i))

    for i in range(1, 32):
            listbox_s_day.insert(END, str(i))
            listbox_e_day.insert(END, str(i))

    scroll_ori = Scrollbar(command=listbox_ori.yview, orient=VERTICAL)
    scroll_ori.grid(row=2, column=1, sticky='NSW')
    listbox_ori.configure(yscrollcommand=scroll_ori.set)

    scroll_dest = Scrollbar(command=listbox_dest.yview, orient=VERTICAL)
    scroll_dest.grid(row=2, column=5, sticky='NSW')
    listbox_dest.configure(yscrollcommand=scroll_dest.set)

    label_e = Label(root, text='Days Per City')
    label_e.grid(row=1, column=10, columnspan=8)
    global e1; global e2; global e3; global e4; global e5;
    global e6; global e7; global e8; global e9; global e10;
    e1 = Entry(root, width=3)
    e1.grid(row=2, column=9, sticky='N')
    e2 = Entry(root, width=3)
    e2.grid(row=2, column=10, sticky='N')
    e3 = Entry(root, width=3)
    e3.grid(row=2, column=11, sticky='N')
    e4 = Entry(root, width=3)
    e4.grid(row=2, column=12, sticky='N')
    e5 = Entry(root, width=3)
    e5.grid(row=2, column=13, sticky='N')
    e6 = Entry(root, width=3)
    e6.grid(row=2, column=14, sticky='N')
    e7 = Entry(root, width=3)
    e7.grid(row=2, column=15, sticky='N')
    e8 = Entry(root, width=3)
    e8.grid(row=2, column=16, sticky='N')
    e9 = Entry(root, width=3)
    e9.grid(row=2, column=17, sticky='N')
    e10 = Entry(root, width=3)
    e10.grid(row=2, column=18, sticky='N')

    button_s = Button(text='Search', command=SearchButton, width=50, bg='green')
    button_s.grid(row=0, column=0, columnspan=50, sticky='NSEW')

    STRING = '\n\n\n\nPlease Choose:\n\n\n\nOne Origin City\n\nStarting Date\n\n' +\
        'Up to 10 Destinations\n\nEnding Date\n\nFill In The Number Of Days For Each City\nFrom Left To Right\nIn Alphabetical Order'
    RES.set(STRING)

    path = 'logo.png'
    img = ImageTk.PhotoImage(Image.open(path))
    logo = Label(root, image=img, width=250, height=200)
    logo.grid(row=2, column=8, columnspan=20, sticky='S')

    root.mainloop()


def SearchButton():
    ori = listbox_ori.curselection()
    dest = listbox_dest.curselection()
    s_month = listbox_s_month.curselection()
    s_day = listbox_s_day.curselection()
    e_month = listbox_e_month.curselection()
    e_day = listbox_e_day.curselection()

    d1, d2, d3, d4, d5 = e1.get(), e2.get(), e3.get(), e4.get(), e5.get()
    d6, d7, d8, d9, d10 = e6.get(), e7.get(), e8.get(), e9.get(), e10.get()
    days = [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10]

    STRING = '\n\n\n\nPlease Choose:\n\n\n\nOne Origin City\n\nStarting Date\n\n' +\
        'Up to 10 Destinations\n\nEnding Date\n\nFill In The Number Of Days For Each City\nFrom Left To Right\nIn Alphabetical Order' +\
        '\n\n\n\nMissing Input!!!'

    if not(ori) or not(dest) or not(s_month) or not(s_day) or not(e_month) or not(e_day) or not(d1):
        RES.set(STRING)
        return

    if (len(dest) > 1 and not(d2)) or (len(dest) > 2 and not(d3)) or (len(dest) > 3 and not(d4)):
        RES.set(STRING)
        return

    if (len(dest) > 4 and not(d5)) or (len(dest) > 5 and not(d6)) or (len(dest) > 6 and not(d7)):
        RES.set(STRING)
        return
    if (len(dest) > 7 and not(d8)) or (len(dest) > 8 and not(d9)) or (len(dest) > 9 and not(d10)):
        RES.set(STRING)
        return

    ori_name = str(ori_sort[ori[0]])
    dest_names = []
    for d in dest:
        dest_names.append(str(dest_sort[d]))
    start_month = s_month[0] + 1
    start_day = s_day[0] + 1
    end_month = e_month[0] + 1
    end_day = e_day[0] + 1

    main(ori_name, dest_names, start_month, start_day, end_month, end_day, days)


if __name__ == '__main__':

    init()
