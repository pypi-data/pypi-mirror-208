import pandas as pd
import os
import TPEBot

class Password():
    def __init__(self) -> None:
        pass

    def createPwIntent(df):
        package_dir = os.path.abspath(TPEBot.__path__[0])
        template_dir = (package_dir.replace('\\','/')) + '/Data/Log In - Results - Password - Template.json'

        f1 = open(template_dir, "r", encoding='utf8')
        template = f1.read()
        f2 = open("./Chatbot/Intents/Recommended/intents/Log In - Results - Password.json", 'w', encoding='utf8')

        project_id = df['GCP Project ID'][0]

        template = template.replace("RESETURLHERE", "https://"+project_id+".web.app/reset.html")
        f2.write(template)

        f1.close()
        f2.close()
