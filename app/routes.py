from flask import Flask, url_for, session, redirect, render_template, request, jsonify
from flask_mail import Mail, Message
import maria_dao
import json
import os
import io
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
import add_function
import stt

app = Flask(__name__)      

app.config['MAIL_SERVER'] = 'smtp.naver.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jy981205_@naver.com'
app.config['MAIL_PASSWORD'] = 'PKWGGBKHET69'
app.config['MAIL_DEFAULT_SENDER'] = ('Your Name', 'jy981205_@naver.com')

mail = Mail(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(app.root_path, "stt", "robust-summit-425707-d7-62176ec3f4d7.json")

ffmpeg_path = os.path.join(app.root_path, "stt", "ffmpeg-2024-06-06-git-d55f5cba7b-essentials_build", "bin", "ffmpeg.exe")
ffprobe_path = os.path.join(app.root_path, "stt", "ffmpeg-2024-06-06-git-d55f5cba7b-essentials_build", "bin", "ffprobe.exe")

os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path


def convert_to_wav(file_path):
    try:
        print(f"Converting {file_path} to WAV format using ffmpeg at {AudioSegment.converter}.")
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_channels(1)  # 오디오를 모노로 변환
        wav_path = file_path.rsplit('.', 1)[0] + '.wav'
        audio.export(wav_path, format='wav')
        print(f"Converted file saved to: {wav_path}")
        return wav_path
    except Exception as e:
        print(f"Error during conversion: {e}")
        raise e


def long_running_recognize(file_path):
    print(f"Starting long running speech recognition for file: {file_path}")
    client = speech.SpeechClient()

    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code="ko-KR",
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=3600)  # 최대 1시간 대기

    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)

    return "\n".join(transcripts)


def process_audio_file(input_file_path):
    if not os.path.exists(input_file_path):
        return f"File not found: {input_file_path}"
    else:
        try:
            print(f"File found: {input_file_path}")
            wav_file_path = convert_to_wav(input_file_path)
            transcript = long_running_recognize(wav_file_path)
            print("Transcript:")
            print(transcript)
            return transcript
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)


@app.route('/contact')
def contact():
  return render_template('contact.html')


@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    data = request.get_json()
    user_email = data['email']
    subject = user_email + " 에게서 온 " + data['subject']
    body = data['message']

    msg = Message(subject, recipients=['jy981205_@naver.com'])
    msg.body = f"From: {user_email}\n\n{body}"

    mail.send(msg)

    return jsonify({'success': True})


@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', username=session['user_id'])
    else:
        return render_template('index.html')


@app.route('/memo', methods=['GET', 'POST'])
def memo():
    if request.method == 'POST':
        data = request.get_json()
        selected_semester = data.get('semester')
        if selected_semester:
            session['selected_semester'] = selected_semester
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})

    course_dict = {"course_name": [], 
                   "course_id": []}

    if 'user_id' in session:
        course_object = maria_dao.select_course(session['user_id'], session['selected_semester'])
        semester_object = maria_dao.select_semester(session['user_id'])
        memo_object = maria_dao.select_memos(session['user_id'])

        for course in course_object["data"]:
            if course['user_id'] == session['user_id']:
                course_dict["course_name"].append(course['course_name'])
                course_dict["course_id"].append(course["course_id"])

        return render_template('memo.html', username=session['user_id'], courses = course_dict, enumerate=enumerate, memos = memo_object['data'], sem_data=semester_object['data'], now_sem=session['selected_semester'])
    else:
        return redirect(url_for('login'))


@app.route('/add_memo', methods=['POST'])
def add_memo():
    req_data = request.get_json()
    print(req_data)
    result = maria_dao.insert_memo(session['user_id'], req_data)
    return jsonify({'status': 'success'})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        transcript = process_audio_file(file_path)
        print(transcript)
        return jsonify({'transcript': transcript})


