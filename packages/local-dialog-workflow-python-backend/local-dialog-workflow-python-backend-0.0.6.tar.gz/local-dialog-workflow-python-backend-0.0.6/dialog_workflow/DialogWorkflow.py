from utils import *
from Act import action
from TablesAsObjects import DialogWorkflowRecord, Variable


def get_preferred_language(profile_id: int):
    cursor.execute("""USE profile""")
    cursor.execute("""SELECT preferred_lang_code FROM profile_view WHERE user_id = %s""", [profile_id])
    language = (cursor.fetchone())["preferred_lang_code"]
    cursor.execute("""USE dialog_workflow""")
    return language

def get_dialog_workflow_record(profile_curr_state: int, language: str):
    cursor.execute("""SELECT * FROM dialog_workflow_state_view WHERE state_id = %s AND lang_code = %s""", [profile_curr_state, language])
    optional_records = cursor.fetchall()
    random_index = random.randint(0,len(optional_records)-1)
    return DialogWorkflowRecord(optional_records[random_index])


def post_message(profile_id:  int, incoming_message: str):
    """This function is supposed to serve as a POST request later on using REST API.
    It runs until needing input from the user, which it then sends a json to the user with the message and exits
    PARAMS: 
        1. profile_id: the profile id that sent the request
        2. incoming_message: the message he sent"""
    variables = Variable()            
    profile_curr_state = get_curr_state(profile_id)
    language = get_preferred_language(profile_id)
    got_response = True #This variable indicates if we must act now as we got a response from the user or as if we should send one to him
    init_action = action(incoming_message, profile_id, language, profile_curr_state, variables)
    while True: 
        dialog_workflow_record = get_dialog_workflow_record(init_action.profile_curr_state, language)
        is_state_changed, outgoing_message = init_action.act(dialog_workflow_record, got_response)
        if outgoing_message != None:
            return outgoing_message
        init_action.profile_curr_state = dialog_workflow_record.next_state_id if is_state_changed == False else init_action.profile_curr_state
        update_profile_curr_state_in_DB(init_action.profile_curr_state, profile_id)
        got_response = False

