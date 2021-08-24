from flask import Flask, json, request, render_template, flash,  redirect, url_for, send_from_directory, send_file, session ,jsonify
import os
import sqlite3
import random
from datetime import datetime
import test
import pandas as pd


def check_user(page):
    if session.get("email"):
        if session.get("user_role") == 'S':
            return [page]
        else:
            return [page , "You Don't have these previlages." ]
    else:
        return ['login.html']


def StudentHome():
    page = check_user("/studentSite/studentHome.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()

            n_course = len(  session['courses']  )            

            n_quize = len( session['quizes']) # cursor.execute(" SELECT count(QUIZ_ID) from QUIZ WHERE TEACHER_ID = ? " , ( session['role_id'] , )).fetchone()[0]
            n_teacher = cursor.execute(" select count(distinct(c.teacher_id)) from Course c where c.course_id in (select e.course_id from Enrollment_Course e where e.student_id = ? )  " , ( session['role_id'] , )).fetchone()[0]
            
            cursor.close()
            conn.close()
        except Exception as e:
            msg = "Some Error : " + str(e) 
            print("errr", msg)
        return render_template(page[0] ,  n_course = n_course , n_quize = n_quize , n_teacher = n_teacher )  


def AllTeachers():
    page = check_user("/studentSite/all.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        conn = sqlite3.connect("DataBase/quizAppDataBase.db")
        cursor = conn.cursor()
        all_teachers = cursor.execute("SELECT TEACHER_ID , TEACHER_NAME from TEACHER ").fetchall()
        cursor.close()
        conn.close()
        return render_template(page[0] , all_teachers = all_teachers )

def Teacher():
    page = check_user("/studentSite/teacher.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        conn = sqlite3.connect("DataBase/quizAppDataBase.db")
        cursor = conn.cursor()
        id = request.args.get('id',type = int)
        name = request.args.get('name', type = str)
        courses = cursor.execute("SELECT COURSE_ID , COURSE_NAME , TEACHER_ID from COURSE WHERE TEACHER_ID = ?" , ( id,)).fetchall()
        cursor.close()
        conn.close()
        return render_template(page[0] , teacher = [id , name] , courses = courses )

def AllCourse():
    page = check_user("/studentSite/all.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        # conn = sqlite3.connect("DataBase/quizAppDataBase.db")
        # cursor = conn.cursor()
        # all_teachers = cursor.execute("SELECT TEACHER_ID , TEACHER_NAME from TEACHER ").fetchall()
        # cursor.close()
        # conn.close()
        return render_template(page[0] , courses = session['courses'] )

def Course():
    page = check_user("/studentSite/course.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        id = request.args.get('id',type = int)
        name = request.args.get('name', type = str)
        tid = request.args.get('tid' , type = int)
        if (id , name , tid) in session['courses']:

            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()

                quizes = cursor.execute("SELECT QUIZ_ID , QUIZ_NAME , QUIZ_MARKS , QUIZ_STARTDATE , QUIZ_ENDDATE from QUIZ WHERE COURSE_ID = ? AND TEACHER_ID = ? " , ( id , tid , )).fetchall()
                cursor.close()
                conn.close()

            except Exception as e:
                msg = "Some Error : " + str(e) 
            # return render_template(page[0] , course = [ cid, name ] , quizes = quizes)
            return render_template(page[0] , course = [id , name , tid] , flag = True , quizes = quizes )

        else:
            msg1 = "Enroll to the course to view all the quizs. For Public Courses the Key is '1234'."
            return render_template(page[0] , course = [id , name , tid] , flag = False , msg1 = msg1 )
        
def Enroll_Course():
    page = check_user("/studentSite/course.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        id = request.args.get('id',type = int)
        name = request.args.get('name', type = str)
        tid = request.args.get('tid' , type = int)
        if request.method == 'POST' :          

            key = str(request.form['enroll_key']).strip()
            url = '/student/course?id=' + str(id) + '&name=' + name + '&tid=' + str(tid)
            print('Enrolled : ' , key , url)
            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                en_key = cursor.execute("SELECT ENROLLMENT_KEY from COURSE WHERE TEACHER_ID = ? AND COURSE_ID = ? " , ( tid , id )).fetchone()[0]
                if( key == en_key ):
                    cursor.execute("INSERT INTO ENROLLMENT_COURSE (STUDENT_ID , COURSE_ID) VALUES (?, ?)",
                        ( session['role_id'] , id ))
                    conn.commit()
                    session['courses'] = cursor.execute("SELECT COURSE_ID , COURSE_NAME , TEACHER_ID from COURSE WHERE COURSE_ID IN ( SELECT COURSE_ID from ENROLLMENT_COURSE WHERE STUDENT_ID = ? )" , ( session['role_id'] , )).fetchall()
                    msg1 = 'Success'
                    print(msg1 , 'msg1')
                    cursor.close()
                    conn.close()
                    return redirect(url)
                else:
                    msg1 = 'Enter proper Key'
                    print(msg1 , 'msg1')
                    return render_template(page[0] , course = [id , name , tid]  , flag = False , msg1 = msg1 )
                # return redirect(url)
            except Exception as e:
                msg1 = 'Some Error : ' + str(e)
                return render_template(page[0] ,course = [id , name , tid]  , flag = False , msg1 = msg1 )

        else:
            msg1 = "For Public Courses the Key is '1234'."
            return render_template(page[0] , course = [id , name , tid]  , flag = False , msg1 = msg1)

def AllQuiz():
    page = check_user("/studentSite/all.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        # conn = sqlite3.connect("DataBase/quizAppDataBase.db")
        # cursor = conn.cursor()
        # all_teachers = cursor.execute("SELECT TEACHER_ID , TEACHER_NAME from TEACHER ").fetchall()
        # cursor.close()
        # conn.close()
        return render_template(page[0] , quizes = session['quizes'] )

def Quiz():
    page = check_user("/studentSite/quiz.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        id = request.args.get('id',type = int)
        name = request.args.get('name', type = str)
        tid = request.args.get('tid' , type = int)
        cid = request.args.get('cid' , type = int)
        imgs = session['image_ids']
        pg = (len(imgs) // 9 ) + 1
        random.shuffle(imgs)

        if (id , name , tid , cid) in session['quizes']:

            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                quiz_details = cursor.execute("SELECT  * from QUIZ WHERE QUIZ_ID = ? AND COURSE_ID = ? AND TEACHER_ID = ? " , ( id , cid , tid , )).fetchone()
                
                abc= test.validDate( quiz_details[7] , quiz_details[8] )
                print('XYZ======' , abc)
                msg = ''#quiz_details
                if  not test.validDate( quiz_details[7] , quiz_details[8] )[0]:
                    print('Results======')
                    result = cursor.execute("select sum(question_score) from Questions_Result where student_id = ? and quiz_id = ? " , ( session['role_id'] , id )).fetchone()[0]
                    cursor.close()
                    conn.close()
                    return render_template(page[0] , quiz = quiz_details , flag = True , msg1 = msg , result = result )              
                cursor.close()
                conn.close()
                print("msg=======" , msg)
            except Exception as e:
                msg = "Some Error : " + str(e) 

            return render_template(page[0] , quiz = quiz_details , flag = True , msg1 = msg )

        else:
            msg1 = "Enroll to the course to view all the quizs. For Public Courses the Key is '1234'."
        return render_template(page[0] , quiz = [id , name , tid , cid] , flag = False , imgs = imgs , pg = pg )


def Enroll_Quiz():
    page = check_user("/studentSite/quiz.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        id = request.args.get('id',type = int)
        name = request.args.get('name', type = str)
        tid = request.args.get('tid' , type = int)
        cid = request.args.get('cid' , type = int)
        imgs = session['image_ids']
        pg = (len(imgs) // 9 ) + 1
        random.shuffle(imgs)
        if request.method == 'POST' : 

            img_key = str(request.form["optionsRadios"])
            url = '/student/quiz?id=' + str(id) + '&name=' + name + '&cid=' + str(cid) +'&tid=' + str(tid)
            print('Enrolled : ' , img_key , url)
            
            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                en_key = cursor.execute("SELECT IMG_ID from QUIZ WHERE TEACHER_ID = ? AND COURSE_ID = ? AND QUIZ_ID = ? " , ( tid , cid , id )).fetchone()[0]
                print( "en_key :" , en_key)
                if( int(img_key) == en_key ):
                    cursor.execute("INSERT INTO ENROLLMENT_QUIZ (STUDENT_ID , QUIZ_ID) VALUES (?, ?)",
                        ( session['role_id'] , id ))
                    conn.commit()
                    session['quizes'] = cursor.execute("SELECT QUIZ_ID , QUIZ_NAME , TEACHER_ID , COURSE_ID from QUIZ WHERE QUIZ_ID IN ( SELECT QUIZ_ID from ENROLLMENT_QUIZ WHERE STUDENT_ID = ? )" , ( session['role_id'] , )).fetchall()

                    # session['courses'] = cursor.execute("SELECT COURSE_ID , COURSE_NAME , TEACHER_ID from COURSE WHERE COURSE_ID IN ( SELECT COURSE_ID from ENROLLMENT WHERE STUDENT_ID = ? )" , ( session['role_id'] , )).fetchall()
                    msg1 = 'Success'
                    print(msg1 , 'msg1')
                    cursor.close()
                    conn.close()
                    return redirect(url)
                else:
                    msg1 = 'Enter proper Key'
                    print(msg1 , 'msg1')
                    return render_template(page[0] , quiz = [id , name , tid , cid]  , flag = False , msg1 = msg1 , imgs = imgs ,  pg = pg  )
                # return redirect(url)
            except Exception as e:
                msg1 = 'Some Error : ' + str(e)
                return render_template(page[0] ,quiz = [id , name , tid , cid]  , flag = False , msg1 = msg1 , imgs = imgs , pg = pg )

            
        else:
            msg1 = "For Public Courses the Key is '1234'."
            return render_template(page[0] , quiz = [id , name , tid , cid]  , flag = False , msg1 = msg1 , imgs = imgs , pg = pg  )

def Start_Quiz():
    page = check_user("/studentSite/showtime.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        if request.method == 'GET':
            # id = request.args.get('id',type = int)
            # name = request.args.get('name', type = str)
            # tid = request.args.get('tid' , type = int)
            # cid = request.args.get('cid' , type = int)
            quiz = request.args.get('qz')
            quiz =[ int(i) if i.strip().isdigit() else i.strip("' '") for i in quiz[1:-2].split(',')]
            print('type(quiz)=====' , quiz , type(quiz))
            try:
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                # quiz_details = cursor.execute("select * from Question q , Options o where q.question_id = o.question_id and  q.quiz_id = ? " , ( quiz[0] , )).fetchall()
                questions = cursor.execute("select * from Question where quiz_id = ? " , ( quiz[0] , )).fetchall()
                options = cursor.execute(" select * from Options where question_id in ( select question_id from Question where quiz_id = ? ) " , ( quiz[0] , )).fetchall()
                
                cursor.close()
                conn.close()
                cols = ['question_id' , 'course_id' , 'quiz_id' , 'question_type' , 'question_text' , 'question_marks' , 'question_neg_marks' ]
                cols2 = [ 'option_id' , 'question_id' , 'option' ]

                questions = pd.DataFrame( questions , columns= cols , index=None )
                options = pd.DataFrame( options , columns= cols2 , index=None )

                # quiz_details = pd.DataFrame( quiz_details , columns= cols , index=None )
                # quiz_details = quiz_details.groupby(['question_id1', 'course_id' , 'quiz_id' , 'question_type' , 'question_text' , 'question_marks' , 'question_neg_marks' ])
                print('==== Questions====\n' ,questions)
                for q in range(questions.shape[0]):
                    print('q',questions.loc[q].values)
                    print('q',questions.loc[q].to_dict())
                    print('option :' ,options[options['question_id'] == questions.loc[q].to_dict()['question_id']])

                print('==== Options====\n' ,options)
               
                
                return render_template(page[0] , quiz = quiz , questions = questions , options = options )
            except Exception as e:
                print('Error')
                msg = 'Error' + str(e)
                return render_template(page[0] , msg = msg )


def Answer_Question():
    if request.method == 'POST' :
        try :
            quest_details = request.args.get('qd',type = str)
            quest_details = json.loads(quest_details)            
            formdata = request.get_json()
            # print('id======================================' , quest_details , type(quest_details) )
            # print('questiontype' , quest_details['question_type'] )
            # print('Data======================================' , formdata , len(formdata) )
            if formdata:     
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()

                db_ans = cursor.execute("select * from Questions_Result where student_id = ? and  quiz_id = ? and question_id = ?" , (  session['role_id'] , quest_details['quiz_id'] , quest_details['question_id'] )).fetchone()
                
                if db_ans:
                    flag = True
                else:
                    flag = False             


                if quest_details['question_type'] == 'MCQ':
                    # print('+++++++++++db_ans' , db_ans , flag )
                    # print('questiontype' , quest_details['question_type'] )
                    # print('FormData//////////' , formdata[0]['value'] )
                    
                   
                    correct_ans = cursor.execute("select option_id from Answers where question_id = ?" , ( quest_details['question_id'] , )).fetchone()
                    # print('correct_ans//////////' , correct_ans[0] )

                    if int(formdata[0]['value']) == correct_ans[0]:
                        score =  quest_details['question_marks']
                    else:
                        score =  quest_details['question_neg_marks']
                    
                    if flag:
                        cursor.execute("UPDATE Questions_Result SET question_score = ? , Ans_datetime = ?  WHERE student_answer_id = ?",
                            ( int(score), str( datetime.now()) , db_ans[0]))
                        conn.commit()
                        cursor.execute("UPDATE Student_Answer SET Answer = ? WHERE student_answer_id = ?",
                            ( int(formdata[0]['value']) , db_ans[0]))
                        conn.commit()
                    else:
                        cursor.execute("INSERT INTO Questions_Result (student_id, course_id, quiz_id , question_id , question_type , question_score , Ans_datetime) VALUES (?, ?, ?, ?, ?, ? ,?)",
                            (  session['role_id'] , quest_details['course_id'] , quest_details['quiz_id'] , quest_details['question_id'] , quest_details['question_type'] , int(score) , str(datetime.now()) ))
                        conn.commit()
                        stud_ans_id = cursor.execute("select student_answer_id from Questions_Result where student_id = ? and  quiz_id = ? and question_id = ?" , (  session['role_id'] , quest_details['quiz_id'] , quest_details['question_id'] )).fetchone()[0]
                        cursor.execute("INSERT INTO Student_Answer (student_answer_id,  Answer ) VALUES (?, ?)",
                            ( stud_ans_id , int(formdata[0]['value']) ))
                        conn.commit()
                       
                   
                elif quest_details['question_type'] == 'MSQ':     
                    # print('+++++++++++db_ans' , db_ans , flag )
                    # print('questiontype' , quest_details['question_type'] )
                    # for i in range( len(formdata) ):
                    #     print('FormData//////////' , formdata[i]['value'] , type( formdata[i]['value']) )
                    formdata = [ int(i['value']) for i in formdata ]
                    correct_ans =[ i[0] for i in cursor.execute("select option_id from Answers where question_id = ?" , ( quest_details['question_id'] , )).fetchall() ]
                    # print('correct_ans//////////' , correct_ans , formdata )

                    formdata.sort()
                    correct_ans.sort()
                    if( formdata == correct_ans ):
                        score =  quest_details['question_marks']
                    else:
                        score =  quest_details['question_neg_marks']
                    # print('correct_ans//////////' , correct_ans , formdata , score )

                    if flag:
                        cursor.execute("UPDATE Questions_Result SET question_score = ? , Ans_datetime = ?  WHERE student_answer_id = ?",
                            ( int(score), str( datetime.now()) , db_ans[0]))
                        conn.commit()
                        cursor.execute("Delete from Student_Answer WHERE student_answer_id = ?", ( db_ans[0] , ))
                        conn.commit()
                        for i in range( len(formdata)):
                            cursor.execute("INSERT INTO Student_Answer (student_answer_id,  Answer ) VALUES (?, ?)",
                                ( db_ans[0] , formdata[i] ))
                            conn.commit()
                        
                    else:
                        cursor.execute("INSERT INTO Questions_Result (student_id, course_id, quiz_id , question_id , question_type , question_score , Ans_datetime) VALUES (?, ?, ?, ?, ?, ? ,?)",
                            (  session['role_id'] , quest_details['course_id'] , quest_details['quiz_id'] , quest_details['question_id'] , quest_details['question_type'] , int(score) , str(datetime.now()) ))
                        conn.commit()
                        stud_ans_id = cursor.execute("select student_answer_id from Questions_Result where student_id = ? and  quiz_id = ? and question_id = ?" , (  session['role_id'] , quest_details['quiz_id'] , quest_details['question_id'] )).fetchone()[0]
                        for i in range( len(formdata)):
                            cursor.execute("INSERT INTO Student_Answer (student_answer_id,  Answer ) VALUES (?, ?)",
                                ( stud_ans_id , formdata[i] ))
                            conn.commit()

                elif quest_details['question_type'] == 'SA':
                    if formdata[0]['value'] :
                        print('formdata' , formdata[0]['value'] )
                    else:
                        return jsonify({'status': False,})

                elif quest_details['question_type'] == 'MF':
                    # print('+++++++++++db_ans' , db_ans , flag )
                    # print('questiontype' , quest_details['question_type'] )
                    formdata = [ i['name']+'|'+i['value']  for i in formdata ]
                    correct_ans =[ i[0] for i in cursor.execute("select option from Options where question_id = ?" , ( quest_details['question_id'] , )).fetchall() ]
                    if( formdata == correct_ans ):
                        score =  quest_details['question_marks']
                    elif ( formdata == ['A1|', 'Z1|', 'Q1|'] ):
                        score = 0
                    else:
                        score =  quest_details['question_neg_marks']
                    # print('correct_ans//////////' , correct_ans , formdata , score)
                    if flag:
                        cursor.execute("UPDATE Questions_Result SET question_score = ? , Ans_datetime = ?  WHERE student_answer_id = ?",
                            ( int(score), str( datetime.now()) , db_ans[0]))
                        conn.commit()
                        cursor.execute("Delete from Student_Answer WHERE student_answer_id = ?", ( db_ans[0] , ))
                        conn.commit()
                        for i in range( len(formdata)):
                            cursor.execute("INSERT INTO Student_Answer (student_answer_id,  Answer ) VALUES (?, ?)",
                                ( db_ans[0] , formdata[i] ))
                            conn.commit()
                        
                    else:
                        cursor.execute("INSERT INTO Questions_Result (student_id, course_id, quiz_id , question_id , question_type , question_score , Ans_datetime) VALUES (?, ?, ?, ?, ?, ? ,?)",
                            (  session['role_id'] , quest_details['course_id'] , quest_details['quiz_id'] , quest_details['question_id'] , quest_details['question_type'] , int(score) , str(datetime.now()) ))
                        conn.commit()
                        stud_ans_id = cursor.execute("select student_answer_id from Questions_Result where student_id = ? and  quiz_id = ? and question_id = ?" , (  session['role_id'] , quest_details['quiz_id'] , quest_details['question_id'] )).fetchone()[0]
                        for i in range( len(formdata)):
                            cursor.execute("INSERT INTO Student_Answer (student_answer_id,  Answer ) VALUES (?, ?)",
                                ( stud_ans_id , formdata[i] ))
                            conn.commit()

                elif quest_details['question_type'] == 'FB':      
                    # print('questiontype' , quest_details['question_type'] )
                    formdata = [ i['name']+'|'+i['value']  for i in formdata ]
                    correct_ans =[ i[0] for i in cursor.execute("select option from Options where question_id = ?" , ( quest_details['question_id'] , )).fetchall() ]
                    score = 0 
                    for i in formdata:
                        if i in correct_ans:
                            score = score + quest_details['question_marks'] / len(formdata)

                    if( score  ):
                        score =  int(score)                    
                    else:
                        score =  quest_details['question_neg_marks']

                    # print('correct_ans//////////' , correct_ans , formdata , score)
                    if flag:
                        cursor.execute("UPDATE Questions_Result SET question_score = ? , Ans_datetime = ?  WHERE student_answer_id = ?",
                            ( int(score), str( datetime.now()) , db_ans[0]))
                        conn.commit()
                        cursor.execute("Delete from Student_Answer WHERE student_answer_id = ?", ( db_ans[0] , ))
                        conn.commit()
                        for i in range( len(formdata)):
                            cursor.execute("INSERT INTO Student_Answer (student_answer_id,  Answer ) VALUES (?, ?)",
                                ( db_ans[0] , formdata[i] ))
                            conn.commit()
                        
                    else:
                        cursor.execute("INSERT INTO Questions_Result (student_id, course_id, quiz_id , question_id , question_type , question_score , Ans_datetime) VALUES (?, ?, ?, ?, ?, ? ,?)",
                            (  session['role_id'] , quest_details['course_id'] , quest_details['quiz_id'] , quest_details['question_id'] , quest_details['question_type'] , int(score) , str(datetime.now()) ))
                        conn.commit()
                        stud_ans_id = cursor.execute("select student_answer_id from Questions_Result where student_id = ? and  quiz_id = ? and question_id = ?" , (  session['role_id'] , quest_details['quiz_id'] , quest_details['question_id'] )).fetchone()[0]
                        for i in range( len(formdata)):
                            cursor.execute("INSERT INTO Student_Answer (student_answer_id,  Answer ) VALUES (?, ?)",
                                ( stud_ans_id , formdata[i] ))
                            conn.commit()

                cursor.close()
                conn.close()
                return jsonify({'status': True, })
            else :
                return jsonify({'status': False,})

            
           
        except Exception as e:
            print('Error==================================' , str(e))
            return jsonify({'status': False,})



def View_Result():
    page = check_user("/studentSite/result.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        # if request.method == 'POST':
        try :
            quiz_details = request.args.get('qz',type = str)
            quiz_details = [ int(i) if i.strip().isdigit() else i.strip("' '") for i in quiz_details[1:-2].split(',')]

            score = request.args.get('scr',type = int)
 
            print('quiz_details////////////////' , quiz_details)
            msg = quiz_details

            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            # quiz_details = cursor.execute("select * from Question q , Options o where q.question_id = o.question_id and  q.quiz_id = ? " , ( quiz[0] , )).fetchall()
            questions = cursor.execute("select * from Question where quiz_id = ? " , ( quiz_details[0] , )).fetchall()
            options = cursor.execute(" select * from Options where question_id in ( select question_id from Question where quiz_id = ? ) " , ( quiz_details[0] , )).fetchall()
            cor_answers = cursor.execute(" select * from Answers where question_id in ( select question_id from Question where quiz_id = ? )  " , ( quiz_details[0] , )).fetchall()
            stud_answers =  cursor.execute(" Select qr.student_answer_id , qr.question_id , qr.question_score , qr.Ans_datetime , sa.Answer from Questions_Result qr , Student_Answer sa where qr.student_answer_id = sa.student_answer_id and qr.quiz_id = ? and qr.student_id = ?  " , ( quiz_details[0] , session['role_id'] )).fetchall()
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

            print('questions********' ,questions)
            print('options------' ,options)
            print('cor_answers++++++' ,cor_answers)
            print('stud_answers$$$$$$$$' ,stud_answers)

            return render_template(page[0] , quiz = quiz_details , questions = questions , options = options , cor_answers = cor_answers , stud_answers= stud_answers , score = score ,msg1 = msg )

        except Exception as e:
            print('Error==================================' , str(e))
            return render_template(page[0] ,  msg1 = str(e) )
