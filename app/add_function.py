from datetime import datetime
import random


def calc_now_sem():
    now = datetime.now()
    year = now.year

    if 1 <= now.month <= 2:
        period = 1
    elif 3 <= now.month <= 6:
        period = 2
    elif 7 <= now.month <= 8:
        period = 3
    else:
        period = 4

    now_sem = f"{year}-{period}"

    return now_sem

def find_course_by_time(target, time, col):
    for course in target:
        if time in list(map(int, course['times'].split('|'))):
            return course[col]
    return "None"


def find_consecutive_elements_with_plus_five(input_nums):
    output_dict = {"start":[], "seq": [], "rep":[]}
    for nums in input_nums:
        nums_set = set()
        nums_set = set(nums)
        checked = set()
        result_dict = {}

        for num in nums:
            if num in checked:
                continue

            current = num
            sequence = []

            while (current + 5) in nums_set:
                sequence.append(current)
                checked.add(current)
                current += 5

            if sequence:
                sequence.append(current)
                checked.add(current)
                result_dict[num] = sequence

        for key, sequence in result_dict.items():
            output_dict["start"].append(key)
            output_dict["seq"].append(sequence)
            output_dict["rep"].append(len(sequence))
        
    return output_dict


def assign_colors(courses):
    PASTEL_COLORS = [
        "#FFB3BA", "#FFDFBA", "#FFB347", "#FFCC33", "#FFCC99",
        "#CCCCFF", "#99FF99", "#FFCCCC", "#FFD1DC", "#FFDEAD",
        "#FFE4E1", "#FFE4B5", "#FFEBCD", "#FFE4C4", "#FFDAB9",
        "#EEE8AA", "#F0E68C", "#D3FFCE", "#CCE8CF", "#FF9AA2"
    ]

    course_colors = {}
    available_colors = PASTEL_COLORS[:]
    random.shuffle(available_colors)

    for course in courses:
        course_name = course['course_name']
        if course_name not in course_colors:
            course_colors[course_name] = available_colors.pop()
            if not available_colors:
                available_colors = PASTEL_COLORS[:]
                random.shuffle(available_colors)

    return course_colors



def creat_table(test_dict):
    times = []

    for course in test_dict['data']:
        times.append(list(map(int, course['times'].split('|'))))

    test_re = find_consecutive_elements_with_plus_five(times)
    course_colors = assign_colors(test_dict['data'])

    html_t = [[1, 2, 3, 4, 5], 
              [6, 7, 8, 9, 10], 
              [11, 12, 13, 14, 15], 
              [16, 17, 18, 19, 20], 
              [21, 22, 23, 24, 25], 
              [26, 27, 28, 29, 30], 
              [31, 32, 33, 34 ,35], 
              [36, 37, 38, 39 ,40], 
              [41, 42, 43, 44 ,45]]

    for t in test_re['seq']:
        for i in range(9):
            for j in range(5):
                crt = (i*5)+j+1
                if crt in t:
                    if crt == min(t):
                        course_name = find_course_by_time(test_dict['data'], min(t), "course_name")
                        classroom = find_course_by_time(test_dict['data'], min(t), "classroom")
                        professor = find_course_by_time(test_dict['data'], min(t), "professor")
                        course_id = find_course_by_time(test_dict['data'], min(t), "course_id")
                        color = course_colors[course_name]
                        html_t[i][j] = f'<td rowspan="{len(t)}" style="background-color: {color}; cursor: pointer;" onclick="onTableCellClick(\'{course_name}\', \'{course_id}\')"><strong>{course_name}</strong><br>{classroom}<br>{professor}</td>'
                        continue
                    else:
                        html_t[i][j] = ""
                        continue

    for last in times:
        for i in range(9):
            for j in range(5):
                if type(html_t[i][j]) == int:
                    crt = (i*5)+j+1
                    if crt in last:
                        course_name = find_course_by_time(test_dict['data'], crt, "course_name")
                        classroom = find_course_by_time(test_dict['data'], crt, "classroom")
                        professor = find_course_by_time(test_dict['data'], crt, "professor")
                        course_id = find_course_by_time(test_dict['data'], crt, "course_id")
                        color = course_colors[course_name]
                        html_t[i][j] = f'<td style="background-color: {color}; cursor: pointer;" onclick="onTableCellClick(\'{course_name}\', \'{course_id}\')"><strong>{course_name}</strong><br>{classroom}<br>{professor}</td>'
                        continue

    result = ""
    for idx, r in enumerate(html_t):
        result = result + f'<tr style="height: 80px;"><td>{idx+1}</td>'
        for c in r:
            if type(c) == int:
                result = result + "<td></td>"
            else:
                result = result + c
        result = result + "</tr>"
        
    return result


def convert_num_to_timetable(str_num):
    result_str = ""
    lst_num = str_num.split("|")
    for num in lst_num:
        for i, each_time in enumerate(["1교시", "2교시", "3교시", "4교시", "5교시", "6교시", "7교시", "8교시", "9교시"]):
            for j, each_day in enumerate(["월요일", "화요일", "수요일", "목요일", "금요일"]):
                if (i*5)+j+1 == int(num):
                    result_str = result_str + f"{each_day} {each_time}, "
                    
                    
    return result_str[:-2]


def convert_timetable_to_num(timetable_str):
    times = ["1교시", "2교시", "3교시", "4교시", "5교시", "6교시", "7교시", "8교시", "9교시"]
    days = ["월요일", "화요일", "수요일", "목요일", "금요일"]

    timetable_list = timetable_str.split(", ")
    result_list = []
    
    for entry in timetable_list:
        day, time = entry.split()
        day_index = days.index(day)
        time_index = times.index(time)
        num = time_index * 5 + day_index + 1
        result_list.append(str(num))
    
    return '|'.join(result_list)