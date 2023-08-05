import pandas as pd
import hashlib
import os

class Firebase_Reco:
    def __init__(self):
        pass

    def sanitizeID(df):
        # Admin No
        adminNumber = df["Full Admin Number"]#Collect Admin No. into variable
        adminID = adminNumber.str[3:8] #Get last 4 digits of Admin no.
        df["Admin Number"] = adminID

        strings = []
        for index, row in df.iterrows():
            b = row["Admin Number"].encode('utf-8')
            hashed = hashlib.sha224(b).hexdigest()
            strings.append(hashed)
        return strings
    
    def createGreetingNames(df):
        # Name
        student_name = df["Name"]
        name = student_name.str.split() #Split full name by whitespace into fragments
        name.dropna()
        shortname = []
        for n in name:
            if(len(n) == 1):
                sanitized_name = n[0]
            elif(len(n) == 2):
                sanitized_name = n[0] + '.' + n[1][0]
            elif(len(n) == 3):
                sanitized_name = n[0] + '.' + n[1][0] + '.' + n[2][0]
            elif(len(n) == 4):
                sanitized_name = n[0] + '.' + n[1][0] + '.' + n[2][0] + '.' + n[3][0]
            elif(len(n) == 5):
                sanitized_name = n[0] + '.' + n[1][0] + '.' + n[2][0] + '.' + n[3][0] + '.' + n[4][0]
            elif(len(n) > 5):
                sanitized_name = n[0] + '.' + n[1][0] + '.' + n[2][0] + '.' + n[3][0] + '.' + n[4][0] + '.' + n[5][0]

            shortname.append(sanitized_name)
        return shortname
    
    def combineResult(df, strings, shortname):
        # -- Combine Results + Name + HASHED ID -- #
        df["ID"] = strings
        df["NAME"] = shortname #Create Column to store sanitized name

        df.drop('Class', axis='columns', inplace=True)
        df.drop('Student', axis='columns', inplace=True)
    
    def createDBData(data):
        data.to_json("./Tutor/For Deployment/Recommended/FirebaseData.json")
