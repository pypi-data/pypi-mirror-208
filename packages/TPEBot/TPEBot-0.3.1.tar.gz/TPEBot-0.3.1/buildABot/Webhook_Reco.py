import os
import pandas as pd
import pkgutil

class Webhook_Reco:
    def __init__(self):
        pass

    def get_snapshot_template():
        return ' var CRITERIA = snapshot.child("/TOPICNAME/"+id).val();'

    def get_highlight_template():
        return ' var highlight = "";'

    def get_null_template():
        return ' && criteria{} == null'

    def get_if_template():
        return " if (criteria1 <= THRESHOLD) { flaw +=1; highlight1 = '❗';}"

    def get_results_template():
        return "+ 'CRITERIANAME :' + criteria1 + '\\n' "

    def getRubricsCriteria(df):
        topics = list(df['Criteria'])
        numOfTopics = len(topics)

        return topics, numOfTopics
    
    def getFromSLInputs(df, keyFile):
        acc_key = open(keyFile)
        acckey = acc_key.read()

        dbUrl = df['Firebase URL'][0]
        email = df['Email'][0]

        return acckey, dbUrl, email
    
    def webhookCode(acckey, dbUrl, email):
        f1 = pkgutil.get_data("buildABot.Data", '/Webhook/Recommended/index_template.js').decode("utf-8") 
        data = f1.read()

        data = data.replace("SERVICEACCOUNTKEYHERE", acckey)
        data = data.replace("DBURLHERE", dbUrl)
        data = data.replace("TUTOREMAILHERE", email)

        return data, f1

    def snapShotCode(data, numOfTopics, topics):
        snapshots = ''
        for i in range (1, numOfTopics+1):
            snapshot = Webhook_Reco.get_snapshot_template()
            snapshot = snapshot.replace('CRITERIA', 'criteria{}'.format(i))
            snapshot = snapshot.replace('TOPICNAME', topics[i-1])
            snapshot = snapshot.strip("'")
            snapshots += snapshot
        data = data.replace("SNAPSHOTHERE", snapshots)

        return data
    
    def highlightVariable(data, numOfTopics):
        highlights = ''
        for i in range (1, numOfTopics+1):
            highlight = Webhook_Reco.get_highlight_template()
            highlight = highlight.replace('highlight', 'highlight{}'.format(i))
            highlight = highlight.strip("'")
            highlights += highlight
        data = data.replace("HIGHLIGHTHERE", highlights)

        return data

    def nullStrings(data, numOfTopics):
        nullStrings = ''
        for i in range (2, numOfTopics+1):
            nullString = Webhook_Reco.get_null_template()
            nullString = nullString.replace('criteria{}', 'criteria{}'.format(i))
            nullStrings += nullString
        data = data.replace("NULLHERE", nullStrings)

    def highlightTopic(df, data, numOfTopics):
        threshold = list(df['Threshold'])
        ifloops = ''
        for i in range (1, numOfTopics+1):
            ifloop = Webhook_Reco.get_if_template()
            ifloop = ifloop.replace('criteria1', 'criteria{}'.format(i))
            ifloop = ifloop.replace('THRESHOLD', threshold[i-1])
            ifloop = ifloop.replace('highlight1', 'highlight{}'.format(i))
            ifloop.strip("'")
            ifloops += ifloop
        data = data.replace("IFLOOPHERE", ifloops)

        return data
    
    def reportCard(data, numOfTopics, topics):
        results = ''
        for i in range(1, numOfTopics+1):
            result = Webhook_Reco.get_results_template()
            result = result.replace('CRITERIANAME', topics[i-1])
            result = result.replace('criteria1', 'criteria{}'.format(i))
            result.strip("'")
            results += result
        data = data.replace("RESULTSHERE", results)

    def createRecoMenu(data, numOfTopics, topics):
        f2 = open('./Tutor/For Deployment/Recommended/index.js', 'w', encoding='utf8')

        payloads = ''

        for i in range (1, numOfTopics+1):
            payload = "{'text': highlight + 'CRITERIANAME'}, "
            payload = payload.replace('CRITERIANAME', str('[Rubrics] ' + topics[i-1]))
            
            highlights = ('highlight' + str(i))
            highlights = highlights.replace(' " ', "")
            
            payload = payload.replace('highlight', highlights)
            payloads += payload

        payloads = payloads[:-2]
        payload_text = '[' + payloads + ']'
        data = data.replace('MENUPAYLOADHERE', payload_text)

        f2.write(data)   # Write the file out again

        return f2
    
    def closeFiles(f1, f2):
        f1.close()
        f2.close()