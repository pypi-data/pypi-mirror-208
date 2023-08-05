import json
import os
import pandas as pd
import numpy as np

directory = os.getcwd()
parent = os.path.dirname(directory).replace('\\','/')

class Entities:
    def __init__(self):
        import pandas as pd

    def getEntityTemplate():  # Entity template
        return {
            "value": "",
            "synonyms": [
            ]
        }

    def appendJSON(file, d):  # Store entity template into json file
        with open(file, 'a') as outfile:
            outfile.write(json.dumps(d))
            outfile.close()

    def commaJSON(file):  # Add comma between objects
        with open(file, 'r+') as f:
            old = f.read()
            f.seek(0)
            f.write(old.replace('}{', '},{'))
            f.close

    def structureJSON(file, file1):  # Add bracket for a complete structure
        with open(file, 'r+') as f:
            old = f.read()
            with open(file1, 'w') as r:
                tmps = '[' + str(old) + ']'
                json_string = json.loads(tmps)
                json.dump(json_string, r, indent=4)
                f.close

    def cleanStudentID(df):
        
        cleanID = []
        for index, rows in df.iterrows():
            rows["Full Admin Number"].replace("@student.tp.edu.sg", "") # to clean and get student id (incase sl retrive from student email)
            cleanID.append(rows["Full Admin Number"][3:8])

        '''
        To filter and add in sanitised student id + exporting to respective location
        '''
        #num = df["Full Admin Number"]
        #cleanID = num.str[3:8]

        df["ID"] = cleanID
        dfAnalytics = df[['Class', 'Name', 'ID']]
        dfAnalytics = dfAnalytics.rename(columns = {'ID':'Admin Number'})
        dfAnalytics.to_excel('./Chatbot/Dashboard/Data/students-data.xlsx', index=False)
        dfAnalytics.to_excel('./Chatbot/Data/students-data.xlsx', index=False)

        df.drop('Class', axis='columns', inplace=True) # Filter data
        df.drop('Name', axis='columns', inplace=True) # Filter data

        return df

    def createEntity(df):
        '''
        Retrieve entity value & synonyms
        Convert entities to JSON
        '''

        for index, rows in df.iterrows():
            synonyms = [] # Create empty list to store all synonyms for entity
            entity = Entities.getEntityTemplate()
            synonyms.append(rows["ID"])  # Synonyms Value of Entity
            synonyms.append(rows["ID"].lower())

            entity["value"] = rows["ID"] #Reference Value of Entity
            entity["synonyms"] = synonyms

            Entities.appendJSON("./Chatbot/LoginID.json", entity)
            Entities.commaJSON("./Chatbot/LoginID.json")
            Entities.structureJSON("./Chatbot/LoginID.json", "./Chatbot/entities/LoginID_entries_en.json")
            
        # -- Dummy Login ID -- #
        df = pd.read_excel("./Tutor/SL Inputs.xlsx", dtype=str)
        df.fillna(value='', inplace=True)

        # Read in the file
        loginID = df['ID'].replace('', np.nan).ffill().iloc[-1]
        dummy = []
        dummy.append(loginID)
        dummy.append(loginID.lower())

        entity = Entities.getEntityTemplate()
        entity["value"] = loginID #Reference Value of Entity
        entity["synonyms"] = dummy

        Entities.appendJSON("./Chatbot/LoginID.json", entity)
        Entities.commaJSON("./Chatbot/LoginID.json")
        Entities.structureJSON("./Chatbot/LoginID.json", "./Chatbot/entities/LoginID_entries_en.json")
        
        os.remove("./Chatbot/LoginID.json")
