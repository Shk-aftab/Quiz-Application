import sqlite3
# import os 
from datetime import datetime 
import random


def convertToBLOB( filename ):
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")

def insertImage( filename ):
    try:        
        print("Connected to SQLite")      
        img = convertToBLOB(filename)
        if ( CompairBlobData(img) == False ):
            conn = sqlite3.connect("DataBase/quizAppDataBase.db")
            cursor = conn.cursor()

            sqlite_insert_blob_query = """ INSERT INTO IMAGES
                                  (IMAGE) VALUES (?)"""
            cursor.execute(sqlite_insert_blob_query, ((img),))
            conn.commit()
            cursor.close()
            conn.close()
            msg = "Image Uploaded Successfully, Now image key can be selected below."
            # return msg
        else:
            msg = "Image Already exists"
            # return msg
        
        return msg
        # print(img)
        # Convert data into tuple format
        # data_tuple = ()
        # cursor.execute(sqlite_insert_blob_query, ((img),))
        # conn.commit()
        # print("Image and file inserted successfully as a BLOB into a table")
        
        # return img

    except sqlite3.Error as error:
        msg = "Failed to insert blob data into sqlite table" + str(error)
        return msg


def readBlobData(id):
    try:
        conn = sqlite3.connect("DataBase/quizAppDataBase.db")
        cursor = conn.cursor()
        print("Connected to SQLite")

        sql_fetch_blob_query = """SELECT * from IMAGES where IMAGE_ID = ?"""
        cursor.execute(sql_fetch_blob_query, (id,))
        record = cursor.fetchall()
        for row in record:
            print("Id = ", row[0], "FILE = ", row[1])
            # name = row[1]
            # photo = row[2]
            # resumeFile = row[3]

            print("Storing employee image and resume on disk \n")
            photoPath = "photos/" + str(id) + ".jpg"
            # resumePath = "E:\pynative\Python\photos\db_data\\" + name + "_resume.txt"
            writeTofile(row[1], photoPath)
            # writeTofile(resumeFile, resumePath)

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("sqlite connection is closed")

def readAllBlobData():
    try:
        conn = sqlite3.connect("DataBase/quizAppDataBase.db")
        cursor = conn.cursor()
        # print("Connected to SQLite")

        sql_fetch_blob_query = """SELECT * from IMAGES """
        cursor.execute(sql_fetch_blob_query)
        record = cursor.fetchall()
        img_ids = [i[0] for i in record ]
        for row in record:
            # print("Id = ", row[0])
            # print("Storing employee image and resume on disk \n")
            photoPath = "static/photos/" + str(row[0]) + ".jpg"
            writeTofile(row[1], photoPath)
        cursor.close()
        return img_ids
    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("sqlite connection is closed")


def CompairBlobData( data ):
    try:
        conn = sqlite3.connect("DataBase/quizAppDataBase.db")
        cursor = conn.cursor()
        print("Connected to SQLite")

        sql_fetch_blob_query = """SELECT * from IMAGES where IMAGE = ?"""
        cursor.execute(sql_fetch_blob_query, (data,))
        record = cursor.fetchall()
        cursor.close()
        for row in record:
            
            # name = row[1]
            # photo = row[2]
            # resumeFile = row[3]
            if data == row[1]:
                print("Id = ", row[0])
                print("found.....")
                return True

            # print("Storing employee image and resume on disk \n")
            # photoPath = "photos/" + str(id) + ".jpg"
            # # resumePath = "E:\pynative\Python\photos\db_data\\" + name + "_resume.txt"
            # writeTofile(row[1], photoPath)
            # # writeTofile(resumeFile, resumePath)

        return False

    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("sqlite connection is closed")

# X =  insertImage('images/4.jpg')
# CompairBlobData(X)
# readBlobData(2)
# lmn = readAllBlobData()
# print(lmn)

def validDate( startDate , endDate ):

    st_d = datetime.strptime( startDate ,  '%Y-%m-%dT%H:%M' )
    en_d = datetime.strptime( endDate ,  '%Y-%m-%dT%H:%M' )
    # print("StartDate : ", st_d , type(st_d))
    # print("EndDate : ", en_d , type(en_d) )
    duration  = en_d - st_d
    now  = datetime.now()
    print("Now : ", now , type(now) )
    # print(  duration , type(duration))
    # print(  duration.days  , duration.seconds)

    if( st_d > now ):
        if( en_d > st_d ):
            print("valid")
            return [ True , duration ]
    else:
        print("Not Valid")
        return [False , 'In Valid timings']


# @app.template_filter('shuffle')
def filter_shuffle(seq):
    try:
        result = list(seq)
        random.shuffle(result)
        return result
    except:
        return seq