import json
import os
import pandas as pd

class Intents():
  def __init__():
      pass

  def write_file_json(QA_Data, data):
      with open(QA_Data, "w", encoding="utf-8") as jsonfile:
          json.dump(data, jsonfile, indent=4)
          
  def getIntentTemplate():
      return {
    "id": "aaaea826-e707-4a08-ae6a-db8d3bd3d2b0",
    "name": "D2 - SampleAPA", #row["Name"]
    "auto": True,
    "contexts": ["loginID"],
    "responses": [
      {
        "resetContexts": False,
        "action": "",
        "affectedContexts": [
          {
            "name": "loginID",
            "lifespan": 50
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
                "parse_mode": "html",
                "text": "" #Response + IMAGE LINK
              }
            },
            "textToSpeech": "",
            "lang": "en",
            "condition": ""
          },
          {
            "type": "4",
            "platform": "telegram",
            "title": "",
            "payload": {
              "telegram": {
                "reply_markup": {
                  "keyboard": [
                    [
                      {
                        "text": "👍",
                        "callback_data": "👍"
                      }
                    ],
                    [
                      {
                        "text": "👎",
                        "callback_data": "👎"
                      }
                    ],
                    [
                      {
                        "text": "Back to {} Menu", #Back to Topic Menu
                        "callback_data": "Back to {} Menu"
                      }
                    ],
                    [
                      {
                        "callback_data": "Back to Main Menu",
                        "text": "Back to Main Menu"
                      }
                    ]
                  ]
                },
                "text": "Did you find our answers helpful?"
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
          "type": "image",
          "rawUrl": "" #["responses"][0]["messages"][0]["payload"][0]["richContent"][0]["rawUrl"] = row["Image Link"]
        },
        {
          "icon": {
            "type": "chevron_right",
            "color": "#FF9800"
          },
          "type": "button", 
          "link": "", #["responses"][0]["messages"][0]["payload"][0]["richContent"]["link"] = row["External Link"]
          "text": "" #["responses"][0]["messages"][0]["payload"][0]["richContent"]["text"] = row["Response 1"]
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

  def getTrainingPhrases():
      return {
          "id": "25d78c72-b3aa-47cc-8c9e-76faca9949d1",
          "data": [
            {
              "text": "", #Q{} Training phrase
              "userDefined": False
            }
          ],
          "isTemplate": False,
          "count": 0,
          "updated": 0
      }

  def getResponse2():
      return {
            "type": "4",
            "title": "",
            "payload": {
    "richContent": [
      [
        {
          "icon": {
            "type": "chevron_right",
            "color": "#FF9800"
          },
          "type": "button",
          "text": "" #["responses"][0]["messages"][0]["payload"][0]["richContent"]["text"] = row["Response 2"]
        }
      ]
    ]
  },
            "textToSpeech": "",
            "lang": "en",
            "condition": ""
          }

  def getFeedbackChips():
      return {
                      "type": "4",
                      "title": "",
                      "payload": {
                          "richContent": [
                              [
                                  {
                                      "options": [
                                          {
                                              "text": "\ud83d\udc4d"
                                          },
                                          {
                                              "text": "\ud83d\udc4e"
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

  def getYouMayAlsoLike():
    """
        Dialogflow's text template for "You may also like:"
        :return: JSON of text response of "you may also like"
    """
    return {
            "type": "0",
            "title": "",
            "textToSpeech": "",
            "lang": "en",
            "speech": [
              "👇 You may also like:"  
            ],
            "condition": ""
          }
  
  def getRelatedIntents():
    """
    Dialogflow's chips template for related intents to be recommended to user
    :return: JSON of chips response consisting all related intents
    """
    return {
      "type": "4",
      "title": "",
      "payload": {
          "richContent": [
              [
                  {
                      "options": [ # top neighbour intent button payload here ["payload"]["richContent"][0][0]
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

  def getRelatedIntentName():
    """
        Dialogflow's text template as placeholder for related intent's name
        :return: JSON of text response consisting all related intent's Q1 as name
    """
    return {
      "text": ""  # Intent Q1 as text
    }

  def getLabels(df):
    """
        To create labels for Main Topics, Sub Topics & Intents for Analytics, FAQ and Intent Naming purposes
        :return: [dataframe] Updated QA file with different labels columns
    """
    listOfMainTopics = df['Main Topic'].unique().tolist()  # Get list of topics
    mainTopicsLabels, subTopicsLabels, intentsLabels, numOfMTIntents = [], [], [], []  # Initialise empty arrays
    count = 1  # Set counter to 1

    '''
    Grouping Intents by Main & Sub Topics
    Set labels for MainTopics, SubTopics and Intents (To be used in Analytics)
    '''
    for i in range(len(listOfMainTopics)):  # Loop for no. of MainTopics
        subTopicsCount = 1  # set counter for subtopic
        mainTopics = df.loc[df['Main Topic'] == listOfMainTopics[i]]  # Filter to each Main Topics
        subTopics = mainTopics['Sub Topic'].unique().tolist()  # Get Sub Topics from each Main Topics

        if (subTopics != ['']):  # For intents that has subtopics
            for i in range(len(subTopics)):
                subTopic = mainTopics.loc[mainTopics['Sub Topic'] == subTopics[i]]  # Filter to each Sub Topics
                numOfSTIntents = len(subTopic.index) * [subTopicsCount]  # Get number of intents for each sub topics
                subTopicsLabels.extend(numOfSTIntents)  # Put labels from count of each subtopics into list
                subTopicsCount += 1
        else:  # For intent that has no sub topic
            numOfSTIntents = len(mainTopics.index) * ['']
            subTopicsLabels.extend(numOfSTIntents)  # Add blank to list to indicate no sub topics

        numOfMTIntents.append(len(mainTopics.index))  # Get number of intents for each main topics

    for num in numOfMTIntents:
        for i in range(num):
            mainTopicsLabels.append(count)  # Make Main Topics Labelling
            intentsLabels.append(i + 1)
        count += 1

    '''
    Create new columns for each labels
    Store updated QA with labels (for Analytics & FAQ)
    '''
    df['Main Label'] = mainTopicsLabels
    df['Sub Label'] = subTopicsLabels
    df['Intent Label'] = intentsLabels
    
    ''' Ensure Name is accepted '''
    df['Name'] = df['Name'].replace('/', ' or ')
    df['Name'] = df['Name'].replace('?', '')
    df['Name'] = df['Name'].replace('"', "'")
    df['Name'] = df['Name'].replace('.', '')
    df['Name'] = df['Name'].replace('[', '')
    df['Name'] = df['Name'].replace(']', '')
    df['Name'] = df['Name'].replace('#', '')
    df['Name'] = df['Name'].replace('$', '')

    # Intent Number, Small Name, Full Name
    intentNum, fullName, smallName, idxNum = [], [], [] , []
    intentNames = []
    for index, row in df.iterrows():
        if(len(row['Name']) > 100):
          print(['Name'][:100])
          intentNames.append(row['Name'][:100])
        else:
          intentNames.append(row['Name'])
        
        intent_name = str(row['Main Label']) + '.' + str(row['Intent Label']) + ' ' + row['Main Topic'] + ' - ' + row['Name']
        intentNum.append(str(row['Main Label']) + '.' + str(row['Intent Label']))
        fullName.append(intent_name) #for dashboard
        smallName.append(row['Main Topic'] + ' - ' + row['Name']) #for dashboard
        idxNum.append(str(index+1))

    df['Intent Number'] = intentNum
    df['Small Name'] = smallName
    df['Full Name'] = fullName
    df['Intent Name'] = intentNames
    df.to_excel('./Chatbot/Dashboard/Data/qna-data.xlsx', index=False)
    df.to_excel('./Chatbot/Data/qna-data.xlsx', index=False)
    
    return df
    
  def getIntents(df):
    """
        Create intents accordingly with Name, Contexts, Training Phrases & Response (Tele & Messenger)
        :param df: QA as dataframe including labels
        :return: JSON file for each intent
    """
    # -- Intents JSON Payload-- #
    for index, rows in df.iterrows():
        intentResponse1 = Intents.getIntentTemplate()
        intentResponse2 = Intents.getResponse2()
        feedbackChips = Intents.getFeedbackChips()
        recText = Intents.getYouMayAlsoLike()
        recResponse = Intents.getRelatedIntents()
        recIntentNames = Intents.getRelatedIntentName()
        recIntents = []  # List to store all the text payload for each related intent
        trainingPhrases = []
        
        # Intent Naming Format
        intent_name = str(rows['Main Label']) + '.' + str(rows['Intent Label']) + ' ' + rows['Main Topic'] + ' - ' + rows['Intent Name']
        intentResponse1.pop("id", None)
        intentResponse1["name"] = intent_name
        
        '''
        1) Response 1
        '''
        # [Messsenger] Pull data and place it to respective placeholders for response
        intentResponse1["responses"][0]["messages"][2]["payload"]["richContent"][0][0]["rawUrl"] = str(rows['Image Link'])
        intentResponse1["responses"][0]["messages"][2]["payload"]["richContent"][0][1]["text"] = rows["Response 1"]
        intentResponse1["responses"][0]["messages"][2]["payload"]["richContent"][0][1]["link"] = str(rows["External Link"])

       # [Telegram] Pull data and place it to respective placeholders for response
        if rows["Image Link"] != "":
            intentResponse1["responses"][0]["messages"][0]["payload"]["telegram"]["text"] = rows["Response 1"] + '\n' + str(rows["Image Link"])
        elif rows["External Link"] != "":
            intentResponse1["responses"][0]["messages"][0]["payload"]["telegram"]["text"] = rows["Response 1"] + '\n' + str(rows["External Link"])
        else:
            intentResponse1["responses"][0]["messages"][0]["payload"]["telegram"]["text"] = rows["Response 1"]

        # [Telegram] Back to Menu inline keyboard (UI)
        intentResponse1["responses"][0]["messages"][1]["payload"]["telegram"]["reply_markup"]["keyboard"][2][0]["text"] = "Back to {} Menu".format(rows["Main Topic"])
        intentResponse1["responses"][0]["messages"][1]["payload"]["telegram"]["reply_markup"]["keyboard"][2][0]["callback_data"] = "Back to {} Menu".format(rows["Main Topic"])


        '''
        2) Response 2
        '''
        if (rows["Response 2"] != ''): # Check for response 2
          intentResponse2["payload"]["richContent"][0][0]["text"] = rows["Response 2"]
          intentResponse1["responses"][0]["messages"].append(intentResponse2)

        '''
        3) Feedback Chips
        '''
        intentResponse1["responses"][0]["messages"].append(feedbackChips) # Add in feedback chips after response 1&2

        
        '''
        4) Related Intents (You May Also Like)
        '''
        if rows["Related Intent 1"] != "": # Check for related intents
            intentResponse1["responses"][0]["messages"].append(recText)  # Add in 'You may also like'

        for i in range(1, 30):
            intent_key = "Related Intent {}".format(str(i)) # Search for related intent's columns
            if intent_key in rows:
                if str(rows[intent_key]).strip() != "": # Check for related Intents
                    pd.set_option("display.max_colwidth", None) # Settings to show full text for chips
                    related = df[df['S/N'] == rows[intent_key]]
                    related_str = related['Q1'].to_string(index=False) #Get related intent's Q1 as display text for chips

                    # Pull data into the text payload and append to list
                    if related_str != '':
                        recIntentNames["text"] = related_str
                        recIntentNames_copy = recIntentNames.copy()
                        recIntents.append(recIntentNames_copy)
                    else: continue

                else: continue
                
        if recIntents != []: # Check if related intents not empty
          recResponse["payload"]["richContent"][0][0]["options"] = recIntents  # to put in all the chip texts into payload
          intentResponse1["responses"][0]["messages"].append(recResponse)  # to put in the payload into the intent template

        '''
        Training Phrases for each intent
        '''
        # Base case - intent name
        trainingPhrase = Intents.getTrainingPhrases()
        trainingPhrase["data"][0]["text"] = rows['Name']
        trainingPhrases.append(trainingPhrase)

        # Get all Questions from QAfile as training phrases and put it into placeholder
        for i in range(1, 40):
            trainingPhrase = Intents.getTrainingPhrases()
            trainingPhrase.pop("id", None)
            question_key = "Q{}".format(str(i)) # Seach for Questions columns
            if question_key in rows:
                if str(rows[question_key]).strip() != "":
                    trainingPhrase["data"][0]["text"] = rows[question_key]
                    trainingPhrases.append(trainingPhrase)  

        '''
        Write Intents & Training Phrases into JSON Files
        '''
        directory = os.getcwd().replace('\\','/')
        Intents.write_file_json("./Chatbot/Intents/Learn/intents/{}.json".format(intent_name), intentResponse1)
        Intents.write_file_json("./Chatbot/Intents/Learn/intents/{}_usersays_en.json".format(intent_name), trainingPhrases)

        recIntents.clear()  # clear list for next intent
