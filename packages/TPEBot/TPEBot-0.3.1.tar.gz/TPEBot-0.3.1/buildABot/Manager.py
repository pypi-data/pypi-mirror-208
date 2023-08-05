import pandas as pd
import os
import datetime
import shutil
import TPEBot
from buildABot.Paraphraser import Paraphraser
from buildABot.Intents import Intents
from buildABot.LearnMenu import LearnMenu
from buildABot.RecommendedMenu import RecommendedMenu
from buildABot.FallbackSocialTag import FallbackSocialTag
from buildABot.Password import Password
from buildABot.Worksheets import Worksheets
from buildABot.Entities import Entities
from buildABot.Webhook_Learn import Webhook_Learn
from buildABot.Webhook_Reco import Webhook_Reco
from buildABot.Firebase_Learn import Firebase_Learn
from buildABot.Firebase_Reco import Firebase_Reco
from buildABot.WebApp_Learn import WebApp_Learn
from buildABot.WebApp_Reco import WebApp_Reco
from buildABot.TelegramLogs import TelegramLogs
from buildABot.Analytics import Analytics

package_dir = os.path.abspath(TPEBot.__path__[0])
print(package_dir)

class Manager(Paraphraser, Intents, LearnMenu, RecommendedMenu, FallbackSocialTag, Password, Worksheets, Entities, Webhook_Learn, Webhook_Reco, Firebase_Learn, Firebase_Reco, WebApp_Learn, WebApp_Reco, TelegramLogs, Analytics):
    def __init__(self, qaFile, slFile, studentFile, resultFile, keyFile):
        self.qaFile = qaFile
        self.slFile = slFile
        self.studentFile = studentFile
        self.resultFile = resultFile
        self.keyFile = keyFile

    def getData(file):
        """
        Read QAfile and clean the file before using
        :param file: QA_data.xlsx, SL Inputs.xlsx
        :return: [Dataframe] Cleaned file as dataframe
        """
        # Get QAfile and read as dataframe
        df = pd.read_excel(file, dtype=str)
        df.fillna(value='', inplace=True)
        return df
    
    def createParaphrases(self):
        Paraphraser.random_state(1234)
        qaData = Manager.getData(self.qaFile)
        df, df_qn, dfString = Paraphraser.extractData(df=qaData)
        numTrainPara, paraphrases = Paraphraser.paraphrase(dfString=dfString)
        Paraphraser.createNewQAFile(numTrainPara=numTrainPara, paraphrases=paraphrases, df=df, df_qn=df_qn)
        
    def createIntents(self):    
        """
        Executing the different functions to obtain JSON files of all intents
        :return: Display message after successful excution
        """
        data = Manager.getData(self.qaFile)
        data_with_labels = Intents.getLabels(df=data)
        data_with_labels.to_excel('./Tutor/QA_Paraphrased.xlsx', index=False)  # Update
        Intents.getIntents(df=data_with_labels)

    def createLearnMenu(self):
        df = Manager.getData("./Tutor/QA_Paraphrased.xlsx")
        LearnMenu.createLearnMenu(df=df)
        LearnMenu.createMainTopicMenu3(df=df)
        LearnMenu.createMainTopicMenu2(df=df)

    def createRecoMenu(self):
        df = Manager.getData("./Chatbot/Data/qna-data.xlsx")
        rubrics = Manager.getData(self.resultFile)
        assignments, topics, numOfTopics = RecommendedMenu.getInfo(resultFile=self.resultFile, rubrics=rubrics)
        RecommendedMenu.createRecoMainMenu(assignments=assignments)
        RecommendedMenu.createRecoAssignmentMenu(assignments=assignments)
        RecommendedMenu.createRecoTopicMenu(topics=topics, numOfTopics=numOfTopics, rubrics=rubrics)
        RecommendedMenu.createRecoSubTopicMenu(df=df, rubrics=rubrics, numOfTopics=numOfTopics)

    def createSocialTag(self):
        df = Manager.getData(self.studentFile)
        FallbackSocialTag.createSocialTag(df=df)

    def createPwIntent(self):
        df = Manager.getData(self.slFile)
        Password.createPwIntent(df=df)

    def createWorksheets(self):
        df = pd.read_excel(self.slFile, sheet_name="Worksheets", dtype=str)
        #df = Manager.getData(self.slFile)
        Worksheets.createWsIntent(df=df)

    def createEntities(self):
        studentData = Manager.getData(file=self.studentFile)
        slData = Manager.getData(file=self.slFile)

        cleanedStudentData = Entities.cleanStudentID(studentData)
        Entities.createEntity(cleanedStudentData)

    def createLearnWebhook(self):
        slData = Manager.getData(file=self.slFile)
        accKeyFile, template = Webhook_Learn.readFiles(keyFile=self.keyFile)
        template = Webhook_Learn.getInfo(slData=slData, accKeyFile=accKeyFile, template=template)
        Webhook_Learn.createFulfillment(template=template)

    def createRecoWebhook(self):
        df = Manager.getData(self.resultFile)
        topics, numOfTopics = Webhook_Reco.getRubricsCriteria(df=df)

        df = Manager.getData(self.slFile)
        acckey, dbUrl, email = Webhook_Reco.getFromSLInputs(df=df, keyFile=self.keyFile)
        data, f1 = Webhook_Reco.webhookCode(acckey=acckey, dbUrl=dbUrl, email=email)
        data = Webhook_Reco.snapShotCode(data=data, numOfTopics=numOfTopics, topics=topics)
        data = Webhook_Reco.highlightVariable(data=data, numOfTopics=numOfTopics)
        data = Webhook_Reco.nullStrings(data=data, numOfTopics=numOfTopics)
        data = Webhook_Reco.highlightTopic(df=df, data=data, numOfTopics=numOfTopics)
        data = Webhook_Reco.reportCard(data=data, numOfTopics=numOfTopics, topics=topics)
        f2 = Webhook_Reco.createRecoMenu(data=data, numOfTopics=numOfTopics, topics=topics)
        Webhook_Reco.closeFiles(f1=f1, f2=f2)

    def createLearnFirebase(self):
        studentData = Manager.getData(file=self.studentFile)
        slData = Manager.getData(file=self.slFile)

        data, slLogins = Firebase_Learn.getID(data=studentData, slData=slData)
        strings = Firebase_Learn.dataEncryption(data=data, slLogins=slLogins)
        names = Firebase_Learn.sanitiseName(data=studentData)
        Firebase_Learn.createDBData(strings=strings, names=names)

    def createRecoFirebase(self):
        df = Manager.getData(self.studentFile)
        strings = Firebase_Reco.sanitizeID(df=df)
        shortname = Firebase_Reco.createGreetingNames(df=df)
        df = Manager.getData(self.resultFile)
        data = Firebase_Reco.combineResult(df=df, strings=strings, shortname=shortname)
        Firebase_Reco.createDBData(data=data)

    def createLearnWebapp(self):
        df = Manager.getData(file=self.slFile)
        template = WebApp_Learn.readFiles()
        data = WebApp_Learn.getInfo(df=df, data=template)
        WebApp_Learn.createHTML(data=data)

    def createRecoWebApp(self):
        df = Manager.getData(self.slFile)
        index_temp, reset_temp, index_file, reset_file, index_data, reset_data = WebApp_Reco.getFiles()
        WebApp_Reco.customisationHTML(df=df, index_file=index_file, index_data=index_data, reset_data=reset_data)
        config = WebApp_Reco.getFirebaseConfig
        WebApp_Reco.resetJS(reset_data=reset_data, reset_file=reset_file, config=config)
        WebApp_Reco.closeFiles(index_temp=index_temp, reset_temp=reset_temp, index_file=index_file, reset_file=reset_file)

    def createTeleLogs(self):
        teleLogs = pd.read_csv('./Chatbot/Data/Logs.csv')
        df = Manager.getData(self.studentFile)

        TelegramLogs.createTeleParticipation(teleLogs=teleLogs, df=df)

    def createDashboard(self):
        logs_raw, qna_data, students_data, dummy = Analytics.retrieveData()
        logs_main = Analytics.cleanData(logs_raw=logs_raw, dummy=dummy)
        logs_main = Analytics.match_unmatchFiles(logs_main=logs_main)
        logs_main = Analytics.saveCleanedLogs(logs_main=logs_main)
        logs_main, helpful_df = Analytics.voteFiles(logs_main=logs_main)
        logs_helpful = Analytics.durationFile(logs_main=logs_main, helpful_df=helpful_df)
        logs_helpful = Analytics.corrFile(qna_data=qna_data, logs_helpful=logs_helpful)
        Analytics.pathFile(logs_helpful=logs_helpful)


    """
    Create respective zip files for option selected by user
    """
    def createLearnRestoreZip(self):
        '''
        combine intents into one folder
        '''
        package_dir = os.path.abspath(TPEBot.__path__[0])
        src_dir = (package_dir.replace('\\','/')) + '/Data/Default - Learn'
        
        intent_dir = './Chatbot/Intents/Learn/intents'
        entity_dir = './Chatbot/entities'

        zip_name = './Tutor/For Deployment/Agent_RESTORE_LEARN'

        files = os.listdir(src_dir)

        '''
        put all intents together
        '''
        shutil.copytree(src_dir, intent_dir, dirs_exist_ok=True)

        '''
        putting all necessary files to zip for importing to dialogflow
        '''
        shutil.copytree(intent_dir, zip_name+'/intents')
        shutil.copytree(entity_dir, zip_name+'/entities')
        shutil.copyfile('./Tutor/agent.json', zip_name+'/agent.json')
        shutil.copyfile('./Tutor/package.json', zip_name+'/package.json')

        shutil.make_archive(zip_name, 'zip',zip_name)
        shutil.rmtree(zip_name) 

    def createRecoRestoreZip(self):
        '''
        combine intents into one folder
        '''
        package_dir = os.path.abspath(TPEBot.__path__[0])
        src_dir = (package_dir.replace('\\','/')) + '/Data/Default - Recommended'
        
        reco_dir = './Chatbot/Intents/Recommended/intents'
        intent_dir = './Chatbot/Intents/Learn/intents'
        entity_dir = './Chatbot/entities'

        zip_name = './Tutor/For Deployment/Agent_RESTORE_RECOMMENDED'

        files = os.listdir(src_dir)
        '''
        put all intents together
        '''
        shutil.copytree(src_dir, intent_dir, dirs_exist_ok=True)
        shutil.copytree(reco_dir, intent_dir, dirs_exist_ok=True)
        '''
        putting all necessary files to zip for importing to dialogflow
        '''
        shutil.copytree(intent_dir, zip_name+'/intents')
        shutil.copytree(entity_dir, zip_name+'/entities')
        shutil.copyfile('./Tutor/agent.json', zip_name+'/agent.json')
        shutil.copyfile('./Tutor/package.json', zip_name+'/package.json')

        shutil.make_archive(zip_name, 'zip',zip_name)
        shutil.rmtree(zip_name) 

    def createWorksheetZip(self):
        '''
        combine intents into one folder
        '''
        dir_name = './Chatbot/Intents/Worksheets/intents'
        zip_name = './Tutor/For Deployment/Agent_IMPORT_Worksheets'

        '''
        putting all necessary files to zip for importing to dialogflow
        '''
        shutil.copytree(dir_name, zip_name+'/intents')
        shutil.copyfile('./Tutor/agent.json', zip_name+'/agent.json')
        shutil.copyfile('./Tutor/package.json', zip_name+'/package.json')

        shutil.make_archive(zip_name, 'zip',zip_name)
        shutil.rmtree(zip_name) 

    def createIntentZip(self):
        '''
        combine intents into one folder
        '''
        folder_name = './Chatbot/Intents/Learn/intents'
        zip_name = './Tutor/For Deployment/Agent_IMPORT_Intents'

        '''
        putting all necessary files to zip for importing to dialogflow
        '''
        shutil.copytree(folder_name, zip_name+'/intents')
        shutil.copyfile('./Tutor/agent.json', zip_name+'/agent.json')
        shutil.copyfile('./Tutor/package.json', zip_name+'/package.json')

        shutil.make_archive(zip_name, 'zip',zip_name)
        shutil.rmtree(zip_name) 

    def createEntZip(self):
        src_dir = (package_dir.replace('\\','/')) + '/Data/Entities'
        dir_name = './Chatbot/entities'
        zip_name = './Tutor/For Deployment/Agent_IMPORT_Entities'

        '''
        putting all necessary files to zip for importing to dialogflow
        '''
        shutil.copytree(src_dir, dir_name, dirs_exist_ok=True)
        shutil.copytree(dir_name, zip_name+'/entities')
        shutil.copyfile('./Tutor/agent.json', zip_name+'/agent.json')
        shutil.copyfile('./Tutor/package.json', zip_name+'/package.json')

        shutil.make_archive(zip_name, 'zip',zip_name)
        shutil.rmtree(zip_name) 

    def createRecoZip(self):
        '''
        combine intents into one folder
        '''
        folder_name = './Chatbot/Intents/Recommended/intents'
        zip_name = './Tutor/For Deployment/Agent_IMPORT_RECOMMENDED'

        '''
        putting all necessary files to zip for importing to dialogflow
        '''
        shutil.copytree(folder_name, zip_name+'/intents')
        shutil.copyfile('./Tutor/agent.json', zip_name+'/agent.json')
        shutil.copyfile('./Tutor/package.json', zip_name+'/package.json')

        shutil.make_archive(zip_name, 'zip',zip_name)
        shutil.rmtree(zip_name) 

    """
    Respective function handler for different purpose
    """
    def createLearnChatbot(self):
        print("Execution started @ \n", datetime.datetime.now())
        Manager.createParaphrases(self)
        Manager.createIntents(self)
        Manager.createLearnMenu(self)
        Manager.createSocialTag(self)
        Manager.createWorksheets(self)
        Manager.createEntities(self)
        Manager.createLearnWebhook(self)
        print("Dialogflow files done... Next up: Firebase\n")

        Manager.createLearnFirebase(self)
        print("Firebase files done... Next up: WebApp\n")

        Manager.createLearnWebapp(self)
        print("WebApp files done... Next up: Prepare all files for deployment\n")

        Manager.createLearnRestoreZip(self)
        print("Chatbot ready for deployment!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())

    def createLearnAndRecoChatbot(self):
        print("Execution started @ \n", datetime.datetime.now())
        Manager.createParaphrases(self)
        Manager.createIntents(self)
        Manager.createLearnMenu(self)
        Manager.createRecoMenu(self)
        Manager.createSocialTag(self)
        Manager.createPwIntent(self)
        Manager.createWorksheets(self)
        Manager.createEntities(self)
        Manager.createRecoWebhook(self)
        print("Dialogflow files done... Next up: Firebase\n")

        Manager.createRecoFirebase(self)
        print("Firebase files done... Next up: WebApp\n")

        Manager.createRecoWebApp(self)
        print("WebApp files done... Next up: Prepare all files for deployment\n")

        Manager.createRecoRestoreZip(self)
        print("Chatbot ready for deployment!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())


    def updateLearnIntents(self):
        print("Execution started @ \n", datetime.datetime.now())

        # Clear files before execution
        dir = './Chatbot/Intents/Learn/intents'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        Manager.createParaphrases(self)
        Manager.createIntents(self)
        Manager.createLearnMenu(self)
        Manager.createWorksheets(self)
        print("New Intents Created...\n")

        Manager.createIntentZip(self)
        print("Chatbot ready for update!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())
    
    def updateRecoIntents(self):
        print("Execution started @ \n", datetime.datetime.now())

        # Clear files before execution
        dir = './Chatbot/Intents/Learn/intents'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        Manager.createParaphrases(self)
        Manager.createIntents(self)
        Manager.createLearnMenu(self)
        Manager.createRecoMenu(self)
        Manager.createWorksheets(self)
        print("New Intents Created...\n")

        Manager.createIntentZip(self)
        print("Chatbot ready for update!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())


    def updateLatestWorksheets(self):
        print("Execution started @ \n", datetime.datetime.now())
        Manager.createWorksheets(self)
        print("Latest Worksheets Added...\n")

        Manager.createWorksheetZip(self)
        print("Chatbot ready for update!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())

    def addNewResults(self):
        print("Execution started @ \n", datetime.datetime.now())
        # Clear files before execution
        dir = './Chatbot/Intents/Recommended/intents'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        Manager.createRecoMenu(self)
        Manager.createRecoWebhook(self)
        Manager.createRecoFirebase(self)
        Manager.createRecoWebApp(self)
        print("Latest Results Added...\n")

        Manager.createRecoZip(self)
        print("Chatbot ready for update!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())


    def updateLearnEntities(self):
        print("Execution started @ \n", datetime.datetime.now())
        Manager.createSocialTag(self)
        Manager.createEntities(self)
        Manager.createLearnFirebase(self)
        print("New Entities Created...\n")

        Manager.createEntZip(self)
        print("Chatbot ready for update!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())

    def updateRecoEntities(self):
        print("Execution started @ \n", datetime.datetime.now())
        Manager.createSocialTag(self)
        Manager.createEntities(self)
        Manager.createRecoFirebase(self)
        print("New Entities Created...\n")

        Manager.createEntZip(self)
        print("Chatbot ready for update!\n")
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())


    def createTeleLogs(self):
        print("Execution started @ \n", datetime.datetime.now())
        print("Please make sure the downloaded logs files are in the Chatbot/Telebot folder, named as 'Logs.csv'.\n")
        input("If you have done so, press enter to continue...\n")

        Manager.createTeleLogs(self)
        print("Telebot Logs created!\n")

        Manager.createDashboard(self)
        print("Dashboard Data created!\n")
        
        print("Excution done, exiting...\n")
        print("Execution Ended @ ", datetime.datetime.now())
  
    
    