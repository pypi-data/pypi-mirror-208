import pandas as pd
import json
import csv

class Worksheets():
  def __init__(self) -> None:
      pass

  def getIntentTemplate():
    return {
      "id": "b67e1e55-5fb5-4516-bb48-861e5be9334e",
      "name": "Log In - Sentiment (Awesome)",
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
              "lifespan": 1 #50
            }
          ],
          "parameters": [
            {
              "id": "f01c8262-a826-461b-ba66-ec3eb9667a0f",
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
            }
          ],
          "messages": [
            {
              "type": "0",
              "platform": "telegram",
              "title": "",
              "textToSpeech": "",
              "lang": "en",
              "speech": [
                "Yay, Keep it up! 🥳 \n\nFeel free to check out the latest worksheets or explore the menu below! You can also ask me anything about the subject, I would love to help!"
              ],
              "condition": ""
            },
            {
              "type": "1",
              "platform": "telegram",
              "title": "Latest Worksheets",
              "buttons": [],
              "textToSpeech": "",
              "lang": "en",
              "condition": ""
            },
            {
              "type": "1",
              "platform": "telegram",
              "title": "Menu",
              "buttons": [
                {
                  "postback": "Learn \u0026 Explore",
                  "text": "Learn \u0026 Explore"
                },
                {
                  "postback": "Results \u0026 Recommendation",
                  "text": "Results \u0026 Recommendation"
                }
              ],
              "textToSpeech": "",
              "lang": "en",
              "condition": ""
            },
            {
              "type": "0",
              "title": "",
              "textToSpeech": "",
              "lang": "en",
              "speech": [
                "Yay, Keep it up! 🥳 \n\nFeel free to check out the latest worksheets or explore the menu below! You can also ask me anything about the subject, I would love to help!"
              ],
              "condition": ""
            },
            {
              "type": "0",
              "title": "",
              "textToSpeech": "",
              "lang": "en",
              "speech": [
                "Latest Worksheets:"
              ],
              "condition": ""
            },
            {
              "type": "4",
              "title": "",
              "payload": {
                "richContent": [
                  [
                    {
                      "icon": {
                        "type": "chevron_right"
                      },
                      "type": "button",
                      "link": "https://www.youtube.com/",
                      "text": "Worksheet 1"
                    },
                    {
                      "icon": {
                        "type": "chevron_right"
                      },
                      "link": "https://www.youtube.com/",
                      "type": "button",
                      "text": "Worksheet 2"
                    },
                    {
                      "link": "https://www.youtube.com/",
                      "text": "Worksheet 3",
                      "type": "button",
                      "icon": {
                        "type": "chevron_right"
                      }
                    }
                  ]
                ]
              },
              "textToSpeech": "",
              "lang": "en",
              "condition": ""
            },
            {
              "type": "0",
              "title": "",
              "textToSpeech": "",
              "lang": "en",
              "speech": [
                "Menu:"
              ],
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
                          "text": "Learn \u0026 Explore"
                        },
                        {
                          "text": "Results \u0026 Recommendation"
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

  def getTrainingIntent():
    return {
      "id": "e5369794-5af3-4884-b591-94c704af567c",
      "data": [
        {
          "text": "Awesome 😄",
          "userDefined": False
        }
      ],
      "isTemplate": False,
      "count": 0,
      "lang": "en",
      "updated": 0
  }

  def getButtonPayload():
    return  {
      "type": "button",
      "icon": {
      "type": "chevron_right"
      },
      "link": "link1",
      "text": "Worksheet 1"
    }

  def getTeleInline():
    return {
        'postback': 'link',
        'text': 'Worksheet'
    }

  def write_file_json(QA_Data, data):
      with open(QA_Data, "w", encoding="utf-8") as jsonfile:
          json.dump(data, jsonfile, indent=4)

  def createWsIntent(df):
    sentiments = ["Awesome", "Doing Fine", "It's been a rough week", "Still Hanging There"]
    text_response = ["Yay, Keep it up! 🥳 \n\nFeel free to check out the hot topics or explore the menu below! You can also ask me anything about the subject, I would love to help!", 
    "That\u0027s good to hear! 😃 \n\nFeel free to check out the hot topics or explore the menu below! You can also ask me anything about the subject, I would love to help!", 
    "Hang on there and don\u0027t give up! Tomorrow will be better. 😉 \n\nFeel free to check out the hot topics or explore the menu below! You can also ask me anything about the subject, I would love to help!", 
    "Keep pushing and it will get better! 🤗 \n\nFeel free to check out the hot topics or explore the menu below! You can also ask me anything about the subject, I would love to help!"]

    # Extract from SL Inputs the Worksheets Name & Links
    worksheets = list(df["Worksheets"])
    links = list(df["Links"])
    buttons, cards = [], []

    for i in range(len(worksheets)):
      button = Worksheets.getButtonPayload()
      button["text"] = "Worksheet " + str(i+1)
      button["link"] = links[i]
      buttons.append(button)

      card = Worksheets.getTeleInline()
      card["text"] = "Worksheet " + str(i+1)
      card["postback"] = links[i]
      cards.append(card)

    intent_payload = Worksheets.getIntentTemplate()
    intent_payload["responses"][0]["messages"][5]["payload"]["richContent"][0] = buttons
    intent_payload["responses"][0]["messages"][1]["buttons"] = cards

    trainingIntent = Worksheets.getTrainingIntent()
  
    for i in range(4):
        intent_payload['name'] = "Log In - Sentiment ({})".format(sentiments[i]) # Intent Name follows Criteria
        intent_payload["responses"][0]["messages"][0]["speech"][0] = text_response[i]
        intent_payload["responses"][0]["messages"][3]["speech"][0] = text_response[i]
        
        trainingIntent['data'][0]['text'] = sentiments[i]

        Worksheets.write_file_json("./Chatbot/Intents/Worksheets/intents/Log In - Sentiment ({}).json".format(sentiments[i]), intent_payload)
        Worksheets.write_file_json("./Chatbot/Intents/Worksheets/intents/Log In - Sentiment ({})_usersays_en.json".format(sentiments[i]), trainingIntent)
