import pymysql
import json
from datetime import datetime
import add_function

def connection():
    conn = pymysql.connect(host='127.0.0.1',
                    user='root',
                    password='1234',
                    database='yotune', 
                    charset='utf8')
    return conn

def insert_register(reqid, reqpw, reqname, reqbirthdate, requniv, reqdept, reqstudentid):
    conn = connection()
    cursor = conn.cursor()

    try:
        check_sql = "SELECT user_id FROM yotune.users WHERE user_id = %s"
        cursor.execute(check_sql, (reqid,))
        row_num = cursor.rowcount

        if row_num > 0:
            return {"success": False, "message": "Registration failed"}
        else:
            insert_sql = """
            INSERT INTO yotune.users (user_id, password, name, birthdate, university, department, student_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (reqid, reqpw, reqname, reqbirthdate, requniv, reqdept, reqstudentid))
            conn.commit()
            return {"success": True, "message": "Registration successful"}
    
    finally:
        cursor.close()
        conn.close()

    return "fail"


def select_login(reqid, reqpw):
    conn = connection()
    cursor = conn.cursor()

    try:
        check_sql = """
            SELECT user_id, name, birthdate, university, department, student_id 
            FROM yotune.users 
            WHERE user_id = %s AND password = %s
        """
        cursor.execute(check_sql, (reqid, reqpw))
        row = cursor.fetchone()

        if row:
            birthdate_str = row[2].strftime('%Y-%m-%d') if isinstance(row[2], datetime) else row[2]

            json_object = {
                "user_id": row[0],
                "name": row[1],
                "birthdate": birthdate_str,
                "university": row[3],
                "department": row[4],
                "student_id": row[5]
            }
            return {"success": True, "message": "Login successful", "data": json_object}
        else:
            return {"success": False, "message": "Invalid id or password"}
    
    finally:
        cursor.close()
        conn.close()


def insert_course(userid, subject_info):
    conn = connection()
    cursor = conn.cursor()

    real_sem = add_function.calc_now_sem()
    sem_list = real_sem.split("-")

    try:
        insert_sql = """
        INSERT INTO yotune.courses (course_id, user_id, course_name, professor, time, classroom, year, semester)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        course_id = subject_info['courseId']
        user_id = userid
        course_name = subject_info['courseName']
        professor = subject_info['professor']
        time = add_function.convert_timetable_to_num(subject_info['time'])
        classroom = subject_info['classroom']
        year = sem_list[0]
        semester = sem_list[1]

        cursor.execute(insert_sql, (course_id, user_id, course_name, professor, time, classroom, year, semester))
        conn.commit()

        return {"success": True, "message": "Course registration successful"}
    
    finally:
        cursor.close()
        conn.close()

    return {"success": False, "message": "Course registration failed"}


def select_course(reqid, semester_info):
    conn = connection()
    cursor = conn.cursor()
    
    year = semester_info.split('-')[0]
    semester = semester_info.split('-')[1]
    
    try:
        check_sql = "SELECT * FROM yotune.courses WHERE user_id = %s AND year = %s AND semester = %s"
        cursor.execute(check_sql, (reqid, year, semester,))
        rows = cursor.fetchall()
        
        courses = []
        if rows:
            for row in rows:
                courses.append({
                    "course_idx": row[0],
                    "course_id": row[1],
                    "user_id": row[2],
                    "course_name": row[3],
                    "professor": row[4],
                    "times": row[5],
                    "classroom": row[6],
                    "year": row[7],
                    "semester": row[8]
                })
            return {"success": True, "message": "Edit time table successful", "data": courses}
        else:
            return {"success": True, "message": "No courses found", "data": courses}
    
    finally:
        cursor.close()
        conn.close()


def insert_todo(user_id, todo_info):
    conn = connection()
    cursor = conn.cursor()

    try:
        insert_sql = """
        INSERT INTO yotune.todos (user_id, title, todo_content, is_completed)
        VALUES (%s, %s, %s, %s)
        """

        title = todo_info["title"]
        todo_content = todo_info["content"]

        cursor.execute(insert_sql, (user_id, title, todo_content, False))
        conn.commit()
        return {"success": True, "message": "Todo added successfully"}

    finally:
        cursor.close()
        conn.close()

    return {"success": False, "message": "Todo registration failed"}


