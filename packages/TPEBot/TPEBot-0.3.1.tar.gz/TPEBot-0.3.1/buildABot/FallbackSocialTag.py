import pandas as pd
import json

class FallbackSocialTag():
  def __init__(self) -> None:
      pass
    

  def getFallbackIntent():
    return {
      "id": "b3d275b9-bbc5-47ef-9b1d-232cd944cf38",
      "name": "Fallback - Logged In",
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
              "lifespan": 1 #2
            },
            {
              "name": "social",
              "lifespan": 1 
            }
          ],
          "parameters": [],
          "messages": [
            {
              "type": "0",
              "platform": "telegram",
              "title": "",
              "textToSpeech": "",
              "lang": "en",
              "speech": [ #telegram social tagging reply here
                  ],
              "condition": ""
            },
            {
              "type": "1",
              "platform": "telegram",
              "title": "Do you know the answer?",
              "buttons": [
                {
                  "postback": "yes",
                  "text": "Yes"
                },
                {
                  "postback": "no",
                  "text": "No"
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
                "We will get back to you soon...  \n\nMeanwhile, please continue to explore the menu:"
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
                          "text": "Learn & Explore"
                        },
                        {
                          "text": "Results & Recommendation"
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
      "fallbackIntent": True,
      "events": [],
      "conditionalResponses": [],
      "condition": "",
      "conditionalFollowupEvents": []
    }

  def write_file_json(QA_Data, data):
      with open(QA_Data, "w", encoding="utf-8") as jsonfile:
          json.dump(data, jsonfile, indent=4)
          
  def createSocialTag(df):
    intent = FallbackSocialTag.getFallbackIntent()

    msg = []
    def_msg = "We will get back to you soon... @"
    for index, row in df.iterrows():
        msg.append(def_msg + row["Telegram ID"] + " do you know the answer?")

    intent["responses"][0]["messages"][0]["speech"] = msg
    FallbackSocialTag.write_file_json("./Chatbot/Intents/Learn/intents/Fallback - Logged In.json", intent)