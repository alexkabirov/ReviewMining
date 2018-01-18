import spacy
import numpy
import en_core_web_lg
#from neo4j.v1 import GraphDatabase, basic_auth
from Ontology import *
import pandas as pd
# from spacy.symbols import ROOT

#githubtest_pull

print ("Loading the model...")
nlp = en_core_web_lg.load()
print("Loaded the model successfully, running...")
#load the reviews from the file
df1 = pd.read_excel("source.xlsx",sheet_name=4,header=0)
#driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "password"))
#session = driver.session()
#doc = nlp("This phone is not worth buying. Doesn't work good it's takes blurry looking pictures internet is slow cuts on and off earphones that came with the phone barely can hear out of one so please don't buy this phone.")
#doc = nlp("Works great but the camera was having focusing problems at first however I believe this was a software issue which was resolved after a update.After a month of use I cracked the screen luckily only in the corner I have never broken a phone screen before so a little disappointed also the camera is still very buggy. Fragile screen, but the edge display is nice.")
#We should add reading from the file directly using pandash
#parse the reviews (dependency parser)
reviews = []
for text in df1["Text"][:50]:
    reviews.append(nlp(text))
bad, good  = nlp(u'bad good')
#bad, good  = nlp(u'poor excellent')

def check_orientation(token,featureName,neg,logfile,printO = True):
    orientation = 0
    #check Exceptions
    feature = smartphone.feature_by_name(featureName)
    exception = feature.check_exception(token.lemma_)
    if exception != 0:
        if printO == True:
            print_orientation(token,neg,logfile,exception)
        return exception
    vsgood = good.similarity(token)
    vsbad = bad.similarity(token)
    #the significance is set to 5%  difference
    if (vsgood - vsbad) >= 0.05:
        orientation = 1
    elif (vsbad - vsgood) >= 0.05:
        orientation = -1
    # multiply by negation if present (default 1)
    orientation = orientation * neg
    if printO == True:
        print_orientation(token,neg,logfile,orientation)
    return orientation

#function to print orientation to log
def print_orientation(token,neg,logfile,orientation):
    if orientation > 0:
        logfile.write(" ".join(["\n  ",token.lemma_,'pos',str(neg)]))
    elif orientation < 0:
        logfile.write(" ".join(["\n  ",token.lemma_,'neg',str(neg)]))
    else:
        logfile.write(" ".join(["\n  ",token.lemma_,'neu',str(neg)]))

#function to check if negation dependency is present
def check_negation(token):
    neg = 1
    # check the negation
    for child in token.children:
        if child.dep_ == 'neg':
            neg = -1
    return neg

def set_opinion(results,feature,opinion,summary):
    # get result array for feature (first - positive, second - negative)
    if opinion is not None:
        featureOpinions = results.get(feature,[0,0])
        if opinion > 0:
            featureOpinions[0] += 1
            summary[0] += 1
            summary[1] += 1
        elif opinion < 0:
            featureOpinions[1] += 1
            summary[0] += 1
            summary[2] += 1
        results.update({feature:featureOpinions})
    return summary

#the switch using dictionaries
def dobj(token,featureName,logfile):
    neg = check_negation(token)
    return check_orientation(token,featureName,neg,logfile)
def nsubj(token,featureName,logfile):
    neg = check_negation(token)
    if token.lemma_ == 'be': #alterrnatively nsubj
        for child in token.children:
            if child.pos_ == 'ADJ': # child.dep_ == 'acomp'
                return check_orientation(child,featureName,neg,logfile)
            elif child.dep_ == 'prep':
                for subchild in child.children:
                    if subchild.pos_ == 'ADJ':
                        return check_orientation(subchild,featureName,neg,logfile)
    else:
        #check acomp
        for child in token.children:
            if child.dep_ == 'acomp': # child.pos_ == 'ADJ'
                return check_orientation(child,featureName,neg,logfile)
        test_orient = check_orientation(token,featureName,neg,logfile,printO = False)
        if test_orient == 0:
            for child in token.children:
                if child.dep_ == 'advmod': # child.dep_ == 'acomp'
                    return check_orientation(child,featureName,neg,logfile)
        else:
            return check_orientation(token,featureName,neg,logfile)