def select_todos(user_id):
    conn = connection()
    cursor = conn.cursor()

    try:
        check_sql = "SELECT * FROM yotune.todos WHERE user_id = %s"
        cursor.execute(check_sql, (user_id,))
        rows = cursor.fetchall()
        
        todos = []
        if rows:
            for row in rows:
                todos.append({
                    "todo_id": row[0],
                    "user_id": row[1],
                    "title": row[2],
                    "todo_content": row[3],
                    "is_completed": row[4]
                })
            return {"success": True, "message": "Edit time table successful", "data": todos}
        else:
            return {"success": True, "message": "No courses found", "data": todos}
    
    finally:
        cursor.close()
        conn.close()


def delete_todo(user_id, todo_id):
    conn = connection()
    cursor = conn.cursor()

    try:
        delete_sql = "DELETE FROM yotune.todos WHERE user_id = %s AND todo_id = %s"
        cursor.execute(delete_sql, (user_id, todo_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"success": True, "message": "Todo deleted successfully"}
        else:
            return {"success": False, "message": "Todo not found"}
    
    finally:
        cursor.close()
        conn.close()


def insert_memo(user_id, memo_info):
    conn = connection()
    cursor = conn.cursor()

    try:
        insert_sql = """
        INSERT INTO yotune.notes (user_id, course_id, course, note_title, note_content)
        VALUES (%s, %s, %s, %s, %s)
        """

        note_title = memo_info["title"]
        note_content = memo_info["content"]
        course = memo_info["course"]
        course_id = memo_info["course_id"]

        cursor.execute(insert_sql, (user_id, course_id, course, note_title, note_content))
        conn.commit()
        return {"success": True, "message": "Todo added successfully"}

    finally:
        cursor.close()
        conn.close()

    return {"success": False, "message": "Todo registration failed"}


def select_memos(user_id):
    conn = connection()
    cursor = conn.cursor()

    try:
        check_sql = "SELECT * FROM yotune.notes WHERE user_id = %s"
        cursor.execute(check_sql, (user_id,))
        rows = cursor.fetchall()
        
        memos = []
        if rows:
            for row in rows:
                memos.append({
                    "note_id": row[0],
                    "user_id": row[1],
                    "course_id": row[2],
                    "course": row[3],
                    "note_title": row[4],
                    "note_content": row[5]
                })
            return {"success": True, "message": "Edit time table successful", "data": memos}
        else:
            return {"success": True, "message": "No courses found", "data": memos}
    
    finally:
        cursor.close()
        conn.close()


def delete_memo(user_id, note_ids):
    conn = connection()
    cursor = conn.cursor()

    for note_id in note_ids:
        delete_sql = "DELETE FROM yotune.notes WHERE user_id = %s AND note_id = %s"
        cursor.execute(delete_sql, (user_id, note_id,))
        conn.commit()
    
    cursor.close()
    conn.close()

    return {"success": True, "message": "Todo deleted successfully"}


def select_semester(reqid):
    conn = connection()
    cursor = conn.cursor()

    try:
        check_sql = "SELECT year, semester FROM yotune.courses WHERE user_id = %s ORDER BY year DESC, semester DESC"
        cursor.execute(check_sql, (reqid,))
        rows = cursor.fetchall()
        
        semester = []
        if rows:
            for row in rows:
                semester.append(f"{row[0]}-{row[1]}")
            
            semester.append(add_function.calc_now_sem())
            semester = list(set(semester))
            semester.sort(reverse=True)  # 문자열로 정렬되므로, '2022-2' > '2022-1' > '2021-2' > '2021-1'
            
            return {"success": True, "message": "Edit time table successful", "data": semester}
        else:
            return {"success": True, "message": "No semester found", "data": semester}
    
    finally:
        cursor.close()
        conn.close()


def select_all_course(real_sem):
    conn = connection()
    cursor = conn.cursor()

    sem_list = real_sem.split("-")
    year = int(sem_list[0])
    sem = int(sem_list[1])

    try:
        check_sql = "SELECT * FROM yotune.def_courses WHERE year = %s AND semester = %s"
        cursor.execute(check_sql, (year, sem,))
        rows = cursor.fetchall()
        
        def_courses = []
        if rows:
            for row in rows:
                def_courses.append({
                    "course_id": row[0],
                    "course_name": row[1],
                    "professor": row[2],
                    "classroom": row[3],
                    "time": add_function.convert_num_to_timetable(row[4]),
                    "year": row[5],
                    "semester": row[6]
                })
            return {"success": True, "message": "Select all course successful", "data": def_courses}
        else:
            return {"success": True, "message": "No courses found", "data": def_courses}
    
    finally:
        cursor.close()
        conn.close()