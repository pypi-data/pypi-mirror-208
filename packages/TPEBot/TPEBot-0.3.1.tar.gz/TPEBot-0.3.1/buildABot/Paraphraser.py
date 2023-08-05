## Note: Installation of git required before running.
## pip install git+https://github.com/Prithi virajDamodaran/Parrot.git

# Importing libraries 
from parrot import Parrot
import torch
import warnings
import pandas as pd
import os
warnings.filterwarnings("ignore")
directory = os.getcwd()
parent = os.path.dirname(directory).replace('\\','/')

class Paraphraser():
    def __init__(self):
        pass

    # Set up for paraphraser model 'parrot'
    # To get reporoducle paraphrase generations
    def random_state(seed): 
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    #random_state(1234)

    def extractData(df):
        #Import data as df
        #df = pd.read_excel("../../Tutor/QA_Data.xlsx")

        qn = []
        for n in range (1, 11): # Extract Q1-Q10 from df into df_qn
            qn.append('Q{}'.format(n)) 
        df_qn = df[qn]

        dfString = df_qn.applymap(str)  ##Must be applied to be able to remove stopwords.
        return df, df_qn, dfString

    def paraphrase(dfString):
        print("Program running, please wait...")
        # Start paraphrasing process
        listOfParaphrased = [] ##To contain paraphrases
        numOfPhrases = []
        rowCounter = 0 ##To move on to the next row for the while loop
        numberOfRows = len(dfString) 
        columnCounter =0
        numOfParaphrases = 0
        numTrainPara = []

        # The paraphrase model
        parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5", use_gpu=True, use_auth_token='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')

        while rowCounter != numberOfRows:
            for i in dfString.iloc[rowCounter, 0:9]:
                if i != "nan":
                    para_phrases = parrot.augment(input_phrase = i, ##Paraphrasing
                                                    do_diverse = True,
                                                    max_return_phrases = 5)

                
                if para_phrases != None:
                    numOfParaphrases += len(para_phrases)
                    for para_phrase in para_phrases:
                        listOfParaphrased.append(para_phrase[0])      ##Once paraphrased, append to contain
            
                else:
                    rowCounter = rowCounter+1                   ##To move on to the next row(intent) 
                    break

            numTrainPara.append(numOfParaphrases)
            numOfParaphrases = 0

        paraphrases = pd.DataFrame(listOfParaphrased) #store all paraphrases into dataframe to use later
        return numTrainPara, paraphrases
    
    #paraphrases = pd.read_csv("Paraphrases_ALL.csv")
    #numTrainPara = pd.read_csv("Num of Paraphrases per Intent.csv")

    def createNewQAFile(numTrainPara, paraphrases, df, df_qn):
        # Organise paraphrases according to intent's training phrases
        intentcount = []
        listOfStacks = []
        start = 0
        empty = pd.DataFrame()


        noOfIntents = len(numTrainPara)
        #numPara = numTrainPara['Num'].tolist()
        #numPara = numPara[1:]

        #phrases = paraphrases['phrases'].tolist()

        for i in range (noOfIntents - 1):
            end = start + int(numTrainPara[i])
            
            data = pd.DataFrame(paraphrases[start:end])
            combined = data.stack()
            combined.reset_index(drop=True, inplace=True)
            empty = pd.concat([empty,combined], ignore_index=False, axis=1)
            
            start = end

        df_para = empty.transpose()
        df_para.reset_index(drop=True, inplace=True)

        # Combine Q1 - Q10 with paraphrases
        new = pd.DataFrame()
        new = pd.concat([df_qn, df_para], ignore_index=True, axis=1) #Combine by rows
        new = new.rename(columns={0:'Q1',1:'Q2',2:'Q3',3:'Q4',4:'Q5',5:'Q6',6:'Q7',7 :'Q8',8:'Q9',9:'Q10',
                            10:'Q11',11:'Q12',12:'Q13',13:'Q14',14:'Q15',15:'Q16',16:'Q17',17 :'Q18',18:'Q19',19:'Q20',
                            20:'Q21',21:'Q22',22:'Q23',23:'Q24',24:'Q25',25:'Q26',26:'Q27',27 :'Q28',28:'Q29',29:'Q30',
                            30:'Q31',31:'Q32',32:'Q33',33:'Q34',34:'Q35',35:'Q36',36:'Q37',37 :'Q38',38:'Q39',39:'Q40',
                            40:'Q41',41:'Q42',42:'Q43',43:'Q44',44:'Q45',45:'Q46',46:'Q47',47 :'Q48',48:'Q49',49:'Q50',
                            })
        for i in range(1, len(new.columns)+1):
            df["Q{}".format(i)] = new["Q{}".format(i)]
        df.to_excel("./Tutor/QA_Paraphrased.xlsx", index=False)
