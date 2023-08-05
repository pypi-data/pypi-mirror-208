import os
import pandas as pd
import pkgutil
import TPEBot
import sys

directory = os.getcwd()
parent = os.path.dirname(directory).replace('\\','/')
print(parent)

class Webhook_Learn:
    def __init__(self):
        pass

    def readFiles(keyFile):
        '''
        Read csv and template files
        :param slFile
        :return:
        '''
        accKeyFile = open(keyFile)

        package_dir = os.path.abspath(TPEBot.__path__[0])
        src_dir = (package_dir.replace('\\','/')) + '/Data/Webhook/Learn/index_template.js'
        template = open(src_dir).read()
        #template = pkgutil.get_data("buildABot.Data.Webhook", 'Learn/index_template.js').decode("utf-8") 

        return accKeyFile, template

    def getInfo(slData, accKeyFile, template):
        '''
        Get necessary data from csv files (service account key, firebase url, email)
        '''
        accKey = accKeyFile.read()
        dbURL = slData['Firebase URL'][0]
        slEmail = slData['Email'][0]

        '''
        Replace keywords with extracted values
        '''
        template = template.replace("SERVICEACCOUNTKEYHERE", accKey)
        template = template.replace("DBURLHERE", dbURL)
        template = template.replace("TUTOREMAILHERE", slEmail)

        return template

    def createFulfillment(template):
        '''
        Write updated fulfillment code into destinated files and close files
        '''
        tutorFile = open("./Tutor/For Deployment/Learn & Explore/index.js", 'w', encoding="utf-8")
        tutorFile.write(template)
        tutorFile.close()