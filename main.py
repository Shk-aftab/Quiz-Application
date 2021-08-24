from crypt import methods
from flask import Flask, request, render_template, flash,  redirect, url_for, send_from_directory, send_file, session
# import pandas as pd
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from Teacher import views as teachUrl
from Student import views as stdUrl
from Admin import views as adminUrl
import test
import flask_excel as excel
# from breadcrumb import breadcrumb
# from flaskwebgui import FlaskUI

UPLOAD_FOLDER = './images'
ALLOWED_EXTENSIONS = {'jpg'}
FILEPATH = ''

app = Flask('app')
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def check_user(page):
    if session.get("email"):
        return page
    else:
        return 'login.html'
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploadfile', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        f = request.files['upfile']
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
            FILEPATH = os.path.join(app.config['UPLOAD_FOLDER']) + '/'+filename 
            print("FILEPATH :", FILEPATH)
            msg = test.insertImage(FILEPATH)
            session['image_ids'] = test.readAllBlobData()
            print(msg)
            url = '/teacher/AddQuiz?msg=' + msg
            return redirect(url) #'file uploaded successfully'

@app.route('/', methods=['GET', 'POST'])
def Home():  
   return render_template('home.html')



app.add_template_filter(test.filter_shuffle , name='shuffle')

app.add_url_rule('/admin/Home', view_func = adminUrl.AdminHome)
app.add_url_rule('/admin/users', view_func = adminUrl.AdminUsers)
app.add_url_rule('/admin/teachers', view_func = adminUrl.AdminTeachers)
app.add_url_rule('/admin/students', view_func = adminUrl.AdminStudents)
app.add_url_rule('/admin/Updateusers', view_func = adminUrl.AdminUpdateUser , methods=['GET','POST'])
app.add_url_rule('/admin/Updatestudent', view_func = adminUrl.AdminUpdateStudent , methods=['GET','POST'])
app.add_url_rule('/admin/Updateteacher', view_func = adminUrl.AdminUpdateTeacher , methods=['GET','POST'])



app.add_url_rule('/teacher/Home', view_func = teachUrl.TeacherHome)
app.add_url_rule('/teacher/AddCourse', view_func = teachUrl.AddCourse , methods=['GET','POST'])
app.add_url_rule('/teacher/AllCourse', view_func = teachUrl.AllCourses , methods=['GET','POST'])
app.add_url_rule('/teacher/Course', view_func = teachUrl.TeacherCourse , methods=['GET','POST'])
app.add_url_rule('/teacher/DeleteCourse', view_func = teachUrl.DeleteCourse , methods=['GET','POST'])
app.add_url_rule('/teacher/AddQuiz', view_func = teachUrl.AddQuiz , methods=['GET','POST'])
app.add_url_rule('/teacher/AllQuiz', view_func = teachUrl.AllQuizes , methods=['GET','POST'])
app.add_url_rule('/teacher/quiz', view_func = teachUrl.QuizQuestions , methods=['GET','POST'])
app.add_url_rule('/teacher/EditQuiz', view_func = teachUrl.EditQuiz , methods=['GET','POST'])
app.add_url_rule('/teacher/DeleteQuiz', view_func = teachUrl.DeleteQuiz , methods=['GET','POST'])
app.add_url_rule('/teacher/AddQuestion', view_func = teachUrl.AddQuestion , methods=['GET','POST'])
app.add_url_rule('/teacher/EditQuestion', view_func = teachUrl.EditQuestion , methods=['GET','POST'])
app.add_url_rule('/teacher/DeleteQuestion', view_func = teachUrl.DeleteQuestion , methods=['GET','POST'])
app.add_url_rule('/teacher/enrolled', view_func = teachUrl.EnrolledQuiz , methods=['GET','POST'])
app.add_url_rule('/teacher/StudentResult', view_func = teachUrl.StudentResult , methods=['GET','POST'])
app.add_url_rule('/teacher/pdfquiz', view_func = teachUrl.pdfquiz , methods=['GET','POST'])
# app.add_url_rule('/teacher/excelquizscore', view_func = teachUrl.excelQuizScore , methods=['GET','POST'])




