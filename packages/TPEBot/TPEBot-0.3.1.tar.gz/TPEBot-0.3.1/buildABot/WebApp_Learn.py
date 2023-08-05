import os
directory = os.getcwd()
parent = os.path.dirname(directory).replace('\\','/')
import pkgutil

class WebApp_Learn:
    def __init__(self):
        import pandas as pd

    def readFiles():
        template = pkgutil.get_data("buildABot.Data", 'WebApp/Learn/index_template.html').decode("utf-8") 
        # tempFile = open('./Data/index_template.html', "r")
        # data = tempFile.read()
        return str(template)
    
    def getInfo(df, data):
        subject = df['Subject'][0]
        persona = df['Persona'][0]

        data = data.replace("SUBJECTNAME", subject)
        data = data.replace("BOTNAME", persona)

        return data

    def createHTML(data):
        htmlFile = open('./Chatbot/WebApp/public/index.html', 'w')
        htmlFile.write(data)
        htmlFile.close()