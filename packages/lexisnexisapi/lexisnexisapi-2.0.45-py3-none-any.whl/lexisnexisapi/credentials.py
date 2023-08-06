import json
import os
 
def set_Key(**kwargs):
    '''
    Send kwargs to be stored as JSON object
    '''
    cred = get_Credentials()
    cred.update(kwargs)
    f=json_file_path()
    with open(f,"w") as outfile:
        json.dump(cred, outfile, indent=4)
def get_Key(key):
    '''
    Send parameter 'key' to return value lf 'key':'value' from myCredentials JSON object.
    '''
    cred = get_Credentials()
    if key in get_Credentials():
        v = cred[key]
    else:
        print(f'the key {a} does not exist yet, use credentials.set_Key({a}=yourkey) to set the key value')
        v=""
    return v
def get_Credentials():
    '''
    get all credentials from myCredentials JSON object.
    '''
    check_file_exists()
    f=json_file_path()
    with open(f,"r") as outfile:
        dict = json.load(outfile)
    return dict
def blank_Credentials():
    '''
    set myCredentials JSON object with each key having a value as blank('')
    '''
    dict={
          "Metabase_Search_Key": "",
          "Metabase_Filters_Key": "",
          "Metabase_Portal_UN": "",
          "Metabase_Portal_PW": "",
          "WSAPI_client_id": "",
          "WSAPI_secret": ""
         }
    return dict
def check_file_exists():
    '''
    ensures the JSON object exists, if not it creates a blank JSON object
    '''
    from os.path import exists
    f=json_file_path()
    file_exists = exists(f)
    if not file_exists:
        with open(f, "w") as outfile:
            json.dump(blank_Credentials(),outfile)
def json_file_path():
    '''
    shows path where JSON object is to be stored
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    json_file_name = 'myCredentials.json'
    json_file_path = os.path.join(path,json_file_name)
    return json_file_path
    

        
        