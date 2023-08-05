import pandas as pd
import json
import os
from shutil import copyfile

class TelegramLogs:
    def __init__(self) -> None:
        pass

    def createTeleParticipation(teleLogs, df):
        df['Telegram Participation Replies'] = df['Telegram Participation Replies'].to_string()
        data = teleLogs[['labels.type', 'textPayload']]
        for col in df.columns:
            df["Telegram Participation"].values[:] = int(0) ## pre-set participation as 0
            df["Telegram Participation Replies"].values[:] = ''
        
        participants, replies = [], []

        for index, row in data.iterrows():
            if (row['labels.type']=='conversation_request'): #filter for user input / remove bot repsonses
                # convert payload to dict format to get data easily
                payload_string = str(row["textPayload"])
                payload_string = payload_string.replace("Dialogflow fulfillment request : ","")
                payload_json = json.loads(payload_string) 

                # filter for user responses to social tag
                if "action" in payload_json["queryResult"]: # only look at those that reply for social tag
                    if(payload_json["queryResult"]["action"] == "Fallback-LoggedIn.Fallback-LoggedIn-fallback"):
                        if(payload_json["originalDetectIntentRequest"]["payload"] != ''):
                        
                            telegram_id = payload_json["originalDetectIntentRequest"]["payload"]["data"]["from"]["username"] # get user tele id
                            reply = payload_json["queryResult"]["queryText"] # get participant reply

                            replies.append(reply)
                            participants.append(telegram_id)
        
        for user in participants:
            df.loc[df['Telegram ID'] == user, 'Telegram Participation'] += 1 # increment by 1 for every found id

        for i in range (len(participants)):
            df.loc[df['Telegram ID'] == participants[i], "Telegram Participation Replies"] += replies[i] + ', '
    
        df.to_excel("./Chatbot/Data/Telegram Participation.xlsx", index=False)

