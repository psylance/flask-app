"""
NOTE: Headers should be as follows =>   1. Content-Type = application/json
                                        2. custom-token-header = JWT generated after login

"""

from flask import Flask, request, jsonify, make_response
from functools import wraps
from PIL import Image
from io import BytesIO
import sqlite3
import jwt
import requests
import markdown


app = Flask(__name__)    # Initialization of Flask
app.config['SECRET_KEY'] = 'strong_secret_key'    # Secret key to be used for creating JWT


conn = sqlite3.connect('survey.db')    # sqlite3 database
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS surveys (
             survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
             survey_name TEXT NOT NULL CHECK (length(survey_name) > 0)
            )''')    # Creating survey table if it does not exist

c.execute('''CREATE TABLE IF NOT EXISTS questions (
             survey_id INTEGER,
             question_id INTEGER CHECK (length(question_id) > 0),
             question_body TEXT CHECK (length(question_body) > 0),
             answer TEXT CHECK (answer == 'yes' OR answer == 'no') COLLATE NOCASE
            )''')    # Creating questions table if it does not exist


def authenticate(check):    # Utilized for checking validity and existance of token
    @wraps(check)
    def in_wraps(*args, **kwargs):
        token = None
        if 'custom-token-header' in request.headers:
            token = request.headers['custom-token-header']
        if not token:
            return jsonify({'ERROR': 'No Token'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'ERROR': 'Invalid Token'}), 403
        return check(*args, **kwargs)
    return in_wraps


@app.route('/survey/create', methods=['POST'])    # Utilizaed to create survey (only for authorizaed user)
@authenticate
def create():
    data = request.get_json()

    conn = sqlite3.connect('survey.db')
    c = conn.cursor()

    try:
        survey_name = data['name']
        c.execute('INSERT INTO surveys VALUES (NULL, ?)', (survey_name,))
        c.execute('SELECT survey_id FROM surveys WHERE survey_name = ?', (survey_name,))
    except:
        return {"ERROR": "Invalid Name"}

    sid = c.fetchone()
    sid = sid[0]
    
    try:
        questions = data['questions']
    
        for question in questions:
            qid = question['qid']
            qbody = question['qbody']
            c.execute('INSERT INTO questions VALUES (?, ?, ?, NULL)', (sid, qid, qbody))
    except:
        return {"ERROR": "Invalid Input"}

    conn.commit()
        
    return {"OK": "Survey '" + survey_name + "' created"}


@app.route('/survey/take/<survey_id>', methods=['POST'])    # Utilizaed to take survey (only for authorizaed user)
@authenticate
def take(survey_id):
    data = request.get_json()
    sid = survey_id
    qid = data['qid']
    answer = data['answer']
    
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    
    try:
        c.execute('UPDATE questions SET answer = ? WHERE survey_id = ? AND question_id = ?', (answer, sid, qid))
    except:
        return {"ERROR": "Invalid Input"}
    conn.commit()

    return {"OK": "Question " + str(qid) + " answered"}


@app.route('/survey')    # Utilized to view survey (only for authorizaed user)
@authenticate
def view():
    view = [[]]

    conn = sqlite3.connect('survey.db')
    c = conn.cursor()

    c.execute('SELECT * FROM surveys')
    surveys = c.fetchall()

    c.execute('SELECT * FROM questions')
    questions = c.fetchall()

    i = 0
    for sid, sname in surveys:
        view[i].append("Survey: " + sname)
        for qsid, qid, qbody, ans in questions:
            if sid == qsid:
                view[i].append("Question: " + qbody)
                if ans == None:
                    view[i].append('Answer: Not answered') 
                else:
                    view[i].append("Answer: " + ans)
                view[i].append('------------------')
        view.append([])
        i += 1
    view.pop()

    return jsonify(view)


@app.route('/login', methods=['POST'])    # Login and create token
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if len(username) > 0 and len(password) > 0:
        token = jwt.encode(
            {'username': username , 'password': password},
            app.config['SECRET_KEY']
        )
        return jsonify({'token': token.decode()})
    
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})   


@app.route('/thumbnail/<path:image_url>')    # Resize given image into a 50x50 pixel image
def thumbnail(image_url):
    response = requests.get(image_url)

    try:
        img = Image.open(BytesIO(response.content))
    except:
        return{"ERROR": "Not an image URL"}

    extention = img.format
    img.save('image.' + extention)
    
    resized_img = img.resize((50, 50))
    resized_img.save('resized.' + extention)

    return {"OK": "Image successfully resized"} 

@app.route('/')
def index():
    with open('README.md', 'r') as mk_file:
        read = mk_file.read()

    return markdown.markdown(read)


app.run()    # Start Flask app