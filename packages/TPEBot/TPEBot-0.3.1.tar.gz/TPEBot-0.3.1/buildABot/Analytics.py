# import packages
import numpy as np
import pandas as pd
import os
import time
import copy
import re
from shutil import copyfile
from dateutil import parser
from datetime import datetime

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Analytics:
    def __init__(self) -> None:
        pass
    
    def retrieveData():
        logs_raw = pd.read_csv('./Chatbot/Data/Logs.csv')
        qna_data = pd.read_excel('./Chatbot/Data/qna-data.xlsx')
        students_data = pd.read_excel('./Chatbot/Data/students-data.xlsx')
        dummy = pd.read_excel('./Tutor/SL Inputs.xlsx', dtype=str)
        return logs_raw, qna_data, students_data, dummy

    def cleanData(logs_raw, dummy):
        data = logs_raw[['labels.type', 'textPayload', 'timestamp', 'trace']]
        df = data[[]]
        data_filtered = []
        row_number = 0

        for index, row in data.iterrows():
            if (row['labels.type']=='dialogflow_response'):
                data_filtered.append(row)

        for i in range (len(data_filtered)):
            
            queryInput = data_filtered[i]["textPayload"]
            queryInput = queryInput.replace('\n', '')
            queryInput = queryInput.replace('Dialogflow Response : ','')
            queryInput = queryInput.replace(' {',': {')
            
            query_json = re.sub("(\w+):", r'"\1":', queryInput) #insert douoble quotes for keys
            
            # Extract User Login ID
            parameter_start = query_json.find('"key": "loginid"')
            parameter_end = query_json.find('"webhook_for_slot_filling_used": "false"')
            
            loginID = query_json[parameter_start:parameter_end]
            loginstr = loginID.find('"string_value":')
            loginID = loginID[loginstr+15:loginstr+15+8]
            
            if (loginID == ''):
                parameter_start = query_json.find('"key": "loginID"')
                loginID = query_json[parameter_start:parameter_end]
                loginstr = loginID.find('"string_value":')

                loginID_start = loginID[loginstr+17:]
                loginID_end = loginID_start.find('"')
            
                loginID = loginID_start[:loginID_end]
            
            # Extract Query Text from user
            query_start = query_json.find('"resolved_query"')
            query_end = query_json.find('"score"')
            query_text = query_json[query_start:query_end]
            query = query_text[18:-1]
            
            if (query[:9]=='"WELCOME"'):
                query=query[:9]
                loginID = ''

            input_start = query.find('"')+1
            input_end = query[input_start:].find('"')
            query = query[input_start : input_start+input_end]
            
            # Extract Intent Name (Response)
            intent_start = query_json.find('"intent_name":')
            intent_end = query_json.find('"webhook_used":')
            intent_response = query_json[intent_start:intent_end]
            intent_name = intent_response[15:-1]
            intent_name = intent_name.replace('"',"")
            intent_name = intent_name.replace('    end_conversation: true', '')
            intent_name = intent_name.rstrip()

            # Extract Timestamp
            time_stamp = data_filtered[i]["timestamp"]
            stamp_date = time_stamp[:10]

            if "-" in stamp_date:
                y = stamp_date.split("-")[0]
                m = stamp_date.split("-")[1]
                d = stamp_date.split("-")[2]

                stamp_date = (f"{d}/{m}/{y}")

            stamp_UTC = time_stamp[11:19]
            stamp_time_8 = int(stamp_UTC[:2]) + 8 # convert to our +8hrs
            if(stamp_time_8 >= 24):
                stamp_time_8 = stamp_time_8 - 24
            stamp_time = stamp_UTC.replace(stamp_UTC[:2],str(stamp_time_8))
            

            # Extract Session ID
            session = data_filtered[i]["trace"]
            sessionID = session.replace("dfMessenger-","")
            
            df.loc[i, "Date"] = stamp_date
            df.loc[i, "Time"] = stamp_time
            df.loc[i, "Session"] = sessionID
            df.loc[i, "Login ID"] = loginID
            df.loc[i, "Query Input"] = query
            df.loc[i, "Intent Response"] = intent_name

        welcome_index = df.index[df['Intent Response']=='Default Welcome Intent   '].tolist()
        df = df.drop(welcome_index) # remove welcome logs 

        fallback_index = df.index[df['Intent Response'] == 'Default Welcome Intent - fallback   '].tolist()
        df = df.drop(fallback_index) #remove wrong loginID logs

        login_index = df.index[df['Intent Response'] == 'Log In   '].tolist()
        df = df.drop(login_index) #remove login logs

        invalidID = []
        
        df.fillna(value='', inplace=True)
        invalidID = dummy['LoginID'][0]

        dummy_index = df.index[df['Login ID'].str.strip() == invalidID].tolist()
        df = df.drop(dummy_index)

        empty_index = df.index[df['Login ID'] == ('      ')].tolist()
        df = df.drop(empty_index)
        
        empty_index = df.index[df['Login ID'] == ('')].tolist()
        df = df.drop(empty_index)

        df.to_excel('./Chatbot/Dashboard/Data/backup/logs-main.xlsx', index = False)
        
        logs_main = copy.deepcopy(df)

        timestr = time.strftime("%m%d%y-%H%M")

        try:
            copyfile("./Chatbot/Dashboard/Data/logs-main.xlsx", "./Chatbot/Dashboard/Data/backup/logs-main-{timestr}.xlsx")

        except:
            pass

        logs_main.to_excel("./Chatbot/Dashboard/Data/logs-main.xlsx", index = False)

        return logs_main
    
    def match_unmatchFiles(logs_main):
        # Un-Matched Intents into a file
        unmatched = logs_main[logs_main['Intent Response'] == 'Fallback - Logged In']
        unmatched.to_excel("./Chatbot/Dashboard/Data/logs-unmatched.xlsx", index = False)

        # Matched Intents into a file
        fallbacks = ['Fallback - Logged In - fallback', 'Fallback - Logged In - yes', 'Fallback - Logged In - no', 'Fallback - Logged In']
        matched = logs_main[~logs_main['Intent Response'].isin(fallbacks) ]
        matched.to_excel("./Chatbot/Dashboard/Data/logs-matched.xlsx", index = False)

        return logs_main

    def saveCleanedLogs(logs_main):
        logs_main = pd.read_excel("./Chatbot/Dashboard/Data/logs-main.xlsx")
        return logs_main
 
    def voteFiles(logs_main):
        logs_main_helpful = copy.deepcopy(logs_main)
        logs_main_helpful = logs_main_helpful.iloc[::-1].reset_index(drop = True)

        session = None
        intent = None

        session_array = []
        intent_array = []
        helpful_array = []

        for i in range(len(logs_main_helpful)):
            intent = logs_main_helpful["Intent Response"][i]
            
            if (str(intent[0]).isnumeric()):
                session = logs_main_helpful["Session"][i]
                
                if (len(helpful_array) < len(intent_array)):
                    helpful_array.append(None)

                session_array.append(session)

                intent_array.append(intent)
                
            elif ("Upvote" in intent) or ("Downvote" in intent):
                helpful_array.append(intent)

            else:
                continue

        if len(helpful_array) < len(session_array):
            helpful_array.append(None)

        helpful_data = {"Session": session_array, "Intent Response": intent_array, "Vote": helpful_array}
        helpful_df = pd.DataFrame(data = helpful_data)

        helpful_df.reset_index(drop=True, inplace=True)
        helpful_df = helpful_df.iloc[::-1].reset_index(drop = True)

        timestr = time.strftime("%m%d%y-%H%M")

        try:
            copyfile("./Chatbot/Dashboard/Data/logs-helpful.xlsx", "./Chatbot/Dashboard/Data/backup/logs-helpful-{timestr}.xlsx")

        except:
            pass

        helpful_df.to_excel("./Chatbot/Dashboard/Data/logs-helpful.xlsx", index = False)

        return logs_main, helpful_df

    def durationFile(logs_main, helpful_df):
        logs_helpful = helpful_df

        logs_main_duration = copy.deepcopy(logs_main)
        logs_main_duration = logs_main_duration.iloc[::-1].reset_index(drop = True)

        session = None
        timestamp_start = None
        timestamp_end = None
        duration = None
        duration_in_s = None
        minutes = None

        session_array = []
        time_array = []

        datetime_array = []

        for i in range(len(logs_main_duration)):
            datetime_temp = datetime.combine(parser.parse(str(logs_main_duration["Date"][i])), parser.parse(str(logs_main_duration["Time"][i])).time())
            datetime_array.append(datetime_temp)

        logs_main_duration["Datetime"] = datetime_array

        logs_main_duration = logs_main_duration.sort_values(["Session", "Datetime"], ascending = [True, True])
        logs_main_duration = logs_main_duration.reset_index(drop = True)

        for i in range(len(logs_main_duration["Session"])):
            if (not session_array):
                session = logs_main_duration["Session"][i]
                timestamp_start = logs_main_duration["Datetime"][i]

                session_array.append(session)

            elif (logs_main_duration["Session"][i] != session_array[-1]) or (i == len(logs_main_duration["Session"]) - 1):
                timestamp_end = logs_main_duration["Datetime"][i - 1]

                duration = timestamp_end - timestamp_start
                duration_in_s = duration.total_seconds()

                minutes = divmod(duration_in_s, 60)[0]

                if (minutes == 0):
                    minutes = 1

                time_array.append(minutes)

                if (logs_main_duration["Session"][i] != session_array[-1]) and (i != len(logs_main_duration["Session"]) - 1):
                    session = logs_main_duration["Session"][i]
                    timestamp_start = logs_main_duration["Datetime"][i]

                    session_array.append(session)

        duration_data = {"Session": session_array, "Duration": time_array}
        duration_df = pd.DataFrame(data = duration_data)

        timestr = time.strftime("%m%d%y-%H%M")

        try:    
            copyfile("./Chatbot/Dashboard/Data/logs-duration.xlsx", "./Chatbot/Dashboard/Data/backup/logs-duration-{timestr}.xlsx")
        except:
            pass

        duration_df.to_excel("./Chatbot/Dashboard/Data/logs-duration.xlsx", index=False)

        return logs_helpful

    def corrFile(qna_data, logs_helpful):
        intent_1 = None
        intent_2 = None

        distance = None

        intent_1_array = []
        intent_2_array = []

        distance_array = []

        data = {"intent_1": intent_1_array, "intent_2": intent_2_array}
        corr_df = pd.DataFrame(data = data)


        for i in qna_data["Full Name"]:
            intent_1 = i

            for j in qna_data["Full Name"]:
                if j != intent_1:
                    intent_2 = j

                    if (len(corr_df.loc[(corr_df["intent_2"] == intent_1) & (corr_df["intent_1"] == intent_2)])) == 0:
                        
                        new_row = {"intent_1": intent_1, "intent_2": intent_2}
                        corr_df = corr_df.append(new_row, ignore_index = True)

        for i in range(len(corr_df)):
            distance_array.append([])

        corr_df["distance_array"] = distance_array

        seeking = False

        for i in range(len(corr_df)):
            intent_1 = corr_df["intent_1"][i]
            intent_2 = corr_df["intent_2"][i]

            for j in range(len(logs_helpful)):
                if (seeking == False):
                    if (logs_helpful["Intent Response"][j] == intent_1):
                        start_num = j
                        session = logs_helpful["Session"][j]
                        seeking = True
                    
                if (seeking == True):
                    for k in range(len(logs_helpful)):
                        if (logs_helpful["Intent Response"][k] == intent_2) and (logs_helpful["Session"][k] == session):
                            end_num = k

                            distance = abs(k - j)
                            corr_df["distance_array"][i].append(distance)

                            seeking = False
                            break

                        elif (logs_helpful["Session"][k] != session) and (k < j):
                            continue

                        elif (logs_helpful["Session"][k] != session) and (k > j):
                            seeking = False
                            break         

        distance_avg = []

        for i in range(len(corr_df)):
            try:
                distance_avg.append(sum(corr_df["distance_array"][i]) / len(corr_df["distance_array"][i]))

            except:
                distance_avg.append(None)

        corr_df["distance_average"] = distance_avg

        frequency_array = []

        for i in range(len(corr_df)):
            frequency_array.append(len(corr_df["distance_array"][i]))

        corr_df["frequency"] = frequency_array

        timestr = time.strftime("%m%d%y-%H%M")

        try:
            copyfile("./Chatbot/Dashboard/data/logs-corr.xlsx", "./Chatbot/Dashboard/backup/logs-corr-{timestr}.xlsx")

        except: 
            pass

        corr_df.to_excel("./Chatbot/Dashboard/Data/logs-corr.xlsx", index=False)

        return logs_helpful

    def pathFile(logs_helpful):
        logs_helpful_reversed = logs_helpful.iloc[::-1].reset_index(drop = True)
        sessions_list = logs_helpful_reversed["Session"].unique()

        logs_path = pd.DataFrame(data = {"Session": [], "Intent 1": [], "Intent 2": [], "Intent 3": [], "Intent 4": [], "Intent 5": [], "Intent 6": [], "Intent 7": [], "Frequency": []})

        new_row = {}

        for i in sessions_list:
            session = i
            new_row["Session"] = session
            new_row["Frequency"] = 1

            logs_helpful_reversed_filtered = logs_helpful_reversed.loc[logs_helpful_reversed["Session"] == i].reset_index(drop = True)

            for j in range(1, 8):
                exec(f"intent_{j} = None")

            intent_7 = None

            for j in range(len(logs_helpful_reversed_filtered)):
                if j == 7:
                    break

                else:
                    exec(f"intent_{j + 1} = logs_helpful_reversed_filtered['Intent Response'][j]")

            for j in range(1, 8):
                exec(f"new_row['Intent {j}'] = intent_{j}")

            logs_path = logs_path.append(new_row, ignore_index = True)

        timestr = time.strftime("%m%d%y-%H%M")

        try:
            copyfile("./Chatbot/Dashboard/data/logs-path.xlsx", "./Chatbot/Dashboard/backup/logs-path-{timestr}.xlsx")

        except: 
            pass

        logs_path.to_excel("./Chatbot/Dashboard/Data/logs-path.xlsx", index=False)
