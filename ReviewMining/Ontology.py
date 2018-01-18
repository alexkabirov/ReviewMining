from owlready2 import *
onto = get_ontology("file://Features.owl").load()
with onto:
    class Feature(Thing):
        #check if string is equal to the name of the current feature or any of it synonyms
        def get_by_name(self,name):
            if self.name == name:
                return True
            for synonym in self.has_for_synonym:
                if synonym == name:
                    return True
            return False
        def check_exception(self,word):
            for exception in self.has_exceptions:
                if exception.name == word:
                    return exception.exception_orientation[0]
            return 0

    class Phone(Thing):
        #Get the list of all features
        def all_features_with_syn(self):
            #for the future notice - it is a shallow copy: all_features = self.has_features
            all_features = []
            for feature in self.has_features:
                all_features.append(feature.name)
                for synonym in feature.has_for_synonym:
                    all_features.append(synonym)
            return all_features
        #return the feature object by name, including synonyms
        def feature_by_name(self,name):
            #check the name directly first, then go for synonyms
            for feature in self.has_features:
                if feature.get_by_name(name) == True:
                    return feature

    class Feature_Exception(Thing):
        pass
    class has_features(Thing >> Thing):
        pass
    class has_for_synonym(Thing >> str):
        pass
    class exception_orientation(Feature_Exception >> int):
        pass
    class has_exceptions(Feature >> str):
        pass
#------------------------------
# The following code should go in the implementation normally, here we put ir for the demo purposes
#define Feature instances:
phone = Feature("phone")
screen = Feature("screen")
battery = Feature("battery")
camera = Feature("camera")
processor = Feature("processor")
memory = Feature("memory")
sensor = Feature("sensor")
speaker = Feature("speaker")
scanner = Feature("scanner") #fingerprint scanner
NFC = Feature("NFC")
connectivity = Feature("connectivity")
antenna = Feature("antenna")
button = Feature("button")
size = Feature("size") # can be standalone
weight = Feature("weight") # can be standalone
style = Feature("style")
interface = Feature("interface")
functionality = Feature("functionality")
durability = Feature("durability")
speed = Feature("speed")
application = Feature("application")
navigation = Feature("navigation")
slot = Feature("slot") #SIM slot, SD card slot etc.
card = Feature("card") #SIM card
earphones = Feature("earphone")
charger = Feature("charger")
case = Feature("case")
price = Feature("price")
value = Feature("value")
pronoun = Feature("it")
#Define synonyms for the features
screen.has_for_synonym = ["display","glass"]
camera.has_for_synonym = ["picture","photo","video"]
phone.has_for_synonym = ["smartphone","item","product","handset"]
processor.has_for_synonym = ["performance","speed"]
memory.has_for_synonym = ["storage","space"]
interface.has_for_synonym = ["UI","UX","OS"]
button.has_for_synonym = ["key"]
connectivity.has_for_synonym = ["wifi","wi-fi","internet"]
antenna.has_for_synonym = ["signal"]
application.has_for_synonym = ["app","program","software"]
scanner.has_for_synonym = ["reader","recognition"]
speaker.has_for_synonym = ["sound"]
earphones.has_for_synonym = ["headphone"]
navigation.has_for_synonym = ["GPS"]
charger.has_for_synonym = ["charge"]
style.has_for_synonym = ["design","look"]
speed.has_for_synonym = ["responsiveness"]
#Define exceptions for the Features
delicate = Feature_Exception("delicate")
delicate.exception_orientation = [-1] #negative
negligible = Feature_Exception("negligible")
negligible.exception_orientation = [-1]
average = Feature_Exception("average")
average.exception_orientation = [-1]
mediocre = Feature_Exception("mediocre")
mediocre.exception_orientation = [-1]
steep = Feature_Exception("steep")
steep.exception_orientation = [-1]
high = Feature_Exception("high")
high.exception_orientation = [-1]
expensive = Feature_Exception("expensive")
expensive.exception_orientation = [-1]
quick = Feature_Exception("quick")
quick.exception_orientation = [1]
slow = Feature_Exception("slow")
slow.exception_orientation = [-1]
#assign exceptions to features
screen.has_exceptions = [delicate,average,mediocre]
camera.has_exceptions = [average,mediocre]
battery.has_exceptions = [average,mediocre]
speaker.has_exceptions = [average,mediocre]
antenna.has_exceptions = [negligible,average,mediocre]
connectivity.has_exceptions = [negligible,average,mediocre]
price.has_exceptions = [steep,high,expensive]
phone.has_exceptions = [expensive,quick,slow,average,mediocre]
connectivity.has_exceptions = [slow,negligible,average,mediocre]
#Create a instance of the Phone (Product) class
smartphone = Phone("smartphone")
#Assign the features to the smartphone instance
smartphone.has_features = [phone,screen,battery,camera,processor,memory,sensor,speaker,scanner,NFC,connectivity,antenna,button,size,weight,style,interface,functionality,durability,speed,navigation,slot,card,earphones,charger,case,price,value,pronoun]
#Set the list of alll features
#rint(smartphone.has_features[phone])
feature_list = smartphone.all_features_with_syn()
#for feature in feature_list:
#    print(feature)
onto.save()
