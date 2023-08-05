from utils import *
import time
import msvcrt
import requests
from AgeDetection import DetectAge
from TablesAsObjects import DialogWorkflowRecord, Variable, ProfileContext

class action(object):
    def __init__(self, incoming_message: str, profile_id: int, language: str, profile_curr_state: int, variables: Variable):
        self.incoming_message = incoming_message
        self.profile_id = profile_id
        self.language = language
        self.variables = variables
        self.profile_curr_state = profile_curr_state
        self.accumulated_message = ""
        self.profile = ProfileContext()
        self.variable = Variable()

    def act(self, dialog_workflow_record: DialogWorkflowRecord, got_response: bool):
        """This function applies the action of the relevant record with the profile's current state id.
        Params:
            1. dialog_workflow_record: The current record from the dialog workflow state table that is applied.
            2. got_response a bool indicator telling us if the user had sent back a response to the last outgoing message
               that we sent him from the same action or not. This will help understand if the action should 
               apply the begging part of the action (i.e to send a request to the user),
               or the second part of the action (i.e got a response and now deal with it)

        Returns:
            1. True if the action resulted in a change of state, False otherwise
            2. The outgoing message json object that the user will recieve if the action needed to send a message to the user,
                or None if the action doesn't need to send a message to the user .
        
        Note : some of the actions are divided into 2 parts: 
            1. The action before sendig the outgoing message to the user (i.e got_response = false)
            2. The action after sending the outgoing message, and getting an incoming_message reply back (i.e got_respone = true). """    
            
        self.record = dialog_workflow_record
        self.got_response = got_response
        action = self.record.workflow_action_id
        match action:
            case action_enum.LABEL_ACTION.value:
                return False, None
            case action_enum.TEXT_MESSAGE_ACTION.value:
                return self.text_message_action()
            case action_enum.QUESTION_ACTION.value:
                return self.question_action()
            case action_enum.JUMP_ACTION.value:
                return self.jump_action()
            case action_enum.SEND_REST_API_ACTION:
                return self.send_rest_api_action()
            case action_enum.ASSIGN_VARIABLE_ACTION.value:
                return self.assign_variable_action()
            case action_enum.INCREMENT_VARIABLE_ACTION.value:
                return self.increment_variable_action()
            case action_enum.DECREMENT_VARIABLE_ACTION.value:
                return self.decrement_variable_action()
            # case action_enum.CONDITION_ACTION.value:
            #     return condition_action(record)
            case action_enum.MENU_ACTION.value:
                return self.menu_action()
            case action_enum.AGE_DETECTION.value:
                return self.age_detection()
            case action_enum.MULTI_CHOICE_POLL.value:
                return self.multi_choice_poll()
            case action_enum.PRESENT_CHILD_GROUPS_NAMES_BY_ID.value:
                return self.present_child_groups_names_by_id()   
            case action_enum.PRESENT_GROUPS_WITH_CERTAIN_TEXT.value:
                return self.present_groups_with_certain_text()     
            case action_enum.INSERT_MISSING_DATA.value:
                return self.insert_missing_data()                
                                 
            
    def text_message_action(self):
        """Prints the paramter1 message after formatting: 
        "Hello {First Name}, how are you {feeling|doing}?" --> "Hello Tal, how are you doing? """
        message = self.record.parameter1
        replace_fields_with_values_class = replace_fields_with_values(message, self.language, self.variable)
        formatted_message = replace_fields_with_values_class.get_variable_values_and_chosen_option()
        self.accumulated_message = self.accumulated_message + formatted_message + '~'
        return False, None

    def question_action(self):
        """Asks a question and waits for an answer from user on STDIN. If the user responded in a certain amount of time,
        then moves to next state, otherwise moves to a different state.
        Note: this function waits for input for a certain amount of time only if using console application.
              If using websocket we send a json message to the user and exit the code normally"""

        if not self.got_response:
            self.accumulated_message += self.record.parameter1
            outgoing_message = process_message(communication_type= COMMUNICATION_TYPE, action_type= action_enum.TEXT_MESSAGE_ACTION.value, message= self.accumulated_message) 
            if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
                return False, outgoing_message
            else:
                self.accumulated_message = ""
            
            waiting_time = self.record.no_feedback_milliseconds 
            start_time = time.monotonic()
            input_str = None
            while True:
                if msvcrt.kbhit():
                    input_str = input().strip()
                    insert_profile_variable_value(self.profile_id, self.record.variable1_id, input_str, self.profile_curr_state)
                    break
                elif time.monotonic() - start_time > waiting_time:
                    break
            if input_str == None:
                self.profile_curr_state = self.record.next_state_id_if_there_is_no_feedback
                return True, None
            else:
                return False, None
        else:
            insert_profile_variable_value(self.profile_id, self.record.variable1_id, self.incoming_message, self.profile_curr_state)
            return False, None
               
    def jump_action(self):
        """Jumps from one state to another."""
        self.profile_curr_state = int(self.record.parameter1)
        update_profile_curr_state_in_DB(self.profile_id, int(self.record.parameter1))
        return True, None

    def send_rest_api_action(self):
        """Sends a REST API post"""
        api_url = self.record.parameter1
        payload_variable_id = self.record.variable1_id
        json_payload_string = get_variable_value_by_id(self.language, payload_variable_id)
        json_payload = json.loads(json_payload_string)
        incoming_message = requests.post(api_url, json=json_payload)
        incoming_message_string = json.dumps(incoming_message.json())
        insert_profile_variable_value(self.profile_id, self.variable.get_variable_id("Post Result"), incoming_message_string, self.profile_curr_state)
        return False, None

    def assign_variable_action(self):
        """Assigns a value to a given variable"""
        parameter_value = self.record.parameter1
        variable_id = self.record.variable1_id
        insert_profile_variable_value(self.profile_id, variable_id, parameter_value, self.profile_curr_state)
        return False, None

    def increment_variable_action(self):
        """Increments a value to a given variable by the amount of the given paramter1"""
        number_to_add = int(self.record.parameter1)
        variable_id = self.record.variable1_id
        current_variable_value = get_variable_value_by_id(self.language, variable_id)
        insert_profile_variable_value(self.profile_id, variable_id, str(int(current_variable_value) + number_to_add), self.profile_curr_state)
        return False, None

    def decrement_variable_action(self):
        """Increments a value to a given variable by the amount of the given paramter1"""
        number_to_add = int(self.record.parameter1)
        variable_id = self.record.variable1_id
        current_variable_value = get_variable_value_by_id(self.language, variable_id)
        insert_profile_variable_value(self.profile_id, variable_id, str(current_variable_value - number_to_add), self.profile_curr_state)
        return False, None

    """I have put this in remark right now because this action need to work with multiple profiles,
    But right now this change makes it difficult to do that. Will work on it later."""
    # def condition_action(self):
    #     cursor.execute("""SELECT * FROM dialog_workflow_state  WHERE parent_state_id = %s""", [record.curr_state_id])
    #     child_nodes = cursor.fetchall()
    #     """I am assuming that in these child records the varaible id must be the same id of the parent variable id, 
    #     and the parameter1 value is the value of a profile_id from which i shall get the age"""
    #     for child in child_nodes:
    #         profile_id = child["parameter1"] 
    #         child_age = (profiles_dict_class.get(profile_id)).get_variable_value_by_id(record.variable1_id)
    #         if child_age < record.result_figure_max and child_age > record.result_figure_min:
    #             profile.curr_state_id = child["next_state_id"]
    #             return True, None
    #     return False, None

    def menu_action(self):
        """This action show a menu of options to the user for which he should choose one from it.
            the options we show are the records such that their parent id is the id of the current record.
            First part of the action is sending the user the options.
            Second part of the action is getting the chosen option (i.e incoming_message) and dealing with it."""
        fields_to_select = ["parameter1", "next_state_id"]
        table_name = "dialog_workflow_state_view"
        values_from_where_to_select = [self.record.curr_state_id]
        variables_from_where_to_select = ["parent_state_id"]
        child_nodes = get_child_nodes_of_current_state(fields_to_select, table_name, values_from_where_to_select, variables_from_where_to_select)
        self.record.parameter1 = "" if self.record.parameter1 == None else self.record.parameter1
        if not self.got_response: #Adds the question and instructions to the accumulated_message to be sent to user.
            self.accumulated_message = self.accumulated_message + self.record.parameter1 +"~" + f"Please choose EXACTLY ONE option between 1-{len(child_nodes)}:~"
        is_state_changed, next_state_id, outgoing_message = generic_user_choice_action(self.record, self.accumulated_message, child_nodes, choose_exactly_one_option=True, got_response=self.got_response, chosen_numbers=self.incoming_message, profile=self.profile)
        if outgoing_message != None: #returns the outgoing message to send to the user.
            return False, outgoing_message
        self.profile_curr_state = next_state_id
        self.accumulated_message = ""
        return is_state_changed, None
        
    def age_detection(self):
        """Action that recieves a path to a picture (for now the picture has to be stored in the folder) 
            and returns the approximate age of the person in the picture.
            Stores the picture in database storage."""
        if not self.got_response:
            self.accumulated_message += "Please insert a path to the picture~"
            outgoing_message = process_message(communication_type= COMMUNICATION_TYPE, action_type= action_enum.AGE_DETECTION.value, message= self.accumulated_message) 
            if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
                return False, outgoing_message
            else:
                self.accumulated_message = ""         
                self.incoming_message = input()
        age_range = DetectAge.detect(self.incoming_message)
        self.accumulated_message += f'The approximate age of the picture you have sent is: {age_range}~'
        insert_profile_variable_value(self.profile_id, self.record.variable1_id, age_range, self.profile_curr_state)
        store_age_detection_picture(age_range, self.profile_curr_state)
        return False, None
    
    def multi_choice_poll(self):
        """ Similar to Menu Action. If the user chose a single option we jump to next_state_id of the chosen option. 
            Otherwise we save the answers and jump to the next_state_id of the parent."""
        fields_to_select = ["parameter1", "next_state_id"]
        table_name = "dialog_workflow_state_view"
        values_from_where_to_select = [self.record.curr_state_id]
        variables_from_where_to_select = ["parent_state_id"]
        child_nodes = get_child_nodes_of_current_state(fields_to_select, table_name, values_from_where_to_select, variables_from_where_to_select)
        self.record.parameter1 = "" if self.record.parameter1 == None else self.record.parameter1
        if not self.got_response: #Adds the question and instructions to the accumulated_message to be sent to user.
            self.accumulated_message = self.accumulated_message + self.record.parameter1 +"~" + f"Please select your desired choices, You may select any of the numbers between 1-{len(child_nodes)} with a comma seperator between each choice:~"        
        is_state_changed, next_state_id, outgoing_message = generic_user_choice_action(self.record, self.accumulated_message, child_nodes, choose_exactly_one_option=False, got_response=self.got_response, chosen_numbers=self.incoming_message, profile=self.profile)
        if outgoing_message != None: #returns the outgoing message to send to the user.
            return False, outgoing_message
        self.profile_curr_state = next_state_id
        return is_state_changed, None

    def present_child_groups_names_by_id(self):
        """Presents all of the groups that their parent id is the given one. Does so recursively"""
        child_groups = group(int(self.record.parameter1))
        self.accumulated_message += "Here are the interests:~" + ", ".join(child_groups.get_child_group_names()) + "~"
        return False, None
    
    def present_groups_with_certain_text(self):
        """Present all groups that their text contains the given text. (e.g given text: 'sport' -> 'sports', 'walking sport..).
            Saves the chosen options in profile context."""
        groups = get_groups_with_text(self.record.parameter1)
        if not self.got_response:
            self.accumulated_message += "Please choose your desired interests. You may select more than one choice with a comma seperator.~"
            for i, child in enumerate(groups):
                self.accumulated_message = self.accumulated_message + f'{i+1}) {child["title"]}~'            
            
            outgoing_message = process_message(communication_type= COMMUNICATION_TYPE, action_type= action_enum.PRESENT_GROUPS_WITH_CERTAIN_TEXT.value, message=self.accumulated_message) 
            if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
                return False, outgoing_message 
            else:
                self.accumulated_message = ""
                chosen_numbers = input()          
        else:
                chosen_numbers = self.incoming_message.split(',')
                chosen_numbers_list = [int(x) for x in chosen_numbers]
                self.profile.groups.extend([groups[chosen_number] for chosen_number in chosen_numbers_list])
        return False, None

    def insert_missing_data(self):
        """Asks the user for missing data (e.g please insert your first name), and after getting a response,
            inserts the given value to the relevant table to fill the missing data.
            The record, field name, table and scehma in which the data should be inserted into are given in parameter1 as:
            <schema>,<table>,<field name>,<record id> (e.g. user,user_table,first_name,1)"""
        parameter1_list = self.record.parameter1.split(",")
        schema = parameter1_list[0]
        table = parameter1_list[1]
        field_name = parameter1_list[2]
        record_id = parameter1_list[3]
        if not self.got_response:
            self.accumulated_message += f"Please insert your {field_name}~"
            outgoing_message = process_message(communication_type= COMMUNICATION_TYPE, action_type= action_enum.TEXT_MESSAGE_ACTION.value, message= self.accumulated_message) 
            if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
                return False, outgoing_message
            else:
                self.accumulated_message = ""
                self.incoming_message = input()            
        else:
            try:
                cursor.execute(f"""USE {schema}""")
                cursor.execute(f"""UPDATE {table} SET {field_name} = '{self.incoming_message}' WHERE (id= {record_id})""")
                cursor.execute("""USE dialog_workflow""")
                connection.commit()
            except: #If one of the arguments isn't valid
                print("Invalid parameter1")
        return False, None


