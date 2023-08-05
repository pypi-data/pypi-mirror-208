from dialog_workflow.Constants import *
from dialog_workflow.utils import insert_profile_variable_value, get_curr_state, get_variable_value_by_id

class Variable(object):
    def __init__(self):
        self.name2id_dict = {}
        self.id2name_dict = {}
        self.next_variable_id = 1
        for variable_id in VARIABLE_NAMES_DICT:
            self.add(variable_id, VARIABLE_NAMES_DICT[variable_id])

    def add(self, variable_id : int, variable_name : str):
        try:
            self.name2id_dict[variable_name] = variable_id
            self.id2name_dict[variable_id] = variable_name
            cursor.execute("""INSERT INTO variable_table(id, name) VALUES (%s, %s)""", [variable_id, variable_name])
            connection.commit()

        except:
            """TODO: add error to logger"""
            
    def get_variable_id(self, variable_name : str):
        return self.name2id_dict[variable_name]
    
    def get_variable_name(self, variable_id : int):
        return self.id2name_dict[variable_id]

    def get_variable_value_by_name(self, language: str, variable_name : str) -> str:
        variable_id = self.get_variable_id(variable_name)
        return get_variable_value_by_id(self, language, variable_id)
    
class ProfileContext (object):
    def __init__(self):
        self.dict = {}
        self.profile_id = ACTIVE_PROFILE_ID
        self.chosen_poll_options = {}
        self.curr_state_id = get_curr_state(self.profile_id)
        self.variables = Variable()
        self.groups = []

    def get_variable_value_by_id(self, variable_id : int) -> str:
        return self.dict[variable_id]
    
    def save_chosen_options(self, question_asked: str, variable_id: int, chosen_numbers_list: list[int], list_of_options: list[str]):
        """Saves the options chosen by the user in the multi_choice_poll action in a dict with the question as the key
            and a list of the options chosen as the value i.e: {<question asked> : [<chosen option 1>, <chosen option 2>..]}
            Also saves the chosen options in the database."""
        self.chosen_poll_options[question_asked] = [list_of_options[chosen_option-1] for chosen_option in chosen_numbers_list]
        variable_value_to_insert = question_asked + " "
        for chosen_option in self.chosen_poll_options[question_asked]:
            variable_value_to_insert = variable_value_to_insert + str(chosen_option) + ", "
        insert_profile_variable_value(self.profile_id, variable_id, variable_value_to_insert, self.curr_state_id)

    def get_variable_value_by_name(self, variable_name : str) -> str:
        return self.get_variable_value_by_id(self.variables.get_variable_id(variable_name))

    def set(self, variable_id : int, variable_value : str):
        self.dict[variable_id] = variable_value
        cursor.execute("""USE logger""")
        cursor.execute("""INSERT INTO logger
                        (profile_id, state_id, variable_id, variable_value_new) 
                        VALUES (%s,%s,%s,%s)""", 
                        (self.profile_id, self.curr_state_id, variable_id, variable_value))
        cursor.execute("""USE dialog_workflow""")
        connection.commit()

class ProfilesDict(object):
    def __init__(self):
        self.profiles_dict = {}

    def add(self, profile : ProfileContext):
        self.profiles_dict[profile.profile_id] = profile

    def get(self, profile_id : int) -> ProfileContext:
        return None if profile_id not in self.profiles_dict else self.profiles_dict[profile_id]

class DialogWorkflowRecord(object):
    def __init__(self, record):
        self.curr_state_id : int = record["state_id"]
        self.parent_state_id : int = record["parent_state_id"]
        self.workflow_action_id : int = record["workflow_action_id"]
        self.lang_code = record["lang_code"]
        self.parameter1 = record["parameter1"]
        self.variable1_id : int= record["variable1_id"]
        self.result_logical = record["result_logical"]
        self.result_figure_min : float = record["result_figure_min"]
        self.result_figure_max : float = record["result_figure_max"]
        self.next_state_id : int = record["next_state_id"]
        self.no_feedback_milliseconds : float = record["no_feedback_milliseconds"]
        self.next_state_id_if_there_is_no_feedback  : int = record["next_state_id_if_there_is_no_feedback"]

