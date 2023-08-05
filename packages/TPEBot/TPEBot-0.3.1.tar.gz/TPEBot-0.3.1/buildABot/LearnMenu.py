import pandas as pd
import json
import os

directory = os.getcwd()
parent = os.path.dirname(directory).replace('\\','/')

class LearnMenu():
    def getMainTemplate():
        return {
    "id": "b6b5f5c1-04fb-4745-b8e1-1aa250d684ec",
    "name": "Menu - Learn",
    "auto": True,
    "contexts": [
        "loginID"
    ],
    "responses": [
        {
        "resetContexts": False,
        "action": "",
        "affectedContexts": [
            {
            "name": "loginID",
            "lifespan": 5
            }
        ],
        "parameters": [],
        "messages": [
            {
            "type": "4", #Telegram Response
            "platform": "telegram",
            "title": "",
            "payload": {
                "telegram": {
                "reply_markup": {
                    "keyboard": [
                    [
                        {
                        "text": "", #Main Topic Name
                        "callback_data": "" #Main Topic Name
                        }
                    ]
                    ]
                },
                "text": "Pick a topic"
                }
            },
            "textToSpeech": "",
            "lang": "en",
            "condition": ""
            },
            {
            "type": "4", #Web Response
            "title": "",
            "payload": {
                "richContent": [
                [
                    {
                    "type": "chips",
                    "options": [
                        {
                        "text": "" #Main Topic Name
                        }
                    ]
                    }
                ]
                ]
            },
            "textToSpeech": "",
            "lang": "en",
            "condition": ""
            }
        ],
        "speech": []
        }
    ],
    "priority": 500000,
    "webhookUsed": False,
    "webhookForSlotFilling": False,
    "fallbackIntent": False,
    "events": [],
    "conditionalResponses": [],
    "condition": "",
    "conditionalFollowupEvents": []
    }

    def getMainTopicTemplate():
        return {
    "id": "a22ba3ca-fce6-47cf-a06d-40e48989c8c3",
    "name": "", #Main Topic Name
    "auto": True,
    "contexts": [
        "loginID"
    ],
    "responses": [
        {
        "resetContexts": False,
        "action": "",
        "affectedContexts": [
            {
            "name": "loginID",
            "lifespan": 5
            }
        ],
        "parameters": [],
        "messages": [
            {
            "type": "4",
            "platform": "telegram",
            "title": "",
            "payload": {
                "telegram": {
                "text": "Pick a topic",
                "reply_markup": {
                    "keyboard": [
                    [
                        {
                        "text": "", #Sub Topic Name
                        "callback_data": "" #Sub Topic Name
                        }
                    ]
                    ]
                }
                }
            },
            "textToSpeech": "",
            "lang": "en",
            "condition": ""
            },
            {
            "type": "4",
            "title": "",
            "payload": {
                "richContent": [
                [
                    {
                    "options": [
                        {
                        "text": "" #Sub Topic Name
                        }
                    ],
                    "type": "chips"
                    }
                ]
                ]
            },
            "textToSpeech": "",
            "lang": "en",
            "condition": ""
            },
            {
            "type": "4",
            "title": "",
            "payload": {
                "richContent": [
                [
                    {
                    "options": [
                        {
                        "image": {
                            "src": {
                            "rawUrl": "https://firebasestorage.googleapis.com/v0/b/almgtbot.appspot.com/o/home%20(1).png?alt=media&token=c8b0db13-9aeb-48ab-ad44-6134a55049e2"
                            }
                        },
                        "text": "Back to Main Menu"
                        }
                    ],
                    "type": "chips"
                    }
                ]
                ]
            },
            "textToSpeech": "",
            "lang": "en",
            "condition": ""
            }
        ],
        "speech": []
        }
    ],
    "priority": 500000,
    "webhookUsed": False,
    "webhookForSlotFilling": False,
    "fallbackIntent": False,
    "events": [],
    "conditionalResponses": [],
    "condition": "",
    "conditionalFollowupEvents": []
    }

    def getSubTopicTemplate():
        return {
            "id": "a22ba3ca-fce6-47cf-a06d-40e48989c8c3",
            "name": "", #Main Topic - Sub Topic
            "auto": True,
            "contexts": ["loginID"],
            "responses": [{
                "resetContexts": False,
                "action": "",
                "affectedContexts": [
                    {
                    "name": "loginID",
                    "lifespan": 5
                    }
                ],
                "parameters": [],
                "messages": [
                    {
                        "type": "4",
                        "platform": "telegram",
                        "title": "",
                        "payload":{
                            "telegram": {
                                "text": "Pick a topic",
                                "reply_markup": 
                                {
                                    "keyboard": [
                                        [
                                            {
                                                "text": "", #Intent Name
                                                "callback_data": "" #Intent Name
                                            }
                                        ]#insert tele resp
                                    ]
                                }
                            }
                        },
                        "textToSpeech": "",
                        "lang": "en",
                        "condition": ""
                    },
                    {
                        "type": "4",
                        "title": "",
                        "payload": {
                            "richContent": [[
                                {
                                    "options": [
                                        {
                                            "text": "" #Intent Name
                                        }
                                    ],
                                    "type": "chips"
                                }
                            ]]
                        },
                        "textToSpeech": "",
                        "lang": "en",
                        "condition": ""
                    },
                    {
                        "type": "4",
                        "title": "",
                        "payload": {
                            "richContent": [[
                                {
                                    "options": [
                                        {
                                            "text": "Back to Sub Topic", #Back to ['Sub Topic']
                                            "image": {
                                                "src": {
                                                    "rawUrl": "https://firebasestorage.googleapis.com/v0/b/almgtbot.appspot.com/o/left-arrow-curved-black-symbol.png?alt=media&token=f0225665-02e7-459f-b8e9-1c19618a7234"
                                                }
                                            }
                                        },
                                        {
                                            "text": "Back to Main Menu",
                                            "image": {
                                                "src": 
                                                {
                                                    "rawUrl": "https://firebasestorage.googleapis.com/v0/b/almgtbot.appspot.com/o/home%20(1).png?alt=media&token=c8b0db13-9aeb-48ab-ad44-6134a55049e2"
                                                }
                                            }
                                        }
                                    ],
                                    "type": "chips"
                                }
                            ]]
                        },
                        "textToSpeech": "",
                        "lang": "en",
                        "condition": ""
                    }
                ],
                "speech": []
                }],
            "priority": 500000,
            "webhookUsed": False,
            "webhookForSlotFilling": False,
            "fallbackIntent": False,
            "events": [],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": []
        }

    def getTrainingTemplate():
        return {
            "id": "e4442cbe-5335-4282-8691-890ba020b0aa",
            "data": [
                {
                    "text": "See Topics", #Phrases to call out Main Menu
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "lang": "en",
            "updated": 0
        }   

    def getChipsPayload():
        return {
                "text": ""
        }

    def getTelePayload():
        return [{
            "text": "", #Intent Name
            "callback_data": "" #Intent Name
        }]
  
    def write_file_json(QA_Data, data):
        with open(QA_Data, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=4)

    def append_file_json(jsonfile, d): #Store entity template into json file
        with open(jsonfile, 'a') as outfile:
            outfile.write(json.dumps(d))
            outfile.close()


    def createLearnMenu(df):
        """
        Import data and declare variables
        """
        #df = pd.read_excel("../../Tutor/QA_Paraphrased.xlsx", na_filter=False, dtype='str')
        data = df[['Main Label', 'Main Topic', 'Sub Label', 'Sub Topic', 'Name']]

        maxi, count = 0, 0
        listOfMainLabels = []
        payload, telePayload = [], []

        # Get Labels of Main Topics
        for index, row in data.iterrows():
            if int(row['Main Label']) > maxi:
                maxi = int(row['Main Label'])
            mainLabels = row["Main Label"]
            listOfMainLabels.append(int(mainLabels))

        '''
        Create Intent Response Payload
        '''
        for i in range(1, maxi + 1):
            chipsTemplate = LearnMenu.getChipsPayload()
            teleTemplate = LearnMenu.getTelePayload()
            
            grouping = listOfMainLabels.count(i) # count no. of intents for current main topic
            
            intentGroup = data.iloc[count:(count+1), 1:2]

            intentGroup.columns = [''] * len(intentGroup.columns)
            
            concept_strings = str(intentGroup).replace(('{}'.format(count)),'')
            concept_strings = concept_strings.replace('\n','')
            concept_strings = concept_strings.strip()

            # Put topic string into intent placeholders
            chipsTemplate["text"] = concept_strings
            teleTemplate[0]["text"] = concept_strings
            teleTemplate[0]["callback_data"] = concept_strings
            
            count += (grouping)
            payload.append(chipsTemplate)
            telePayload.append(teleTemplate)
            
            intent = LearnMenu.getMainTemplate()
            intent["responses"][0]["messages"][1]["payload"]["richContent"][0][0]["options"] = payload
            intent["responses"][0]["messages"][0]["payload"]["telegram"]["reply_markup"]["keyboard"] = telePayload

        '''
        Create Training Phrases for Intent
        '''
        trainingIntent = []
        defaultPhrases = ['See Topics', 'Learn', 'Learn Menu', 'Back to Learn Menu', "↩ Back to Learn Menu", "Learn & Explore", 'Go to Learn Menu', 'Back to Menu']

        for phrase in defaultPhrases:
        
            trainingPayload = LearnMenu.getTrainingTemplate()
            trainingPayload["data"][0]["text"] = phrase
            trainingIntent.append(trainingPayload)

            LearnMenu.write_file_json("./Chatbot/Intents/Learn/intents/Menu - Learn.json", intent)
            LearnMenu.write_file_json("./Chatbot/Intents/Learn/intents/Menu - Learn_usersays_en.json", trainingIntent)

    def createMainTopicMenu3(df):
        data = df[['Main Label', 'Main Topic', 'Sub Label', 'Sub Topic', 'Name']]
        data3Layers = data[(data['Sub Topic']!='')] # Get Intents with 3 layers structure
        data3Layers.reset_index(drop=True, inplace=True)

        maxi, count, intentCount = 0, 0, 0
        numOfIntentsMain = []
        listOfSubLabels, listOfsubLabelsGroup = [], []
        listOfSubTopicGrouping, listOfSubTopicNames = [], []
        payload, telePayload = [], []

        for index, row in data3Layers.iterrows():
            if int(row['Main Label']) > maxi:
                maxi = int(row['Main Label'])
                numOfIntentsMain.append(maxi)
        
        while intentCount < len(numOfIntentsMain):
            intentGroup = data3Layers.loc[data3Layers['Main Label'] == str(numOfIntentsMain[intentCount])]
           
            for index, rows in intentGroup.iterrows():
                listOfSubLabels.append(int(rows['Sub Label']))
            listOfsubLabelsGroup.append(max(listOfSubLabels))
            
            for i in range(1, listOfsubLabelsGroup[intentCount]+1):
                chipsTemplate = LearnMenu.getChipsPayload()
                teleTemplate = LearnMenu.getTelePayload()
                
                subGrouping = listOfSubLabels.count(i)
                listOfSubTopicGrouping.append(subGrouping)
                subTopicIntents = data3Layers.iloc[count:(count+1), 3:4]

                subTopicName = ''.join(i for i in str(subTopicIntents) if not i.isdigit())
                subTopicName = subTopicName.replace('Sub Topic\n', '')
                subTopicName = subTopicName.strip()

                listOfSubTopicNames.append(subTopicName)
                chipsTemplate["text"] = subTopicName
                teleTemplate[0]["text"] = subTopicName
                teleTemplate[0]["callback_data"] = subTopicName
        
                payload.append(chipsTemplate)
                telePayload.append(teleTemplate)
                count += (subGrouping) # move to next grouping
                
            intent = LearnMenu.getMainTopicTemplate()
            intent["name"] = "{}".format(rows['Main Topic'])
            intent["responses"][0]["messages"][1]["payload"]["richContent"][0][0]["options"] = payload
            intent["responses"][0]["messages"][0]["payload"]["telegram"]["reply_markup"]["keyboard"] = telePayload
 
            LearnMenu.write_file_json("./Chatbot/intents/{}.json".format(rows['Main Topic']), intent)

            '''
            Create Training Phrases File
            '''
            defaultPhrases = []
            defaultPhrases.append(rows['Main Topic'])
            defaultPhrases.append("Back to {}".format(rows['Main Topic']))
            #defaultPhrases.append("Topic {}".format(numOfIntentsMain[intentCount]))
            
            trainingIntent = []
            for phrase in defaultPhrases:
                trainingPayload = LearnMenu.getTrainingTemplate()
                trainingPayload["data"][0]["text"] = phrase
                trainingIntent.append(trainingPayload)
                LearnMenu.write_file_json("./Chatbot/intents/{}_usersays_en.json".format(rows['Main Topic']), trainingIntent)

            #Reset all items to move on to next Main Topic
            defaultPhrases.clear()
            trainingIntent.clear()
            listOfSubLabels.clear()
            payload.clear()
            telePayload.clear()

            intentCount+=1

        '''
        3rd Layer : Selection of intents
        '''
        intentCount = 0
        #numOfIntentsMain = []
        #payload, telePayload = [], []
        listOfMainTopics, listOfSubTopics = [], []

        while intentCount < len(numOfIntentsMain):
            sub_count = listOfsubLabelsGroup[intentCount]
            intentGroupMain = data3Layers.loc[data3Layers['Main Label'] == str(numOfIntentsMain[intentCount])]
            numOfIntentsSub = int(sub_count)

            for n in range (1, numOfIntentsSub+1):
                intentGroupSub = intentGroupMain.loc[intentGroupMain['Sub Label'] == str(n)]
                
                for k, rows in intentGroupSub.iterrows():
                    chipsTemplate = LearnMenu.getChipsPayload()
                    teleTemplate = LearnMenu.getTelePayload()
                    intent = LearnMenu.getSubTopicTemplate()

                    chipsTemplate['text'] = rows['Name']
                    teleTemplate[0]["text"] = rows['Name']
                    teleTemplate[0]["callback_data"] = rows['Name']
                    
                    payload.append(chipsTemplate)
                    telePayload.append(teleTemplate)

                listOfMainTopics.append(rows['Main Topic'])
                listOfSubTopics.append(rows['Sub Topic'])

                intent["name"] = "{} - {}".format(rows['Main Topic'], rows['Sub Topic'])
                intent["responses"][0]["messages"][1]["payload"]["richContent"][0][0]["options"] = payload
                intent["responses"][0]["messages"][0]["payload"]["telegram"]["reply_markup"]["keyboard"] = telePayload
                intent["responses"][0]["messages"][2]["payload"]["richContent"][0][0]["options"][0]['text'] = "Back to {}".format(rows['Main Topic'])
                
                LearnMenu.write_file_json("./Chatbot/intents/{} - {}.json".format(rows['Main Topic'], rows['Sub Topic']), intent)
                
                payload.clear()
                telePayload.clear()
                numOfIntentsSub +=1
            
            intentCount +=1
        
        '''
        Create training phrase file
        '''
        trainingPayload = []

        for i in range(len(listOfSubTopicGrouping)):
            trainingTemplate = LearnMenu.getTrainingTemplate()
            trainingTemplate["data"][0]["text"] = listOfSubTopicNames[i]
            trainingPayload.append(trainingTemplate)

            LearnMenu.write_file_json("./Chatbot/intents/{} - {}_usersays_en.json".format(listOfMainTopics[i], listOfSubTopics[i]), trainingPayload)

            trainingPayload.clear()
        listOfMainTopics.clear()
         
    def createMainTopicMenu2(df):
        data = df[['Main Label', 'Main Topic', 'Sub Label', 'Sub Topic', 'Name']]
        data2Layer = data[(data['Sub Topic']=='')]
        data2Layer.reset_index(drop=True, inplace=True)

        maxi, countOfIntents = 0, 0
        numOfIntentMain = []
        payload, telePayload = [], []

        for index, row in data2Layer.iterrows():
            if int(row['Main Label']) > maxi:
                maxi = int(row['Main Label'])
                numOfIntentMain.append(maxi)
            
        #Focus on Each Main Topic
        while countOfIntents < len(numOfIntentMain):
            intentGroup = data2Layer.loc[(data2Layer['Main Label'] == str(numOfIntentMain[countOfIntents]))]

            for j, rows in intentGroup.iterrows():
                chipsTemplate = LearnMenu.getChipsPayload()
                teleTemplate = LearnMenu.getTelePayload()
                
                chipsTemplate["text"] = rows["Name"]
                teleTemplate[0]["text"] = rows['Name']
                teleTemplate[0]["callback_data"] = rows['Name']
                
                payload.append(chipsTemplate)
                telePayload.append(teleTemplate)
                
            intent = LearnMenu.getMainTopicTemplate()
            intent["name"] = "{}".format(rows['Main Topic'])
            intent["responses"][0]["messages"][1]["payload"]["richContent"][0][0]["options"] = payload
            intent["responses"][0]["messages"][0]["payload"]["telegram"]["reply_markup"]["keyboard"] = telePayload

            LearnMenu.write_file_json("./Chatbot/intents/{}.json".format(rows['Main Topic']), intent)
            
            '''
            Create training phrase file
            '''
            trainingPhrases, trainingPayload= [], []

            trainingPhrases.append(rows["Main Topic"])
            #trainingPhrases.append("Topic {}".format(numOfIntentMain[countOfIntents]))
            #phrases.append("⮌ Back to {}".format(rows['Main Topic']))
            
            for phrase in trainingPhrases:
                trainingTemplate = LearnMenu.getTrainingTemplate()
                trainingTemplate["data"][0]["text"] = phrase
                trainingPayload.append(trainingTemplate)
                
            LearnMenu.write_file_json("./Chatbot/Intents/Learn/intents/{}_usersays_en.json".format(rows['Main Topic']), trainingPayload)
            
            '''
            Reset list for next group
            '''
            payload.clear()
            telePayload.clear()
            trainingPhrases.clear()
            trainingPayload.clear()
            
            countOfIntents +=1