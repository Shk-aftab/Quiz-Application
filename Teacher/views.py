# from Student.views import Course
from datetime import datetime
from flask import Flask, request, render_template, flash,  redirect, url_for, send_from_directory, send_file, session , json , make_response
import pandas as pd
import os
import sqlite3
import random
import test
from breadcrumb import breadcrumb
import pdfkit 


def check_user(page):
    if session.get("email"):
        if session.get("user_role") == 'T':
            return [page]
        else:
            return [page , "You Don't have these previlages." ]
    else:
        return ['login.html']

# @app.route('/teacherHome', methods=['GET', 'POST'])
@breadcrumb('Home')
def TeacherHome():
    page = check_user("/teacherSite/teacherHome.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()

            n_course = len(  session['courses']  )            

            n_quize = cursor.execute(" SELECT count(QUIZ_ID) from QUIZ WHERE TEACHER_ID = ? " , ( session['role_id'] , )).fetchone()[0]
            n_student = cursor.execute(" select count(distinct(e.student_id)) from Enrollment_Course e where e.course_id in ( select c.course_id from Course c WHERE TEACHER_ID = ? ) " , ( session['role_id'] , )).fetchone()[0]
            
            cursor.close()
            conn.close()
        except Exception as e:
            msg = "Some Error : " + str(e) 
            print("errr", msg)
        return render_template(page[0] ,  n_course = n_course , n_quize = n_quize , n_student = n_student )  

@breadcrumb('Add Course')
def AddCourse():
    page = check_user("/teacherSite/addCourse.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        if request.method == "POST":
            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                course_name = str(request.form['course_name']).strip()
                enroll_key = str(request.form["enroll_key"]).strip()
                if enroll_key:
                    cursor.execute("INSERT INTO COURSE(TEACHER_ID, COURSE_NAME, ENROLLMENT_KEY) VALUES (?, ?, ?)",
                                    ( session['role_id'], course_name, enroll_key))
                    conn.commit()
                else:
                    cursor.execute("INSERT INTO COURSE(TEACHER_ID, COURSE_NAME) VALUES (?, ?)",
                                    ( session['role_id'], course_name))
                    conn.commit()
                session['courses'] = cursor.execute("SELECT COURSE_ID , COURSE_NAME from COURSE WHERE TEACHER_ID = ?" , ( session['role_id'],)).fetchall()

                msg = "Course " +course_name + " Scuccefully Add. "
                print(course_name , 'course_name' , enroll_key , 'enroll_key')
                print('Hey')
                cursor.close()
                conn.close()

            except Exception as e:
                msg = "Some Error : " + str(e) 

            return render_template(page[0] , msg1 = msg )

        else :
            return render_template(page[0])

def DeleteCourse():
    page = check_user("/teacherSite/allCourses.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        cid = request.args.get('cid',type = int)        
        try:
            print('cid===', cid)
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()     
            
            cursor.execute("DELETE FROM COURSE WHERE course_id = ? ", ( cid , ))
            conn.commit()

            session['courses'] = cursor.execute("SELECT COURSE_ID , COURSE_NAME from COURSE WHERE TEACHER_ID = ?" , ( session['role_id'],)).fetchall()

            conn.execute("PRAGMA foreign_keys = OFF")
            cursor.close()
            conn.close()
        except Exception as e:
            msg = "Some Error : " + str(e) 
            print("errr", msg)
        return redirect('/teacher/AllCourse')

@breadcrumb('All Courses')
def AllCourses():
    page = check_user("/teacherSite/allCourses.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        return render_template(page[0] , courses = session['courses'] )

@breadcrumb('Course')
def TeacherCourse():
    page = check_user("/teacherSite/course.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        cid = request.args.get('id',type = int)
        name = request.args.get('name', type = str)
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()

            quizes = cursor.execute("SELECT QUIZ_ID , QUIZ_NAME , QUIZ_MARKS , QUIZ_STARTDATE , QUIZ_ENDDATE from QUIZ WHERE COURSE_ID = ? AND TEACHER_ID = ? " , ( cid , session['role_id'] , )).fetchall()
            cursor.close()
            conn.close()

        except Exception as e:
                msg = "Some Error : " + str(e) 
        return render_template(page[0] , course = [ cid, name ] , quizes = quizes)

@breadcrumb('Add Quiz')
def AddQuiz():
    page = check_user("/teacherSite/addQuiz.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        cid = request.args.get('cid',type = int)
        msg = request.args.get('msg', type= str)
        imgs = session['image_ids']
        pg = (len(imgs) // 9 ) + 1
        random.shuffle(imgs)
        if request.method == "POST":
            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()

                quiz_name = str(request.form['quiz_name']).strip()
                cid = str(request.form['course_id'])
                img_key = str(request.form["optionsRadios"])
                startDate = str(request.form["startDate"])
                endDate = str(request.form["endDate"])
                print("startDate :",startDate, " endDate: ",endDate)
                flag , duration  = test.validDate( startDate , endDate )
                if ( flag ):
                    cursor.execute("INSERT INTO QUIZ (TEACHER_ID, COURSE_ID, QUIZ_NAME , IMG_ID , QUIZ_STARTDATE , QUIZ_ENDDATE ) VALUES (?, ?, ?, ?, ?, ?)",
                                ( session['role_id'], int(cid), quiz_name , img_key , startDate , endDate ))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    msg = "QUIZ : " +quiz_name + " Quiz Duration :" + str(duration) + " Sucessfully Created !"

                    # msg = "QUIZ : " +quiz_name + " img_key " + img_key + " cid " + cid + "Duration " + str(duration)

                else:
                    msg = duration         

            except Exception as e:
                msg = "Some Error : " + str(e) 
            cid = None
            return render_template(page[0] , cid = cid , imgs = imgs , msg1 = msg , pg = pg )

        else :
            # img_ids = test.readAllBlobData()
            if(msg == None):
                msg = "Every Quiz has an Image Key assinged to it by selecting one from existing images or Upload one image in adjecent form. "
            # print( session['image_ids'] , random.shuffle(session['image_ids']) , "random.shuffle(session['image_ids'])")
            
            return render_template(page[0], cid = cid , imgs = imgs , msg1 = msg , pg= pg)

def DeleteQuiz():
    page = check_user("/teacherSite/allCourses.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        qid = request.args.get('qid',type = int)        
        try:
            print('qid===', qid)
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()   

            course_details = cursor.execute(" SELECT course_id , course_name from COURSE WHERE course_id in (SELECT course_id from QUIZ WHERE quiz_id = ? ) " , ( qid , )).fetchone()
            url = '/teacher/Course?id=' + str(course_details[0]) + '&name=' + course_details[1]
            
            cursor.execute("DELETE FROM QUIZ WHERE quiz_id = ? ", ( qid , ))
            conn.commit()
            conn.execute("PRAGMA foreign_keys = OFF")
            cursor.close()
            conn.close()
            return redirect(url)
        except Exception as e:
            msg = "Some Error : " + str(e) 
            print("errr", msg)
            return redirect('/teacher/AllCourse')

@breadcrumb('All Quizes')
def AllQuizes():
    page = check_user("/teacherSite/course.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        # cid = request.args.get('cid',type = int)
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()

            quizes = cursor.execute("SELECT QUIZ_ID , QUIZ_NAME , QUIZ_MARKS , QUIZ_STARTDATE , QUIZ_ENDDATE from QUIZ WHERE TEACHER_ID = ? " , ( session['role_id'] , )).fetchall()
            cursor.close()
            conn.close()

        except Exception as e:
                msg = "Some Error : " + str(e) 
        return render_template(page[0] , quizes = quizes )

@breadcrumb('Quiz Questions')
def QuizQuestions():
    page = check_user("/teacherSite/quiz.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        id = request.args.get('id',type = int)
        name = request.args.get('name', type= str)
        msg = request.args.get('msg1', type= str)

        imgs = session['image_ids']
        pg = (len(imgs) // 9 ) + 1
        random.shuffle(imgs)
        # quiz = [id , name]
        try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                quiz_details = cursor.execute("SELECT  * from QUIZ WHERE QUIZ_ID = ? AND TEACHER_ID = ? " , ( id , session['role_id'] , )).fetchone()
                questions = cursor.execute("SELECT * from QUESTION WHERE QUIZ_ID = ? AND COURSE_ID = ? ", (id , quiz_details[2] ,)).fetchall()
                # quiz_details = cursor.execute("SELECT  QUIZ_NAME , QUIZ_MARKS , QUIZ_STARTDATE , QUIZ_ENDDATE from QUIZ WHERE QUIZ_ID = ? AND COURSE_ID = ? AND TEACHER_ID = ? " , ( id , cid , tid , )).fetchall()
                cursor.close()
                conn.close()
                # msg += str(quiz_details)

        except Exception as e:
            msg = "Some Error quiz: " + str(e) 
        return render_template(page[0] , quiz = quiz_details , imgs = imgs , msg1 = msg , pg= pg , questions = questions)

def EditQuiz():
    page = check_user("/teacherSite/quiz.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        id = request.args.get('id',type = int)
        name = request.args.get('name', type= str)
        if request.method == "POST":

            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()

                quiz_name = str(request.form['quiz_name']).strip()                
                img_key = str(request.form["optionsRadios"])               
                    
                startDate = str(request.form["startDate"])
                endDate = str(request.form["endDate"])

                print("startDate :",startDate, " endDate: ",endDate)
                flag , duration  = test.validDate( startDate , endDate )
                if ( flag ):
                    cursor.execute("UPDATE QUIZ SET QUIZ_NAME = ? , IMG_ID = ? , QUIZ_STARTDATE = ? , QUIZ_ENDDATE = ?  WHERE QUIZ_ID = ? ",
                                ( quiz_name , img_key , startDate , endDate , id ))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    msg = "QUIZ : " +quiz_name + " Quiz Duration :" + str(duration) + " Sucessfully Edited !"

                else:
                    msg = duration

            except Exception as e:
                msg = "Some Error Edit: " + str(e) 
            
            url = '/teacher/quiz?id='+str(id)+'&name='+quiz_name + '&msg1='+msg 
            return redirect(url) #render_template(page[0] , quiz = quiz)
        
        else:
            return redirect('/teacher/AllQuiz')

def AddQuestion():
    page = check_user("/teacherSite/quiz.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        qid = request.args.get('qid',type = int)
        cid = request.args.get('cid',type = int)
        name = request.args.get('name', type= str)

        if request.method == "POST":

            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                # conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
              
                ques_type = str(request.form["ques_type"])             
                marks = str(request.form["marks"])
                neg_marks = str(request.form["neg_marks"])
                ques_text = str(request.form["question_text"]).strip() 

                print("-------" , ques_text , '----', ques_type ,'----' , marks , neg_marks )
                
                cursor.execute("INSERT INTO QUESTION ( COURSE_ID , QUIZ_ID , QUESTION_TYPE , QUESTION_TEXT , QUESTION_MARKS , QUESTION_NEG_MARKS ) VALUES (?,?,?,?,?,?)",
                            ( cid , qid , ques_type , ques_text , marks , neg_marks ))
                conn.commit()

                sum_marks = cursor.execute("select sum(question_marks) from Question where quiz_id = ?", (qid , )).fetchone()[0]
                cursor.execute("UPDATE QUIZ SET quiz_marks = ? WHERE QUIZ_ID = ?", ( sum_marks , qid ))
                conn.commit() 
                # conn.execute("PRAGMA foreign_keys = OFF")
                cursor.close()
                conn.close()
                # msg = "qid "+ str(qid) + " cid " + str(cid) +" ques_text : " +ques_text + " Quiz ques_type :" + ques_type +  marks + neg_marks +
                msg = " Sucessfully Added !"

            except Exception as e:
                msg = "Some Error Adding: " + str(e) 
            
            url = '/teacher/quiz?id='+str(qid)+'&name='+ name + '&msg1='+msg 
            return redirect(url) #render_template(page[0] , quiz = quiz)
        
        else:
            return redirect('/teacher/AllQuiz')

@breadcrumb('Edit Question')
def EditQuestion():
    page = check_user("/teacherSite/question.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        id = request.args.get('id',type = int)
        qid = request.args.get('qid',type = int)
        cid = request.args.get('cid',type = int)
        name = request.args.get('name', type= str)
        msg = request.args.get('msg1', type= str)

        if request.method == "POST":

            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
              
                prev_options = cursor.execute("SELECT OPTION from OPTIONS WHERE QUESTION_ID = ?", (id , )).fetchall()
                conn.commit()
                prev_ans = cursor.execute("SELECT ANSWER , OPTION_ID from ANSWERS WHERE QUESTION_ID = ?", (id , )).fetchall()
                conn.commit()

                prev_options = [i[0] for i in prev_options]
                print('prev_options' , prev_options)
                prev_ans = [i[0] for i in prev_ans]
                print('prev_ans' , prev_ans)
                prev_ans_oid = [i[1] for i in prev_ans]
                print('prev_ans_oid' , prev_ans_oid)

                ques_type = str(request.form["ques_type"])             
                marks = str(request.form["marks"])
                neg_marks = str(request.form["neg_marks"])
                ques_text = str(request.form["question_text"]).strip() 
                msg = 'Question Updated '
                Flag = False

                print("-------" , ques_text , '----', ques_type ,'----' , marks , neg_marks )
                if (ques_type == 'MCQ'):
                    option = request.form.getlist('opti[]') 
                    answer = request.form.getlist('Rdopti[]')      
                    if( len(option) >= 2 ) :                              
                        for opt in option:
                            msg += opt
                            if opt not in prev_options:
                                cursor.execute("INSERT INTO OPTIONS ( QUESTION_ID , OPTION ) VALUES (?,?)", ( id , opt ))
                                conn.commit()
                            print(opt)
                        for opt in prev_options:
                            if opt not in option:
                                cursor.execute(" DELETE FROM OPTIONS where OPTION = ? And QUESTION_ID = ?", ( opt, id ))
                                conn.commit()
                        Flag = True
                        print('ans', answer)
                        print('options', option)
                        for ans in answer:
                            if ans not in prev_ans:
                                op_id = cursor.execute("SELECT OPTION_ID from OPTIONS WHERE QUESTION_ID = ? And OPTION = ? ", (id , ans )).fetchone()
                                conn.commit()
                                print('op_id====0' , op_id)
                                cursor.execute("INSERT INTO ANSWERS ( QUESTION_ID , OPTION_ID , ANSWER ) VALUES (?,? , ?)", ( id , op_id[0] , ans ))
                                conn.commit()
                        for ans in prev_ans:
                            if ans not in answer:
                                op_id = cursor.execute("SELECT OPTION_ID from OPTIONS WHERE QUESTION_ID = ? And OPTION = ? ", (id , ans )).fetchone()
                                conn.commit()
                                print('op_id====0' , op_id)
                                cursor.execute("DELETE FROM ANSWERS where QUESTION_ID = ? AND OPTION_ID = ?", ( id , op_id[0] ))
                                conn.commit()

                        url = '/teacher/quiz?id='+str(qid)+'&msg1='+msg 
                    
                    else:                        
                        msg = "MCQ type question must have at least 2 options."           
                        url = '/teacher/EditQuestion?id='+str(id)+'&cid='+str(cid)+'&qid='+str(qid)+'&name='+str(qid)+ '&msg1='+msg 
                    print('ans', answer)
                    print('options', option)
                elif (ques_type == 'MSQ'):
                    option = request.form.getlist('opti[]') 
                    answer = request.form.getlist('Rdopti[]') 
                    if( len(option) >= 2 and len(answer) >= 1 ) :
                        for opt in option:
                            msg += opt
                            if opt not in prev_options:
                                cursor.execute("INSERT INTO OPTIONS ( QUESTION_ID , OPTION ) VALUES (?,?)", ( id , opt ))
                                conn.commit()
                            print(opt)
                        for opt in prev_options:
                            if opt not in option:
                                cursor.execute(" DELETE FROM OPTIONS where OPTION = ? And QUESTION_ID = ?", ( opt, id ))
                                conn.commit()
                        Flag = True

                        for ans in answer:
                            if ans not in prev_ans:
                                op_id = cursor.execute("SELECT OPTION_ID from OPTIONS WHERE QUESTION_ID = ? And OPTION = ? ", (id , ans )).fetchone()
                                conn.commit()
                                print('op_id====0' , op_id)
                                cursor.execute("INSERT INTO ANSWERS ( QUESTION_ID , OPTION_ID , ANSWER ) VALUES (?,? , ?)", ( id , op_id[0] , ans ))
                                conn.commit()
                        for ans in prev_ans:
                            if ans not in answer:
                                op_id = cursor.execute("SELECT OPTION_ID from OPTIONS WHERE QUESTION_ID = ? And OPTION = ? ", (id , ans )).fetchone()
                                conn.commit()
                                print('op_id====0' , op_id)
                                cursor.execute("DELETE FROM ANSWERS where QUESTION_ID = ? AND OPTION_ID = ?", ( id , op_id[0] ))
                                conn.commit()

                        url = '/teacher/quiz?id='+str(qid)+'&msg1='+msg 
                    else:
                        msg = "MSQ type question must have at least 2 options. And Also don't forget to select answers."           
                        url = '/teacher/EditQuestion?id='+str(id)+'&cid='+str(cid)+'&qid='+str(qid)+'&name='+str(qid)+ '&msg1='+msg 
                    print('ans', ans)
                    print('options', option)
                elif (ques_type == 'SA'):
                    ans = str(request.form["short_ans_txt"]).strip()                    
                    if ans :
                        msg = ans
                        if len(prev_ans) == 0 :                                    
                            cursor.execute("INSERT INTO ANSWERS ( QUESTION_ID , ANSWER ) VALUES (?,? )", ( id , ans ))
                            conn.commit()    
                        else :
                            cursor.execute("UPDATE  ANSWERS SET ANSWER = ? where QUESTION_ID = ? ", ( ans , id ))
                            conn.commit()                     
                        print('ans', ans)
                        Flag = True
                        url = '/teacher/quiz?id='+str(qid)+'&msg1='+msg 
                    else:
                        msg = "Short Answer can't be empty."           
                        url = '/teacher/EditQuestion?id='+str(id)+'&cid='+str(cid)+'&qid='+str(qid)+'&name='+str(qid)+ '&msg1='+msg 
                    # print('ans', ans)
                elif (ques_type == 'MF'):
                    option = request.form.getlist('opti[]') 
                    # ans = str(request.form["short_ans_txt"]).strip()  
                    msg = msg +  '|'.join(option)  
                    print('option MF ----------=====' , option)                                   
                    option = [ '|'.join(option[i:i + 2]) for i in range(0, len(option), 2)]
                    if( len(option) >= 2 ) :                              
                        for opt in option:
                            # msg += opt
                            print(opt)
                            # opt = ' | '.join(opt)
                            print(opt)
                            if opt not in prev_options:
                                cursor.execute("INSERT INTO OPTIONS ( QUESTION_ID , OPTION ) VALUES (?,?)", ( id , opt ))
                                conn.commit()
                            
                        for opt in prev_options:
                            if opt not in option:
                                cursor.execute(" DELETE FROM OPTIONS where OPTION = ? And QUESTION_ID = ?", ( opt, id ))
                                conn.commit()
                        Flag = True
                        url = '/teacher/quiz?id='+str(qid)+'&msg1='+msg 
                    else:                        
                        msg = "MF type question must have at least 2 Pairs."           
                        url = '/teacher/EditQuestion?id='+str(id)+'&cid='+str(cid)+'&qid='+str(qid)+'&name='+str(qid)+ '&msg1='+msg 
                    # print('ans', ans)
                    print('options', option)
                elif (ques_type == 'LA'):                   
                    Flag = True
                    url = '/teacher/quiz?id='+str(qid)+'&msg1='+msg                     
                elif (ques_type == 'FB'):
                    option = request.form.getlist('opti[]') 
                     
                    # ans = str(request.form["short_ans_txt"]).strip()  
                    # msg = '|'.join(option)  
                    # print('option MF ----------=====' , option)           
                    # gp =[ int(option[i]) for i in range(0, len(option), 2) ]    
                    # print('gp======',gp)  
                    # no_blanks = int(request.form["no_blanks"])   
                    
                    option = [ '|'.join(option[i:i + 2]) for i in range(0, len(option), 2)]
                    if( len(option) >= 2 ) :                              
                        for opt in option:
                            # msg += opt
                            # print(opt)
                            # opt = ' | '.join(opt)
                            # print(opt)
                            if opt not in prev_options:
                                print(opt)
                                cursor.execute("INSERT INTO OPTIONS ( QUESTION_ID , OPTION ) VALUES (?,?)", ( id , opt ))
                                conn.commit()
                            
                        for opt in prev_options:
                            if opt not in option:
                                print(opt)
                                cursor.execute(" DELETE FROM OPTIONS where OPTION = ? And QUESTION_ID = ?", ( opt, id ))
                                conn.commit()
                        Flag = True
                        url = '/teacher/quiz?id='+str(qid)+'&msg1='+msg 
                    else:                        
                        msg = "MF type question must have at least 2 Pairs."           
                        url = '/teacher/EditQuestion?id='+str(id)+'&cid='+str(cid)+'&qid='+str(qid)+'&name='+str(qid)+ '&msg1='+msg 
                    # print('ans', ans)
                    print('options', option)    
                    

                if ( Flag ):
                    cursor.execute("UPDATE QUESTION SET QUESTION_TEXT = ?, QUESTION_MARKS = ?, QUESTION_NEG_MARKS = ? WHERE QUESTION_ID = ? AND QUIZ_ID = ?",
                            ( ques_text , marks , neg_marks , id , qid ))
                    conn.commit()    
                    sum_marks = cursor.execute("select sum(question_marks) from Question where quiz_id = ?", (qid , )).fetchone()[0]
                    cursor.execute("UPDATE QUIZ SET quiz_marks = ? WHERE QUIZ_ID = ?", ( sum_marks , qid ))
                    conn.commit() 
                # cursor.execute("INSERT INTO QUESTION ( COURSE_ID , QUIZ_ID , QUESTION_TYPE , QUESTION_TEXT , QUESTION_MARKS , QUESTION_NEG_MARKS ) VALUES (?,?,?,?,?,?)",
                #             ( cid , qid , ques_type , ques_text , marks , neg_marks ))
                # conn.commit()
                cursor.close()
                conn.close()
                # msg = "qid "+ str(qid) + " cid " + str(cid) +" ques_text : " +ques_text + " Quiz ques_type :" + ques_type +  marks + neg_marks +" Sucessfully Added !"
                # msg = 'Successfully Updated'

            except Exception as e:
                msg = "Some Error Adding: " + str(e)             
                url = '/teacher/EditQuestion?id='+str(id)+'&cid='+str(cid)+'&qid='+str(qid)+'&name='+str(qid)+ '&msg1='+msg 
            # url = '/teacher/quiz?id='+str(qid)+'&name='+ name + '&msg1='+msg 
            return redirect(url) #render_template(page[0] , quiz = quiz)
        
        else:
            try:
                
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()             
               
                question = cursor.execute("SELECT * from QUESTION WHERE QUESTION_ID = ?", (id , )).fetchone()
                
                # options = list(enumerate(options,1))
                options = cursor.execute("SELECT QUESTION_ID , OPTION from OPTIONS WHERE QUESTION_ID = ?", (id , )).fetchall()
                conn.commit()

                answer = cursor.execute("SELECT ANSWER from ANSWERS WHERE QUESTION_ID = ?", (id , )).fetchall()
                conn.commit()
                answer =  [i[0] for i in answer]

                cursor.close()
                conn.close()
                if( (question[3] == 'MF') or (question[3] == 'FB') ):  
                    mof_opt = []                  
                    for opt in options:
                        print('opt====' , opt[1])
                        mof_opt.append((opt[0] ,  opt[1].split('|') ))
                        # mof_opt.append((opt[0] , opt[1],  opt[2].split('|') ))
                        
                    options = mof_opt
                # options = [(1, ['ABC','123']), (1, ['XYZ','242526'])]
                print('options' , options)
                print('answer' , answer)
                # msg = question.join(',')
                return render_template(page[0] , question = question , options = options , answer = answer, msg1 = msg )

            except Exception as e:
                msg = "Some Error: " + str(e) 
            
            # url = '/teacher/quiz?id='+str(qid)+'&name='+ name + '&msg1='+msg 
                return render_template(page[0] , msg1 = msg ) # return redirect(url)

def DeleteQuestion():
    page = check_user("/teacherSite/allCourses.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        qid = request.args.get('qid',type = int)   
        questid = request.args.get('questid',type = int)
        
        try:
            print('qid===', qid , 'questid===', questid)
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()   

            cursor.execute("DELETE FROM Question WHERE question_id = ? ", ( questid , ))
            conn.commit()

            sum_marks = cursor.execute("select sum(question_marks) from Question where quiz_id = ?", (qid , )).fetchone()[0]
            cursor.execute("UPDATE QUIZ SET quiz_marks = ? WHERE QUIZ_ID = ?", ( sum_marks , qid ))
            conn.commit() 

            conn.execute("PRAGMA foreign_keys = OFF")
            cursor.close()
            conn.close()
            msg = 'Successfully Deleted'
            url = '/teacher/quiz?id=' + str(qid) + '&msg1=' + msg
            return redirect(url)
        except Exception as e:
            msg = "Some Error : " + str(e) 
            print("errr", msg)
            url = '/teacher/quiz?id=' + str(qid) + '&msg1=' + msg
            return redirect(url)

def EnrolledQuiz():
    page = check_user("/teacherSite/results.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        try :
            quiz_details = request.args.get('qz',type = str)
            quiz_details = [ int(i) if i.strip().isdigit() else i.strip("' '") for i in quiz_details[1:-2].split(',')]
            print('quiz_details' , quiz_details)

            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()   

            enrolled_students = cursor.execute("select r.student_id , s.student_name , r.score  from (select  q.student_id , sum(q.question_score) as score from Questions_Result q where q.student_id in ( select e.student_id from Enrollment_Quiz e where e.quiz_id = ? ) and q.quiz_id = ? group by q.student_id ) r join Student s where s.student_id = r.student_id", ( quiz_details[0] , quiz_details[0] )).fetchall()
            
            cursor.close()
            conn.close()
            enrolled_students = pd.DataFrame( enrolled_students ,  columns=['Student_ID' , 'Student_Name' , 'Score'] )
            
            if request.method == 'POST':
                resp = make_response(enrolled_students.to_csv())
                resp.headers["Content-Disposition"] = "attachment; filename="+quiz_details[3]+"_scores.csv"
                resp.headers["Content-Type"] = "text/csv"
                return resp
            else:
                return render_template(page[0] , quiz = quiz_details , enrolled_students = enrolled_students )

        except Exception as e:
            print('Error==================================' , str(e))
            return render_template(page[0] ,  msg1 = str(e) )

def StudentResult():
    page = check_user("/teacherSite/StudentResult.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        # if request.method == 'POST':
        try :
            quiz_details = request.args.get('qz',type = str)
            quiz_details = [ int(i) if i.strip().isdigit() else i.strip("' '") for i in quiz_details[1:-2].split(',')]
 
            sid = request.args.get('sid', type = int)
            score = request.args.get('scr', type = int)
            sname = request.args.get('sname', type = str)
            
            
            msg = quiz_details

            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            # quiz_details = cursor.execute("select * from Question q , Options o where q.question_id = o.question_id and  q.quiz_id = ? " , ( quiz[0] , )).fetchall()
            questions = cursor.execute("select * from Question where quiz_id = ? " , ( quiz_details[0] , )).fetchall()
            options = cursor.execute(" select * from Options where question_id in ( select question_id from Question where quiz_id = ? ) " , ( quiz_details[0] , )).fetchall()
            cor_answers = cursor.execute(" select * from Answers where question_id in ( select question_id from Question where quiz_id = ? )  " , ( quiz_details[0] , )).fetchall()
            stud_answers =  cursor.execute(" Select qr.student_answer_id , qr.question_id , qr.question_score , qr.Ans_datetime , sa.Answer from Questions_Result qr , Student_Answer sa where qr.student_answer_id = sa.student_answer_id and qr.quiz_id = ? and qr.student_id = ?  " , ( quiz_details[0] , sid  )).fetchall()
            cursor.close()
            conn.close()
            cols = ['question_id' , 'course_id' , 'quiz_id' , 'question_type' , 'question_text' , 'question_marks' , 'question_neg_marks' ]
            cols2 = [ 'option_id' , 'question_id' , 'option' ]
            cols3 = ['question_id' , 'option_id' , 'answer']
            cols4 = ['student_answer_id' , 'question_id' , 'question_score' , 'Ans_datetime' , 'Answer']

            questions = pd.DataFrame( questions , columns= cols , index=None )
            options = pd.DataFrame( options , columns= cols2 , index=None )
            cor_answers = pd.DataFrame( cor_answers , columns= cols3 , index=None )
            stud_answers = pd.DataFrame( stud_answers , columns= cols4 , index=None )


            return render_template(page[0] , quiz = quiz_details , questions = questions , options = options , cor_answers = cor_answers , stud_answers= stud_answers , score = score , sname = sname ,msg1 = msg )

        except Exception as e:
            print('Error==================================' , str(e))
            return render_template(page[0] ,  msg1 = str(e) )

def pdfquiz():
    page = check_user("/teacherSite/quizpdf.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        # if request.method == 'POST':
        # try :
            quiz_details = request.args.get('qz',type = str)
            quiz_details = [ int(i) if i.strip().isdigit() else i.strip("' '") for i in quiz_details[1:-2].split(',')]
 
            # sid = request.args.get('sid', type = int)
            # score = request.args.get('scr', type = int)
            # sname = request.args.get('sname', type = str)
            
            
            msg = quiz_details

            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            # quiz_details = cursor.execute("select * from Question q , Options o where q.question_id = o.question_id and  q.quiz_id = ? " , ( quiz[0] , )).fetchall()
            questions = cursor.execute("select * from Question where quiz_id = ? " , ( quiz_details[0] , )).fetchall()
            options = cursor.execute(" select * from Options where question_id in ( select question_id from Question where quiz_id = ? ) " , ( quiz_details[0] , )).fetchall()
            cor_answers = cursor.execute(" select * from Answers where question_id in ( select question_id from Question where quiz_id = ? )  " , ( quiz_details[0] , )).fetchall()
            # stud_answers =  cursor.execute(" Select qr.student_answer_id , qr.question_id , qr.question_score , qr.Ans_datetime , sa.Answer from Questions_Result qr , Student_Answer sa where qr.student_answer_id = sa.student_answer_id and qr.quiz_id = ? and qr.student_id = ?  " , ( quiz_details[0] , sid  )).fetchall()
            cursor.close()
            conn.close()
            cols = ['question_id' , 'course_id' , 'quiz_id' , 'question_type' , 'question_text' , 'question_marks' , 'question_neg_marks' ]
            cols2 = [ 'option_id' , 'question_id' , 'option' ]
            cols3 = ['question_id' , 'option_id' , 'answer']
            # cols4 = ['student_answer_id' , 'question_id' , 'question_score' , 'Ans_datetime' , 'Answer']

            questions = pd.DataFrame( questions , columns= cols , index=None )
            options = pd.DataFrame( options , columns= cols2 , index=None )
            cor_answers = pd.DataFrame( cor_answers , columns= cols3 , index=None )
            # stud_answers = pd.DataFrame( stud_answers , columns= cols4 , index=None )


            rendered =  render_template(page[0] , quiz = quiz_details , questions = questions , options = options , cor_answers = cor_answers ,msg1 = msg )
            pdf = pdfkit.from_string(rendered , False)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] =  'inline: filename='+quiz_details[3]+'.pdf'
            return response

        # except Exception as e:
        #     print('Error==================================' , str(e))
        #     return render_template('/teacherSite/quiz.html' ,  msg1 = str(e) )


# def excelQuizScore():
#     return excel.make_response_from_array([[1, 2], [3, 4]], "csv")