app.add_url_rule('/student/Home', view_func = stdUrl.StudentHome)
app.add_url_rule('/student/AllTeachers', view_func = stdUrl.AllTeachers)
app.add_url_rule('/student/teacher', view_func = stdUrl.Teacher , methods=['GET','POST'])
app.add_url_rule('/student/AllCourse', view_func = stdUrl.AllCourse)
app.add_url_rule('/student/course', view_func = stdUrl.Course , methods=['GET','POST'])
app.add_url_rule('/student/Enroll_course', view_func = stdUrl.Enroll_Course , methods=['GET','POST'])
app.add_url_rule('/student/AllQuizes', view_func = stdUrl.AllQuiz)
app.add_url_rule('/student/quiz', view_func = stdUrl.Quiz , methods=['GET','POST'])
app.add_url_rule('/student/Enroll_quiz', view_func = stdUrl.Enroll_Quiz , methods=['GET','POST'])
app.add_url_rule('/student/Start_quiz', view_func = stdUrl.Start_Quiz , methods=['GET','POST'])
app.add_url_rule('/student/AnswerQuestion', view_func = stdUrl.Answer_Question , methods=['GET','POST'])
app.add_url_rule('/student/result', view_func = stdUrl.View_Result , methods=['GET','POST'])


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     page = check_user("index.html")
#     if page == 'login.html':
#         return render_template('login.html')
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try :
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            email = str(request.form['email'])
            password = str(request.form["password"])
            print(email , 'email' , password , 'password')
            # mydoc = cursor.execute("SELECT * from USER")
            mydoc = cursor.execute("SELECT * from USER WHERE USER_EMAIL = ? AND PASSWORD = ? ", (email, password))
            myresult = mydoc.fetchone()

            # print(myresult , type(myresult[0]) , 'myresult' , mydoc)
            # cursor.close()
            # conn.close()
            if myresult:
                if myresult[-1]:
                    session['email'] = str(myresult[1])
                    session['user_id'] = myresult[0]
                    session['user_role'] = str(myresult[4])
                    session['image_ids'] = test.readAllBlobData()
                    if myresult[4] == 'S':
                        session['username'] , session['role_id']  = cursor.execute("SELECT STUDENT_NAME , STUDENT_ID from STUDENT WHERE USER_ID = ?", (myresult[0],)).fetchone()
                        # course_ids = cursor.execute("SELECT COURSE_ID from ENROLLMENT WHERE STUDENT_ID = ?" , ( session['role_id'],)).fetchall()                    
                        session['courses'] = cursor.execute("SELECT COURSE_ID , COURSE_NAME , TEACHER_ID from COURSE WHERE COURSE_ID IN ( SELECT COURSE_ID from ENROLLMENT_COURSE WHERE STUDENT_ID = ? )" , ( session['role_id'] , )).fetchall()
                        session['quizes'] = cursor.execute("SELECT QUIZ_ID , QUIZ_NAME , TEACHER_ID , COURSE_ID from QUIZ WHERE QUIZ_ID IN ( SELECT QUIZ_ID from ENROLLMENT_QUIZ WHERE STUDENT_ID = ? )" , ( session['role_id'] , )).fetchall()
                        cursor.close()
                        conn.close()
                        # print(course_ids , "course_ids")
                        return redirect('/student/Home')
                    elif myresult[4] == 'T':
                        session['username'] , session['role_id'] = cursor.execute("SELECT TEACHER_NAME , TEACHER_ID from TEACHER WHERE USER_ID = ?", (myresult[0],)).fetchone()
                        session['courses'] = cursor.execute("SELECT COURSE_ID , COURSE_NAME from COURSE WHERE TEACHER_ID = ?" , ( session['role_id'],)).fetchall()
                        cursor.close()
                        conn.close()
                        return redirect('/teacher/Home')
                    else:
                        return redirect('/admin/Home')
                else:
                    return render_template('login.html', msg='DeActived User. Contact Admin to get Activated.')
            else:
                return render_template('login.html', msg='email id or password is not matching')
        
        except Exception as e:
            return render_template('login.html', msg=e)


@app.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            fname = str(request.form["fname"])
            lname = str(request.form["lname"])
            password = str(request.form["password"])
            email = str(request.form['email'])
            phone = str(request.form['phoneNo'])
            
            role = (request.form['role'])
            print('role ======' , role)
            msg = ''
            cursor.execute("SELECT * from USER WHERE USER_EMAIL = ?", (str(email),))
            if cursor.fetchall():
                return render_template("sign.html", msg="Email Already Exist Try Different")
            else:
                cursor.execute("INSERT INTO USER(USER_EMAIL, PASSWORD, PHONE_NO , role ) VALUES (?, ?, ? , ?)",
                            (str(email), str(password), int(phone) , str(role)))
                conn.commit()

                mydoc = cursor.execute("SELECT * from USER WHERE USER_EMAIL = ?" , (str(email),))
                myresult = mydoc.fetchone()
                if role == 'S':
                    cursor.execute("UPDATE STUDENT SET STUDENT_NAME = ? WHERE USER_ID = ?",
                                (str(fname) + ' ' + str(lname), int(myresult[0])))
                    conn.commit()
                    msg += 'Successfully Registered'
                else:                    
                    cursor.execute("UPDATE Teacher SET teacher_name = ? WHERE USER_ID = ?",
                                (str(fname) + ' ' + str(lname), int(myresult[0])))
                    conn.commit()
                    msg += 'Successfully Registered. Contact Admin to active the account.'


                # print('Singin User :', myresult)
                # session['username'] = str(fname)+" "+str(lname)
                # session['email'] = str(email)
                # session['user_id'] = myresult[0]
                # session['user_role'] = str(myresult[4])
            cursor.close()
            conn.close()
            
            return render_template('login.html', msg = msg  )

        except Exception as e:
            return render_template('sign.html', msg=e)
        

@app.route("/login_page", methods=["GET", "POST"])
def login_page():
    return render_template('login.html')


@app.route("/sign_page", methods=["GET", "POST"])
def sign_page():
    return render_template('sign.html')


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect('/login_page')

# def excelQuizScore():
#     return excel.make_response_from_array([[1, 2], [3, 4]], "csv")

if __name__ == "__main__":   
    # excel.init_excel(app) 
    app.run(host='0.0.0.0', port=3000 ) # localhost
    # app.run(host='192.168.0.106', port=8081 )  #Router
    # app.run()