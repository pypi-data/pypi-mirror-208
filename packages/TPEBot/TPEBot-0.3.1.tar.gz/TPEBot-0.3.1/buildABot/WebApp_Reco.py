import pandas as pd
import os
import TPEBot

class WebApp_Reco:
    def __init__(self) -> None:
        pass

    def getFiles():
        package_dir = os.path.abspath(TPEBot.__path__[0])
        index_dir = (package_dir.replace('\\','/')) + '/Data/WebApp/Recommended/index_template.html'
        reset_dir = (package_dir.replace('\\','/')) + '/Data/WebApp/Recommended/reset_template.js'

        index_temp = open(index_dir, "r")
        reset_temp = open(reset_dir, "r")

        index_file = open('./Chatbot/WebApp/public/index.html', 'w')
        reset_file = open('./Chatbot/WebApp/public/js/reset.js', 'w')

        index_data = index_temp.read()
        reset_data = reset_temp.read()

        return index_temp, reset_temp, index_file, reset_file, index_data, reset_data
    
    def customisationHTML(df, index_file, index_data, reset_data):
        # Replace the target string
        subject = df['Subject'][0]
        persona = df['Persona'][0]
        project_id = df['GCP Project ID'][0]

        index_data = index_data.replace("SUBJECTNAME", subject)
        index_data = index_data.replace("BOTNAME", persona)

        reset_data = reset_data.replace("PROJECTID", project_id)

        # Write the file out again
        index_file.write(index_data)

    def getFirebaseConfig():
        firebase_config = open("./Tutor/firebase_config.txt")
        config = firebase_config.read()

        return config
    
    def resetJS(reset_data, reset_file, config):
        reset_data = reset_data.replace("firebaseconfighere", config)
        reset_file.write(reset_data)

    def closeFiles(index_temp, reset_temp, index_file, reset_file):
        index_temp.close()
        reset_temp.close()
        index_file.close()
        reset_file.close()


    
