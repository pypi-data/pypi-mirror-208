import pandas as pd
import hashlib
import os
directory = os.getcwd()
parent = os.path.dirname(directory).replace('\\','/')

class Firebase_Learn:
    def __init__(self):
        pass

    def getID(data, slData):
        studentID = data["Full Admin Number"]
        sanitisedID = studentID.str[3:8]
        data["Admin Number"] = sanitisedID

        slLogins = slData['ID'].dropna().to_list()

        return data, slLogins

    def dataEncryption(data, slLogins):
        '''
        SHA224 Encryption for Student data
        '''
        strings = []
        for index, row in data.iterrows():
            b = row["Admin Number"].encode('utf-8')
            hashed = hashlib.sha224(b).hexdigest()
            strings.append(hashed)
        '''
        SHA224 Encryption for SL data
        '''
        slData = list(filter(None, slLogins))
        for slLogin in slData:
            
            b = slLogin.encode('utf-8')
            hashed = hashlib.sha224(b).hexdigest()
            strings.append(hashed)

        return strings

    def sanitiseName(data):
        studentNames = data["Name"].str.split().dropna()
        greetingNames = []
        sanitizedName = ''
        
        for n in studentNames:
            if (len(n) == 1):
                #sanitizedName = data['Name'].tolist()
                sanitizedName = n[0]
            if (len(n) == 2):
                sanitizedName = n[0] + '.' + n[1][0]
            elif (len(n) == 3):
                sanitizedName = n[0] + '.' + n[1][0] + '.' + n[2][0]
            elif (len(n) == 4):
                sanitizedName = n[0] + '.' + n[1][0] + '.' + n[2][0] + '.' + n[3][0]
            elif (len(n) == 5):
                sanitizedName = n[0] + '.' + n[1][0] + '.' + n[2][0] + '.' + n[3][0] + '.' + n[4][0]
            elif (len(n) > 5):
                sanitizedName = n[0] + '.' + n[1][0] + '.' + n[2][0] + '.' + n[3][0] + '.' + n[4][0] + '.' + n[5][0]

            greetingNames.append(sanitizedName)
        greetingNames.append('Subject Leader')

        return greetingNames

    def createDBData(strings, names):
        dbData = pd.DataFrame()
        dbData['NAME'] = names
        dbData['ID'] = strings

        # dbData.to_excel("./Chatbot/Data/DBData.xlsx", index=False)
        # dbData.to_json("./Chatbot/Data/DBData.json")
        # dbData.to_json("./Chatbot/Data/FirebaseData.json")
        dbData.to_json("./Tutor/For Deployment/Learn & Explore/FirebaseData.json")





