import firebase_admin
import pandas as pd
from firebase_admin import firestore,_apps,credentials
def connect(json):
    if not _apps:
        cred=credentials.Certificate(json)
        firebase_admin.initialize_app(cred)
connect("pp.json")
def selectallfromcollection(kalyan):
    if _apps:
        cursor=firestore.client()
        stream=cursor.collection(kalyan).stream()
        list=[]
        for i in stream:
            list.append(i.to_dict())
        p=pd.DataFrame(list)
        print(p)
selectallfromcollection('kalyan')
