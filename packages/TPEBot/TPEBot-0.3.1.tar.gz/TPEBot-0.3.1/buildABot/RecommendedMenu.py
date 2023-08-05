# Import Libraries
import csv
import json
import pandas as pd

class RecommendedMenu():
  def __init__(self) -> None:
      pass
    
  def getRecoIntent():
    return {
      "id": "de288473-414e-4fd8-aaa4-811f17c1db50",
      "name": "Menu - Recommended - {}",
      "auto": True,
      "contexts": [
          "loginID",
          "password"
        ],
      "responses": [
        {
          "resetContexts": False,
          "action": "",
          "affectedContexts": [
            {
              "name": "loginID",
              "lifespan": 1 #50
            },
            {
              "name": "password",
              "lifespan": 100
            }
          ],
          "parameters": [
            {
              "id": "575c9164-d3da-4344-8f1e-f822383eeafc",
              "name": "loginID",
              "required": False,
              "dataType": "@LoginID",
              "value": "#loginID.loginID",
              "defaultValue": "",
              "isList": False,
              "prompts": [],
              "promptMessages": [],
              "noMatchPromptMessages": [],
              "noInputPromptMessages": [],
              "outputDialogContexts": []
            },
            {
              "id": "dd192f56-9b1f-4f21-890c-a2d1a82f773b",
              "name": "pwd",
              "required": True,
              "dataType": "@sys.any",
              "value": "#password.pwd",
              "defaultValue": "",
              "isList": False,
              "prompts": [
                {
                  "lang": "en",
                  "value": "Please enter your password to access the results:"
                }
              ],
              "promptMessages": [],
              "noMatchPromptMessages": [],
              "noInputPromptMessages": [],
              "outputDialogContexts": []
            }
          ],
          "messages": [],
          "speech": []
        }
      ],
      "priority": 500000,
      "webhookUsed": True,
      "webhookForSlotFilling": False,
      "fallbackIntent": False,
      "events": [],
      "conditionalResponses": [],
      "condition": "",
      "conditionalFollowupEvents": []
    }

  def getAssignmentMenu():
    return {
      "id": "b6b5f5c1-04fb-4745-b8e1-1aa250d684ec",
      "name": "", # Criteria
      "auto": True,
      "contexts": [
        "loginID",
        "password"
      ],
      "responses": [
        {
          "resetContexts": False,
          "action": "",
          "affectedContexts": [
            {
              "name": "loginID",
              "lifespan": 1 #50
            },
            {
              "name": "password",
              "lifespan": 100
            }
          ],
          "parameters": [],
          "messages": [
            {
              "type": "1",
              "platform": "telegram",
              "title": "Available Assignment Recommended Menu:", 
              "buttons": [],
              "textToSpeech": "",
              "lang": "en",
              "condition": ""
            },
            {
              "type": "4",  # Web Response
              "title": "",
              "payload": {
                "richContent": [
                  [
                    {
                        "text": "Available Assignment Recommended Menu:"
                    },
                    {
                      "type": "chips",
                      "options": [] # Web Chips Selection here
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

  def getIntent():
    return {
      "id": "b6b5f5c1-04fb-4745-b8e1-1aa250d684ec",
      "name": "", # Criteria
      "auto": True,
      "contexts": [
        "loginID",
        "password"
      ],
      "responses": [
        {
          "resetContexts": False,
          "action": "",
          "affectedContexts": [
            {
              "name": "loginID",
              "lifespan": 1 #50
            },
            {
              "name": "password",
              "lifespan": 100
            }
          ],
          "parameters": [],
          "messages": [
            {
              "type": "4",  # Telegram Response
              "platform": "telegram",
              "title": "",
              "payload": {
                "telegram": {
                  "reply_markup": {
                    "keyboard": []  # Telegram inline Selection here
                  },
                  "text": "Pick a topic."
                }
              },
              "textToSpeech": "",
              "lang": "en",
              "condition": ""
            },
            {
              "type": "4",  # Web Response
              "title": "",
              "payload": {
                "richContent": [
                  [
                    {
                      "type": "chips",
                      "options": [] # Web Chips Selection here
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

  def getSubtopicIntent():
    return {
      "id": "a22ba3ca-fce6-47cf-a06d-40e48989c8c3",
      "name": "", #Main Topic - Sub Topic
      "auto": True,
      "contexts": [
        "loginID",
        "password"
      ],
      "responses": [
        {
          "resetContexts": False,
          "action": "",
          "affectedContexts": [
            {
              "name": "loginID",
              "lifespan": 1 #50
            },
            {
              "name": "password",
              "lifespan": 100
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
                "richContent": [
                  [
                    {
                      "options": [
                        {
                          "text": "" #Intent Name
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
                "text": "Back to Recommended Menu", #Back to ['Sub Topic']
                "image": {
                  "src": {
                    "rawUrl": "https://firebasestorage.googleapis.com/v0/b/almgtbot.appspot.com/o/left-arrow-curved-black-symbol.png?alt=media&token=f0225665-02e7-459f-b8e9-1c19618a7234"
                  }
                }
              },
              {
                "text": "Go to Learn Menu",
                "image": {
                  "src": {
                    "rawUrl": "https://firebasestorage.googleapis.com/v0/b/almgtbot.appspot.com/o/home%20(1).png?alt=media&token=c8b0db13-9aeb-48ab-ad44-6134a55049e2"
                  }
                }
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

  def getTeleInline():
      return [{
          "text": "", #Intent Name
          "callback_data": "" #Intent Name
      }]

  def getTeleCard():
    return {
      "postback": "",
      "text": ""
    }

  def getChips():
    return {
      "text": ""
    }

  def getTrainingPhrases():
      return {
      "id": "e4442cbe-5335-4282-8691-890ba020b0aa",
      "data": [
        {
          "text": "",     # Phrases to call out Main Menu
          "userDefined": False
        }
      ],
      "isTemplate": False,
      "count": 0,
      "lang": "en",
      "updated": 0
    }

  def append_file_json(jsonfile, d): #Store entity template into json file
      with open(jsonfile, 'a') as outfile:
              outfile.write(json.dumps(d))
              outfile.close()

  def write_file_json(QA_Data, data):
      with open(QA_Data, "w", encoding="utf-8") as jsonfile:
          json.dump(data, jsonfile, indent=4)

  def getInfo(resultFile, rubrics):
    # Extract topics tested in assessment from Rubrics
    sheets = pd.ExcelFile(resultFile).sheet_names # list all sheets in the file
    assignments = sheets[1:] # get list of assignments

    topics = list(rubrics['Criteria'])
    numOfTopics = len(topics)

    return assignments, topics, numOfTopics

  def createRecoMainMenu(assignments):
    tele, web = [], []
    training_phrases = []

    # 1) Menu with all the assignment as selection (1st Layer)
    for assignment in assignments:
        intent_payload = RecommendedMenu.getAssignmentMenu()
        card = RecommendedMenu.getTeleCard()
        chips_text = RecommendedMenu.getChips()

        intent_payload['name'] = "Menu - Recommended" # Intent Name follows Criteria

        card['text'] = assignment  # TopicName
        card['postback'] = assignment   # TopicName

        tele.append(card)     # combine all topics payload

        chips_text['text'] = assignment  # TopicName
        web.append(chips_text)   # Combine all Topics payload

    # Training Phrases to call out RecommendedMenu - Criteria
    train = ['Recommended Menu', 'Back to Recommended Menu', 'See Results', 'Results', 'Recommended Topics', 'Recommendation', 'Results & Recommendation', 'Assignments', 'Assignments Menu', 'Check Assignment', '/recomenu', '/assignment', 'Go to Recommended Menu', 'Recommended', '/recomenu@bot']
    for phrase in train:
        training_payload = RecommendedMenu.getTrainingPhrases()
        training_payload["data"][0]["text"] = phrase
        training_phrases.append(training_payload)
            
    # Put Inline & Chips into intent payload
    intent_payload['responses'][0]['messages'][0]['buttons'] = tele
    intent_payload['responses'][0]['messages'][1]['payload']['richContent'][0][1]['options'] = web

    RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended.json", intent_payload)
    RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended_usersays_en.json", training_phrases)

    tele.clear()
    web.clear()
    training_phrases.clear()

  def createRecoAssignmentMenu(assignments):
    training_phrase = []

    # Create assignment intents to handle individual recommended menu
    for assignment in assignments:
        payload = RecommendedMenu.getRecoIntent()
        payload["name"] = 'Menu - Recommended - {}'.format(assignment)

        training = RecommendedMenu.getTrainingPhrases()
        training["data"][0]["text"] = '{}'.format(assignment)
        training_phrase.append(training)
        
        RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended - {}.json".format(assignment), payload)
        RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended - {}_usersays_en.json".format(assignment), training_phrase)
        training_phrase.clear()
  
  def createRecoTopicMenu(topics, numOfTopics, rubrics):
    # 2) Menu with all the criteria as selection (2nd Layer)
    tele, web, phrases, training_phrases = [], [], [], []

    # loc each topic for each criteria and get intent number
    for i in range(numOfTopics):  # Loop n times, n = number of topics
        
        subTopicsName = rubrics['Sub Topic'][i]  # Get the Main Label for each Criteria
        subtopics = subTopicsName.split(', ')  # Store the Main Topics for each Criteria
        
        for subtopic in subtopics:
            if subtopic  != '':
                # referencing intent number to QA_Data and get text, put into placeholders
                intent_payload = RecommendedMenu.getIntent()
                inline = RecommendedMenu.getTeleInline()
                chips_text = RecommendedMenu.getChips()

                intent_payload['name'] = "Menu - Recommended - Criteria {}".format(i+1) # Intent Name follows Criteria

                inline[0]['text'] = '[Recommended] ' + subtopic  # TopicName
                inline[0]['callback_data'] = '[Recommended] ' + subtopic    # TopicName
                tele.append(inline)     # combine all topics payload

                chips_text['text'] = '[Recommended] ' + subtopic  # TopicName
                web.append(chips_text)   # Combine all Topics payload
        
        # Training Phrases to call out RecommendedMenu - Criteria
        phrases.append("[Rubrics] {}".format(topics[i]))
        phrases.append("Back to [Rubrics] {}".format(topics[i]))
        phrases.append("❗ [Rubrics] {}".format(topics[i]))
        
        for phrase in phrases:
            training_payload = RecommendedMenu.getTrainingPhrases()
            training_payload["data"][0]["text"] = phrase
            training_phrases.append(training_payload)

        # Put Inline & Chips into intent payload
        intent_payload['responses'][0]['messages'][0]['payload']['telegram']['reply_markup']['keyboard'] = tele
        intent_payload['responses'][0]['messages'][1]['payload']['richContent'][0][0]['options'] = web
        
        RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended - Criteria {}.json".format(i+1), intent_payload)
        RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended - Criteria {}_usersays_en.json".format(i+1), training_phrases)
        
        tele.clear()
        web.clear()
        training_phrases.clear()
        phrases.clear()

  def createRecoSubTopicMenu(df, rubrics, numOfTopics):
      tele, web, phrases, training_phrases = [], [], [], []
      subTop = []

      #3) Menu with all the subtopic as selection (3rd layer)
      # loc each topic for each criteria and get intent number
      subTopics = rubrics['Sub Topic'].tolist()
      for topics in subTopics:
          topic = topics.split(', ')
          for t in topic:
              subTop.append(t)

      #sub = list(dict.fromkeys(subTop))
      #noOfSub = len(sub)
      #for i in range(noOfSub):
      for i in range(numOfTopics):

          subTopicsName = rubrics['Sub Topic'][i]  # Get the Main Label for each Criteria
          subtopics = subTopicsName.split(', ')  # Store the Main Topics for each Criteria
          #x = df[df['Sub Topic'] == sub[i]]

          for subtopic in subtopics:
              x = df[df['Sub Topic'] == subtopic]
              for k, rows in x.iterrows():
                  intent_payload = RecommendedMenu.getSubtopicIntent()
                  inline = RecommendedMenu.getTeleInline()
                  chips_text = RecommendedMenu.getChips()
                  
                  intent_payload['name'] = "Menu - Recommended - Criteria {} - {}".format(i+1, subtopic) # Intent Name follows Criteria

                  inline[0]['text'] = rows['Name']  # TopicName
                  inline[0]['callback_data'] = rows['Name']    # TopicName
                  tele.append(inline)     # combine all topics payload

                  chips_text['text'] = rows['Name']  # TopicName
                  web.append(chips_text)   # Combine all Topics payload

              # Training Phrases to call out RecommendedMenu - Criteria
              phrases.append("[Recommended] {}".format(subtopic))
              phrases.append("Back to [Recommended] {}".format(subtopic))
              phrases.append("❗ [Recommended] {}".format(subtopic))

              for phrase in phrases:
                  training_payload = RecommendedMenu.getTrainingPhrases()
                  training_payload["data"][0]["text"] = phrase
                  training_phrases.append(training_payload)

              # Put Inline & Chips into intent payload
              intent_payload['responses'][0]['messages'][0]['payload']['telegram']['reply_markup']['keyboard'] = tele
              intent_payload['responses'][0]['messages'][1]['payload']['richContent'][0][0]['options'] = web
              
              RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended - Criteria {} - {}.json".format(i+1, subtopic), intent_payload)
              RecommendedMenu.write_file_json("./Chatbot/Intents/Recommended/intents/Menu - Recommended - Criteria {} - {}_usersays_en.json".format(i+1, subtopic), training_phrases)
              
              tele.clear()
              web.clear()
              training_phrases.clear()
              phrases.clear()




