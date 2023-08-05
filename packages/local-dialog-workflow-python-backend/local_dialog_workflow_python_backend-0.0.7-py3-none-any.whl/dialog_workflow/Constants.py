from enum import Enum
from circles_local_database_python.database import database
from dotenv import load_dotenv
load_dotenv()

class action_enum(Enum):
    LABEL_ACTION = 1
    TEXT_MESSAGE_ACTION = 2
    QUESTION_ACTION = 3
    JUMP_ACTION = 4
    SEND_REST_API_ACTION = 5    
    ASSIGN_VARIABLE_ACTION = 6
    INCREMENT_VARIABLE_ACTION = 7
    DECREMENT_VARIABLE_ACTION = 8
    CONDITION_ACTION = 9
    MENU_ACTION = 10
    AGE_DETECTION = 11
    MULTI_CHOICE_POLL = 12
    PRESENT_CHILD_GROUPS_NAMES_BY_ID = 13
    PRESENT_GROUPS_WITH_CERTAIN_TEXT = 14
    INSERT_MISSING_DATA = 15

class communication_type_enum(Enum):
    CONSOLE = 1
    WEBSOCKET = 2
COMMUNICATION_TYPE = 2

VARIABLE_NAMES_DICT = {1 : "Person Id" , 2 : "User Id", 3 : "Profile Id", 4 : "Lang Code", 
                       5 : "Name Prefix", 6 : "First Name", 7 : "Middle Name" , 
                       8 : "Last Name", 9 : "Name Suffix",  10 : "Full Name", 
                       11 : "Country", 12 : "State" , 13 : "County" , 14 : "City", 
                       15 : "Neighborhood", 16 : "Street", 17 : "House", 18 : "Suite/Apartment", 
                       19 : "Zip Code", 20 : "Post Result", 21 : "Age", 22 : "Result"}

ACTIVE_PROFILE_ID  = 1
connection = database().connect_to_database()
cursor = connection.cursor(dictionary=True, buffered=True)
cursor.execute("""USE dialog_workflow""")
