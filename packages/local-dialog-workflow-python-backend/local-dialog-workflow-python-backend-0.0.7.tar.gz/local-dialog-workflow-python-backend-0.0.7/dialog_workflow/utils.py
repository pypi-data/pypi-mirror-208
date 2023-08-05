# TODO: Let's talk about Constants and the usage in this file
from Constants import *
import random
import json
from circles_local_aws_s3_storage_python.AWSStorage import AwsS3Storage

# TOOD: Please include type to all parameters.
# TODO: Please include return value.
# TODO: Please add short documentation per PEP8 standard

# TODO:Let's move to Object Oriented Programming

def get_variable_value_by_id(language: str, variable_id : int) -> str:
    cursor.execute("""SELECT variable_value_new FROM dialog_workflow_state_history_view WHERE variable_id= %s ORDER BY timestamp DESC""", [variable_id])
    return (cursor.fetchone())["variable_value_new"]

class replace_fields_with_values(object):
    def __init__(self, message, language: str, variable):
        self.message = message
        self.language = language
        self.variable = variable

    def choose_option(self, message_index : int, first_param: str):
        """ Gets a messsage, an index of the first apearance of '|' , and the first parameter of the options
            Returns:
            1. One of the options randomly selected
            2. The index of one char after the next '}'"""
        list_of_params = [first_param]
        while(self.message[message_index] != '}'):
            next_param = ""
            while(self.message[message_index] != '|' and self.message[message_index] != '}'):
                next_param = next_param + self.message[message_index]
                message_index = message_index + 1
            list_of_params.append(next_param)
            message_index = message_index + 1 if self.message[message_index] != '}' else message_index
        random_index = random.randint(0, len(list_of_params)-1)
        return list_of_params[random_index], message_index + 1

    """For the following function to work the message must not have single '{' or '}'. They should always come in pairs"""
    def get_variable_names_and_chosen_option(self):
        """Returns:
            1. A list of all variable names that were inside curly braces of message
            2. A string that's a copy of the message but without the variable names inside curly braces,
            and a randomly chosen parameter out of each curly braces options:
            "Hello {First Name}, how are you {feeling|doing}?" --> "Hello {}, how are you doing?" 
        """
        variable_names_list = []
        message_without_variable_names = ""
        message_index = 0
        while message_index < len(self.message):
            index_after_choosing_option = None
            if(self.message[message_index] == '{'):
                message_index = message_index + 1
                next_variable_name = ""
                chosen_parameter = None
                while self.message[message_index] != '}':
                    if self.message[message_index] == '|':
                        chosen_parameter, index_after_choosing_option = self.choose_option(message_index+1, next_variable_name)
                        break
                    next_variable_name = next_variable_name + self.message[message_index]
                    message_index = message_index + 1
                if chosen_parameter != None:
                    message_without_variable_names = message_without_variable_names + chosen_parameter
                else:
                    message_without_variable_names = message_without_variable_names + "{}"
                    variable_names_list.append(next_variable_name)
            else:
                message_without_variable_names = message_without_variable_names + self.message[message_index]
            message_index = message_index + 1 if index_after_choosing_option == None else index_after_choosing_option
        return variable_names_list, message_without_variable_names

    def get_variable_values_and_chosen_option(self):
        """Returns:
            1. A list of all variable values by variable names that were inside curly braces of message 
            2. A string that's a copy of the message but without the variable names inside curly braces
            and a randomly chosen parameter out of each curly braces options:
            "Hello {First Name}, how are you {feeling|doing}?" --> "Hello {}, how are you doing?"
        """
        variable_names_list, message_without_variable_names = self.get_variable_names_and_chosen_option()
        variable_value_list = []
        for variable_name in variable_names_list:
            variable_id = self.variable.get_variable_id(variable_name)
            variable_value = get_variable_value_by_id(self.language, variable_id)
            variable_value_list.append(variable_value)    
        return message_without_variable_names.format(", ".join(variable_value_list))


def process_message(communication_type : int, action_type : int, message : str):
    """Processes message according to which communication_type is used: console or websocket
        If console then we continue the code normally.
        If websocket then we create a json out of the given message and exit(0)"""
    if communication_type == communication_type_enum.CONSOLE.value:
        message = message.replace('~', '\n')
        print(message)
        return None
    if communication_type == communication_type_enum.WEBSOCKET.value:
        return update_json_message(action_type, message)

def update_json_message(action_type: int, message: str) -> json:
    """Update message to json format"""
    json_message = {"message": message}
    if action_type == action_enum.AGE_DETECTION.value:
        json_message["type"] = "command"
    else:
        json_message["type"] = "text"
    json_dumps = json.dumps(json_message)  
    return json_dumps.replace('~', '\n')

