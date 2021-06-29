from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import date

app = Flask(__name__)

app.secret_key = 'Brookes3099'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="web"
)

cursor = mydb.cursor(buffered=True)
SQLrows = cursor.rowcount
today = date.today()
currentDate = today.strftime("%y/%m/%d")

innerJoin = None
TopicID = None
is_admin = 1

@app.route('/')
def hello_world():
    return redirect(url_for('topics'))


@app.route('/home')
def home():
    return redirect(url_for('topics'))


@app.route('/home', methods=['GET', 'POST'])
def home_post():
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    email = request.form['email']
    password = request.form['password']

    sql = "INSERT INTO users (id, fname , lname , email , password) VALUES (0, %s, %s, %s, %s)"
    val = (firstname, lastname, email, password)

    cursor.execute(sql, val)
    mydb.commit()
#sessions
    sqlReturn = 'SELECT * FROM users WHERE email = %s AND password = %s'
    valReturn = (email, password)
    cursor.execute(sqlReturn, valReturn)
    account1 = cursor.fetchone()
    
    session["email"] = email
    session['password'] = password
    session['firstName'] = firstname
    session['lastName'] = lastname
    session['id'] = account1[0]

    return redirect(url_for('topics'))


@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        email = request.form['logEmail']
        password = request.form['logPassword']

        sql = 'SELECT * FROM users WHERE email = %s AND password = %s'
        val = (email, password)
        cursor.execute(sql, val)
        account = cursor.fetchone()
        mydb.commit()

        if account:
            
            session["is_admin"] = account[5]
            session["email"] = account[3]
            session['password'] = account[4]

            session['firstName'] = account[1]
            session['lastName'] = account[2]
            session['id'] = account[0]
            # Redirect to topics
            return redirect(url_for('topics'))
        else:
            
            return redirect(url_for('topics', msg="incorrect Credientials"))


@app.route('/topics', methods=['GET'])
def topics():
    cursor.execute("SELECT * FROM topic;")
    data = cursor.fetchall()
    
    mydb.commit()

    return render_template('topics.html', value=data)


@app.route('/status', methods=['POST'])
def status():
    return session['id']


@app.route('/edit-profile')
def editProfile():
    if 'id' in session:
        id = session['id']
        return render_template('account.html')
    else:
        return render_template('nologin.html')


@app.route('/edit-profile', methods=['POST'])
def editProfile_post():
    id = session["id"]

    edit_firstname = request.form['edit-firstname']
    edit_lastname = request.form['edit-lastname']
    edit_email = request.form['edit-email']
    edit_password = request.form['edit-password']
    data = cursor.fetchall(3)

    sql = 'UPDATE users SET fname= %s , lname= %s , email= %s , password= %s WHERE id = %s'
    val = (edit_firstname, edit_lastname, edit_email, edit_password, id)
    cursor.execute(sql, val)
    if edit_email == data:
        return redirect(url_for('edit-profile', msg="Email already in use"))

    mydb.commit()

    return redirect(url_for('topics', msg="details changed!"))


@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/topics')


@app.route('/submit-topic')
def submitTopicTemp():
    if 'id' in session:
        id = session['id']
        return render_template('submitTopic.html')
    else:
        return render_template('nologin.html')


@app.route('/submit-topic', methods=['POST'])
def submit_topic():
    topic_title = request.form['topicTitle']
    topic_subject = request.form['topicSubject']
    sqlIn = "INSERT INTO topic (topic_id, topic_title , topic_subject , topic_date) VALUES (0, %s, %s, %s)"
    valIn = (topic_title, topic_subject, currentDate)
    cursor.execute(sqlIn, valIn)
    mydb.commit()

    return redirect(url_for('topics'))


@app.route('/claims/<int:topic_id>', methods=['GET'])
def inTopic(topic_id):
    sql = "SELECT topic_id FROM topic;"
    cursor.execute(sql)
    data1 = cursor.fetchall()

    innerJoin = 'SELECT topic.topic_id, claim.topic_id , claim.claim_title, claim.claim_subject, claim.claim_date FROM topic INNER JOIN claim ON topic.topic_id = claim.topic_id;'
    cursor.execute(innerJoin)
    myresult = cursor.fetchall()

    cursor.execute("SELECT * FROM claim;")
    data = cursor.fetchall()

    mydb.commit()

    return render_template('claims.html', valueClaim=myresult, valueTopic=data1, topicID=topic_id)


#16:08 - trying to make the add claim one route. topicID is working.

@app.route('/add-claim/<int:topic_id>', methods=['GET'])
def addClaim(topic_id):
    if 'id' in session:
        id = session['id']

        cursor.execute("SELECT topic_id from topic")
        data = cursor.fetchall()
        topicID = data[0]

        cursor.execute("SELECT * FROM claim")
        data2 = cursor.fetchall()
        return render_template('addClaim.html', valueClaim = data2, topicID=topic_id)
    else:
        return render_template('nologin.html')


@app.route('/add-claim/<int:topic_id>', methods=['POST', 'GET'])
def addClaim_post(topic_id):
    claim_title = request.form['claimTitle']
    claim_subject = request.form['claimSubject']
    fTopicId = request.form['fTopicId']
    

    cursor.execute("SELECT topic_id from topic")
    data = cursor.fetchall()
    topicID = data[0]

    sqlIn = "INSERT INTO claim (claim_id, claim_title , claim_subject , claim_date, topic_id) VALUES (0, %s, %s, %s, %s)"
    valIn = (claim_title, claim_subject, currentDate, fTopicId)
    cursor.execute(sqlIn, valIn)
    mydb.commit()

    #return render_template('claims.html',topicID=topic_id)
    return redirect(url_for('topics',topic_id=topic_id))


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    if data[4] == 1:
        
        
        data = cursor.fetchall()



        return render_template('admin.html', data=data)

    else:
        return redirect(url_for('topics'))