def generic_user_choice_action(record: DialogWorkflowRecord, accumulated_message: str, child_nodes: list, choose_exactly_one_option : bool, got_response: bool, chosen_numbers: str, profile: ProfileContext):
    """Sends the user a question with a couple of answers. This function is generic and can let the user choose either
        exactly one option, or more than one. Each case is handeled differently.
        Returns: 
            1. True if the users' next state should be changed to a child next state, False if there's no need to change it's state
            2. The next state id that the profile should be in, or None if the action didn't result in a change of state.
            3. The outging message to be sent to the user, or None if the message had already been sent."""
    # This is the first part of the action: sending the request to the user and waiting for an answer.
    if not got_response:
        for i, child in enumerate(child_nodes):
            accumulated_message = accumulated_message + f'{i+1}) {child["parameter1"]}~'
        outgoing_message = process_message(communication_type= COMMUNICATION_TYPE, action_type= action_enum.TEXT_MESSAGE_ACTION.value, message= accumulated_message) 
        if COMMUNICATION_TYPE == communication_type_enum.WEBSOCKET.value:
            return False, record.next_state_id, outgoing_message 
        else:
            chosen_numbers = input()


    # The user has to pick exactly one option
    if choose_exactly_one_option:
        profile_next_state = (child_nodes[int(chosen_numbers)-1])["next_state_id"]
        return True, profile_next_state, None
    # In this case the user can choose more than one option: 
    else:
        chosen_numbers = chosen_numbers.split(',')
        chosen_numbers_list = [int(x) for x in chosen_numbers]
        # If he still chooses exactly one we jump to the next_state_id of the option.
        if len(chosen_numbers_list) == 1: 
            profile_next_state = (child_nodes[chosen_numbers_list[0]-1])["next_state_id"]
            return True, profile_next_state, None
        # If he chooses more than one, we store the chosen options and jump to the next_state_id of the parent.    
        else:
            list_of_options = [option["parameter1"] for option in child_nodes]
            profile.save_chosen_options(record.parameter1, record.variable1_id, chosen_numbers_list, list_of_options)
            return False, record.next_state_id, None

def get_groups_with_text(text: str) -> list[str]:
    cursor.execute("""USE `group`""")
    cursor.execute(f"""SELECT title, group_id FROM group_ml_table WHERE title LIKE '%{text}%'""")
    return cursor.fetchall()
