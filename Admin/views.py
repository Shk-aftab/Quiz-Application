from flask import Flask, request, render_template, flash,  redirect, url_for, send_from_directory, send_file, session , json
import os
import sqlite3
import random
import pandas as pd

def check_user(page):
    if session.get("email"):
        if session.get("user_role") == 'A':
            return [page]
        else:
            return [page , "You Don't have these previlages." ]
    else:
        return ['login.html']

def AdminHome():
    page = check_user("/adminSite/adminHome.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()

            n_teacher =   cursor.execute(" select count(teacher_id) from Teacher ").fetchone()[0]         
            n_student =  cursor.execute(" select count(student_id) from Student  ").fetchone()[0] 
            n_quize = cursor.execute(" select count( quiz_id ) from Quiz ").fetchone()[0] 
            n_course = cursor.execute(" select count( course_id ) from Course ").fetchone()[0] 
                        
            cursor.close()
            conn.close()
        except Exception as e:
            msg = "Some Error : " + str(e) 
            print("errr", msg)
        return render_template(page[0] ,  n_course = n_course , n_quize = n_quize , n_student = n_student , n_teacher = n_teacher )  


def AdminTeachers():
    page = check_user("/adminSite/adminTeachers.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:

        msg = request.args.get('msg',type = str)
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            
            
            teachers = cursor.execute("SELECT * FROM TEACHER").fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            teachers = pd.DataFrame( teachers ,  columns=['Teacher_ID' , 'User_id' , 'Teacher_Name'] )
            
            print("teachers \n" , teachers)           

        except Exception as e:
            msg = "Some Error : " + str(e) 

        return render_template(page[0] , teachers = teachers , msg1 = msg )

def AdminStudents():
    page = check_user("/adminSite/adminStudents.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        msg = request.args.get('msg',type = str)
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            
            
            students = cursor.execute("SELECT * FROM STUDENT").fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            students = pd.DataFrame( students ,  columns=['Student_ID' , 'User_id' , 'Student_Name'] )
            
            print("students \n" , students)
            
           

        except Exception as e:
            msg = "Some Error : " + str(e) 

        return render_template(page[0] , students = students , msg1 = msg)

def AdminUsers():
    page = check_user("/adminSite/adminUsers.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        msg = request.args.get('msg',type = str)
        try:
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()
            
            
            users = cursor.execute("SELECT * FROM USER").fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            users = pd.DataFrame( users ,  columns=[ 'User_id' , 'User_Email' ,'Password' , 'Phone_No' , 'Role' , 'Active'] )
            
            print("users \n" , users)
            
           

        except Exception as e:
            msg = "Some Error : " + str(e) 

        return render_template(page[0] , users = users , msg1 = msg)

def AdminUpdateUser():
    page = check_user("/adminSite/adminUsers.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        msg = ''
        if request.method == "POST":       
            try:               

                user_id = str(request.form['user_id'])
                user_email = str(request.form['user_email'])
                user_password = str(request.form["user_password"])              
                phone_no = str(request.form['phone_no'])
                user_role = str(request.form['user_role'])
                status = str(request.form['status'])

                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                
                cursor.execute("UPDATE USER SET user_email = ? ,  password = ? , phone_no = ?, active = ? WHERE USER_ID = ? ",
                                ( user_email , user_password , int(phone_no) ,int(status) , int(user_id)))
                conn.commit()
                
                cursor.close()
                conn.close()

                msg += 'User Data Updated Successfully'
                print('=====================User_id',user_id , 'User_Email',user_email , 'Password', user_password , 'Phone_No', phone_no ,'Role', user_role , 'Status' , status )

               
            except Exception as e:
                msg = "Some Error : " + str(e) 
                print(msg)

        url = '/admin/users?msg=' + msg
        return redirect(url)
        

def AdminUpdateStudent():
    page = check_user("/adminSite/adminStudents.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        msg = ''
        if request.method == "POST":  
                 
            try:     
                user_id = str(request.form['user_id'])
                Student_ID = str(request.form['Student_ID'])
                Student_Name = str(request.form["Student_Name"])              
                         
                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                
                cursor.execute("UPDATE STUDENT SET STUDENT_NAME = ? WHERE USER_ID = ?",
                                ( Student_Name , int(user_id)))
                conn.commit()
                
                cursor.close()
                conn.close()
                
                msg += 'Student Data Updated Successfully'
                # print('User_id',user_id , 'User_Email',user_email , 'Password', user_password , 'Phone_No', phone_no ,'Role', user_role )
                print('=====================User_id',user_id , 'Student_ID' ,Student_ID , 'Student_Name' ,Student_Name)
               
            except Exception as e:
                msg = "Some Error : " + str(e) 
                print(msg)
        url = '/admin/students?msg=' + msg
        return redirect(url)

def AdminUpdateTeacher():
    page = check_user("/adminSite/adminTeachers.html")
    if len(page) > 1:
        return render_template(page[0] , msg = page[1])
    else:
        msg = ''
        if request.method == "POST":       
            try:               
                
                user_id = str(request.form['user_id'])
                Teacher_ID = str(request.form['Teacher_ID'])
                Teacher_Name = str(request.form["Teacher_Name"])  

                conn = sqlite3.connect("DataBase/quizAppDataBase.db")
                cursor = conn.cursor()
                
                cursor.execute("UPDATE TEACHER SET TEACHER_NAME = ? WHERE USER_ID = ?",
                                ( Teacher_Name , int(user_id)))
                conn.commit()
                
                cursor.close()
                conn.close()            
               
                msg += 'Teacher Data Updated Successfully'
                # print('User_id',user_id , 'User_Email',user_email , 'Password', user_password , 'Phone_No', phone_no ,'Role', user_role )
                print('=====================User_id',user_id , 'Teacher_ID' ,Teacher_ID , 'Teacher_Name' ,Teacher_Name)
               
            except Exception as e:
                msg = "Some Error : " + str(e) 
                print(msg)
        url = '/admin/teachers?msg=' + msg
        return redirect(url)
        