def compound(token,featureName,logfile):
    neg = check_negation(token.head)
    for child in token.children:
        if child.dep_ == 'amod': # child.dep_ == 'acomp'
            return check_orientation(child,featureName,neg,logfile)
    if token.dep_ == 'nsubj':
        for child in token.head.children:
            if child.dep_ == 'acomp': # child.pos_ == 'ADJ'
                return check_orientation(child,featureName,neg,logfile)
    return check_orientation(token,featureName,neg,logfile)
def pobj(token,featureName,logfile):
    if token.head.pos_ == "ADJ":
        #check the negation (specific case)
        neg = check_negation(token.head)
        return check_orientation(token.head,featureName,neg,logfile)
    else:
        logfile.write("   no match")
# dictionary of possible functions to call by dep_
options = {"dobj" : dobj,
           "nsubj" : nsubj,
           "compound" : compound,
           "pobj" : pobj,
           "dobj" : dobj
}

logfile = open("log.txt",'w')
results = {}
# clean the file before use
logfile.truncate()
for index, review in enumerate(reviews):
    logfile.write(" ".join(["\n","--------------- Review number:",str(index + 2), "---------------"]))
    #Set the defaults for the review summary
    summary = [0,0,0]

    for word in review:
        # print(word.text, word.lemma, word.lemma_, word.tag, word.tag_, word.pos, word.pos_, word.dep, word.dep_, word.head)
        # print(word.sentiment)
        if word.pos_ in ["NOUN","PRON"]:
            featureName = word.lemma_
            if word.pos_ == "PRON":
                featureName = word.text.lower()
            if featureName in feature_list:
                #here we check for all possible patterns at the head level
                if word.dep_ in options:
                    logfile.write(" ".join(["\n",word.lemma_, word.head.lemma_,word.dep_,"head:"]))
                    opinion = options[word.dep_](word.head,featureName,logfile)
                    summary = set_opinion(results,word.lemma_,opinion,summary)
                foundADJ = False #but using amod dependency
                for child in word.children:
                    if child.dep_ == 'amod':
                        logfile.write(" ".join(["\n",word.lemma_,child.lemma_,child.dep_,"child:"]))
                        neg = check_negation(child)
                        opinion = check_orientation(child,featureName,neg,logfile)
                        summary = set_opinion(results,word.lemma_,opinion,summary)
                        foundADJ = True
                if foundADJ == False:
                    for child in word.children:  #check the conj
                        if child.dep_ == 'compound':
                            for subchild in child.children:
                                if subchild.dep_ == 'amod':
                                    logfile.write(" ".join(["\n",word.lemma_,child.lemma_,child.dep_,"child:"]))
                                    neg = check_negation(child)
                                    opinion = check_orientation(child,featureName,neg,logfile)
                                    summary = set_opinion(results,word.lemma_,opinion,summary)
                        elif child.dep_ == 'relcl':
                            logfile.write(" ".join(["\n",word.lemma_,child.lemma_,child.dep_,"child:"]))
                            neg = check_negation(child)
                            opinion = check_orientation(child,featureName,neg,logfile)
                            summary = set_opinion(results,word.lemma_,opinion,summary)
    logfile.write(" ".join(["\n","Summary:","\n    Features:",str(summary[0]),"Positive:",str(summary[1]),"Negative:",str(summary[2])]))
#Print the results
for feature, value in results.items():
    if (value[0] > 0 or value[1] > 0):
        print("%s:" % feature)
        print("    Positive opinions:",value[0])
        print("    Negative opinions:",value[1])
logfile.close()

    # nodeStatement = "MERGE (n:" + word.pos_ + " {tag: {tag}, part_of_speach: {pos}, lemma: {lemma}})"
    # session.run(nodeStatement, {"lemma": word.lemma_, "tag": word.tag_, "pos": word.pos_})
    #for subject in word.children:
        #print(subject.text)

# for word in doc:
    # depStatement = "MATCH (a:" + word.head.pos_ + "),(b:" + word.pos_ + ") WHERE a.lemma = {lemma_a} AND b.lemma = {lemma_b} MERGE (a)-[r:" + word.dep_ + " {dep: {dep}}]->(b)"
    # session.run(depStatement, {"lemma_a": word.head.lemma_, "lemma_b": word.lemma_, "dep": word.dep_})

#if word.dep != ROOT:

#session.close()