def update_profile_curr_state_in_DB(new_state: int, profile_id):
    """This function updates the last_dialog_workflow_state_id in the profile table to the new state.
       Note that this function UPDATES the field sand doesn't INSERT into the table. """
    cursor.execute("""USE profile""")
    cursor.execute("""UPDATE profile_table SET last_dialog_workflow_state_id = %s WHERE (user_id= %s)""", [new_state, profile_id])
    cursor.execute("""USE dialog_workflow""")
    connection.commit()

def insert_profile_variable_value(profile_id: int, variable_id : int, variable_value : str, profile_curr_state: int):
    """This function inserts a variable value into the logger table for a given profile"""
    cursor.execute("""USE logger""")    
    cursor.execute("""INSERT INTO logger_table
                    (profile_id, state_id, variable_id, variable_value_new) 
                    VALUES (%s,%s,%s,%s)""", 
                    (profile_id, profile_curr_state, variable_id, variable_value))
    cursor.execute("""USE dialog_workflow""")
    connection.commit()

def store_age_detection_picture(age_range: str, profile_id: int):
    """Stores the picture in Nir's storage schema, gets a storage_id and inserts into the computer_vision_storage_table"""
    storage = AwsS3Storage(bucket_name="storage.us-east-1.dvlp1.bubblez.life", region="us-east-1")
    storage_id = storage.upload_file("C:\\Users\\User\\OneDrive\\Circles\\age-detection-backend\\src\\alonPicture.png", "Alon's picture", "", 1)
    
    age_range_split = age_range.split('-')
    min_age = int(age_range_split[0][:len(age_range_split[0])-1])
    max_age = int((age_range_split[1])[1:])
    cursor.execute("""USE computer_vision_storage""")
    cursor.execute("""INSERT INTO computer_vision_storage_table 
                    (storage_id, profile_id, min_age, max_age) VALUES (%s, %s, %s, %s)""", 
                   [storage_id, profile_id, min_age, max_age])
    connection.commit()

def get_curr_state(profile_id: int):
    """Returns profiles' curernt state number"""
    cursor.execute("""USE profile""")
    cursor.execute("""SELECT last_dialog_workflow_state_id FROM profile_view WHERE user_id = %s ORDER BY id DESC""", [profile_id])
    curr_state = int((cursor.fetchone())["last_dialog_workflow_state_id"])
    cursor.execute("""USE dialog_workflow""")
    return curr_state

def get_child_nodes_of_current_state(fields : list[str], table_name : str, values_from_where_to_select : list[any], variables_from_where_to_select : list[str]):
    """Recieves all of the relevant information and selects the child nodes of the current state from the given table, and returns them"""
    sql_query = "SELECT " + ", ".join(fields) + " FROM " + table_name + " WHERE "
    # Add the variables and values to the SQL query
    for i in range(len(variables_from_where_to_select)):
        sql_query += variables_from_where_to_select[i] + " = %s"
        if i != len(variables_from_where_to_select) - 1:
            sql_query += " AND "
    cursor.execute(sql_query, values_from_where_to_select)
    return cursor.fetchall()

class group(object):
    def __init__(self, parameter1):
        self.parameter1 = parameter1
            
    def get_group_childs_id_bellow_parent_id(self) -> list[int]:  
        """returns all of the childs ids below the given parent_id.
            This funcrion gets all of the id's of records that their parent_state_id is the given id, and continues to add id's  recursively 
            until all of the records that their parent_state_id matches an id in the table."""
        cursor.execute("""USE `group`""")
        cursor.execute("""WITH RECURSIVE cte AS (
            SELECT group_view.id FROM group_view WHERE id = %s
            UNION ALL
            SELECT group_view.id FROM group_view 
            JOIN cte ON group_view.parent_group_id = cte.id
        )
        SELECT * FROM cte""", [self.parameter1])  
        group_id_dict = cursor.fetchall()
        return [group['id'] for group in group_id_dict]

    def get_child_group_names(self) -> list[str]:
        """Gets all of the child title names from the ml table of the given parent_id."""
        group_ids = self.get_group_childs_id_bellow_parent_id()
        group_id_string = ','.join(str(id) for id in group_ids)
        cursor.execute(f"SELECT title FROM group_ml_en_view WHERE group_id IN ({group_id_string}) ")
        group_name_dict = cursor.fetchall()
        return [group['title'] for group in group_name_dict]
    
    # def get_child_group_id(self) -> list[int]:
    #     """Gets the id of all the records with the given group name"""
    #     cursor.execute("""USE `group`""")
    #     cursor.execute("""SELECT group_id from group_ml_en_view WHERE title = %s""", [self.parameter1])
    #     group_id_dict = cursor.fetchall()
    #     return [group['group_id'] for group in group_id_dict]        