@app.route('/delete_memos', methods=['POST'])
def delete_memos():
    req_data = request.get_json()
    memo_ids = req_data.get('memo_ids')
    result = maria_dao.delete_memo(session['user_id'], memo_ids)
    return jsonify({'status': 'success'})


@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    real_sem = add_function.calc_now_sem()
    if request.method == 'POST':
        data = request.get_json()
        selected_semester = data.get('semester')
        if selected_semester:
            session['selected_semester'] = selected_semester
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})

    if 'user_id' in session:
        todo_object = maria_dao.select_todos(session['user_id'])
        semester_object = maria_dao.select_semester(session['user_id'])
        
        if 'selected_semester' in session:
            cource_object = maria_dao.select_course(session['user_id'], session['selected_semester'])
            result = add_function.creat_table(cource_object)
        else:
            session['selected_semester'] = add_function.calc_now_sem()
            cource_object = maria_dao.select_course(session['user_id'], session['selected_semester'])
            result = add_function.creat_table(cource_object)

        if cource_object['success'] and todo_object['success']:
            all_course = maria_dao.select_all_course(real_sem)
            return render_template('timetable.html', username=session['user_id'], all_course = all_course["data"], course_data=result, todo_data=todo_object['data'], sem_data=semester_object['data'], real_sem=real_sem, now_sem=session['selected_semester'])
        else:
            return render_template('timetable.html', username=session['user_id'], all_course = all_course["data"], course_data=[], todo_data=[], sem_data=[], real_sem=real_sem, now_sem=session['selected_semester'])
    else:
        return redirect(url_for('login'))


@app.route('/add_todo', methods=['POST'])
def add_todo():
    req_data = request.get_json()
    result = maria_dao.insert_todo(session['user_id'], req_data)
    return jsonify({'status': 'success'})


@app.route('/delete_todo', methods=['POST'])
def delete_todo():
    req_data = request.get_json()
    result = maria_dao.delete_todo(session['user_id'], req_data['todo_id'])
    return jsonify({'status': 'success'})


@app.route('/add_course', methods=['POST'])
def add_course():
    req_data = request.get_json()
    result = maria_dao.insert_course(session['user_id'], req_data)
    return jsonify({'success': True})


@app.route('/account_setting')
def account_setting():
    if 'user_id' in session:
        return render_template('account_setting.html', username=session['user_id'])
    else:
        return redirect(url_for('login'))
  

@app.route('/introduction')
def introduction():
  return render_template('introduction.html')


@app.route('/developer')
def developer():
  return render_template('developer.html')


@app.route('/login')
def login():
  return render_template('login.html')


@app.route('/login_do', methods=['GET', 'POST'])
def login_do():
  if request.method == 'POST':
    req_data = request.get_json()
    reqid = req_data.get('user_id')
    reqpw = req_data.get('password')
    
    content = maria_dao.select_login(reqid, reqpw) 

    if content['success']:
      session['user_id'] = content['data']['user_id']
      session['name'] = content['data']['name']
      session['birthdate'] = content['data']['birthdate']
      session['university'] = content['data']['university']
      session['department'] = content['data']['department']
      session['student_id'] = content['data']['student_id']

      return content
  return content


@app.route('/register')
def register():
  return render_template('register.html')


@app.route('/register_do', methods=['GET', 'POST'])
def register_do():
  if request.method == 'POST':
      req_data = request.get_json()
      reqid = req_data.get('user_id')
      reqpw = req_data.get('password')
      reqname = req_data.get('user_name')
      reqbirthdate = req_data.get('user_birthdate')
      requniv = req_data.get('user_univ')
      reqdept = req_data.get('user_dept')
      reqstudentid = req_data.get('user_student_id')
    
      content = maria_dao.insert_register(reqid, reqpw, reqname, reqbirthdate, requniv, reqdept, reqstudentid) 

  return content


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    session.pop('selected_semester', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
  app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
  app.run(debug=True)