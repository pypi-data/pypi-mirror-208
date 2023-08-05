import sys
# sys.path.append("C:\\Users\\User\\OneDrive\\Circles\\dialog-workflow-backend")
import unittest
from TablesAsObjects import *
from DialogWorkflow import *
from Constants import *

"""Please make sure to fill al the relevant data in the database in order for the tests to run correctly"""
class TestVariable(unittest.TestCase):
    def setUp(self):
        self.variables = Variable() 

    def test_add(self):
        self.variables.add("Test Name 5", 5)
        self.assertEqual(self.variables.name2id_dict["Test Name 5"], 5)
        self.assertEqual(self.variables.id2name_dict[5], "Test Name 5")
    
    def test_get_variable_id(self):
        self.variables.add("Test Name", 5)
        variable_id = self.variables.get_variable_id("Test Name")
        self.assertEqual(variable_id, 5)
    
    def test_get_variable_name(self):
        self.variables.add("Test Name", 5)
        variable_name = self.variables.get_variable_name(5)
        self.assertEqual(variable_name, "Test Name")

class TestProfileContext(unittest.TestCase):
    def setUp(self):
        self.profile_context = ProfileContext()
    
    def test_get_variable_value(self):
        self.assertEqual(self.profile_context.get_variable_value(101), "Tal")


class TestDialogWorkflowRecord_AND_Actions(unittest.TestCase):
    def setUp(self):
        self.record_dict = {"id":1, "state_id":1, "lang_code":"en", "variable2_id":None, "result_logical" : None, "result_figure_min":None, "result_figure_max":None, "next_state_id":2 ,"no_feedback_milliseconds":None, "next_state_id_if_there_is_no_feedback":2, "version":1, "checked_in":0, "remark":None}
        self.action = action(None, 1, 'en', 1, Variable())
        cursor.execute("""SELECT * FROM dialog_workflow_state_table WHERE workflow_action_id = %s""", [action_enum.MULTI_CHOICE_POLL.value])
        record = cursor.fetchone()
        self.action.record = DialogWorkflowRecord(record)
        self.action.got_response = True

    def test_text_message_action(self):
        self.record_dict["workflow_action_id"] = 2
        self.record_dict["parameter1"] = "Hello, how are you?"
        self.record_dict["variable1_id"] = 6
        self.action.record = DialogWorkflowRecord(self.record_dict)

        self.action.text_message_action(self.action.record)
        self.assertEqual(self.action.accumulated_message, "Hello, how are you?")

    def test_question_action_got_response_false(self):
        self.action.got_response = False
        self.record_dict["workflow_action_id"] = 3
        self.record_dict["parameter1"] = "Hello, what is your first name?"
        self.record_dict["variable1_id"] = 6
        self.action.record = DialogWorkflowRecord(self.record_dict)

        result = self.action.question_action( self.action.record, False, "Do you like sports?")
        self.assertEqual(result[1], "Hello, what is your first name?")

    def test_jump_action(self):
        self.record_dict["workflow_action_id"] = 4
        self.record_dict["parameter1"] = "5"
        self.record_dict["variable1_id"] = None
        self.action.record = DialogWorkflowRecord(self.record_dict)

        result = self.action.jump_action(self.action.record)
        self.assertEqual(result, (True, None))
        self.assertEqual(self.profile_curr_state, 5)

    def test_send_rest_api_action(self):
        self.record_dict["workflow_action_id"] = 5
        self.record_dict["parameter1"] = "https://restcountries.com/"
        self.record_dict["variable1_id"] = 6
        self.action.record = DialogWorkflowRecord(self.record_dict)

        result = self.action.send_rest_api_action(self.action.record)
        self.assertEqual(result, (True, None))

    def test_assign_variable_action(self):
        self.record_dict["workflow_action_id"] = 6
        self.record_dict["parameter1"] = "middle"
        self.record_dict["variable1_id"] = 7
        self.action.record = DialogWorkflowRecord(self.record_dict)

        result = self.action.assign_variable_action(self.profile, self.record)
        self.assertEqual(result, (True, None))
        self.assertEqual(get_variable_value_by_id(Variable().get_variable_id("Middle Name")), self.action.record.parameter1)

    def test_increment_variable_action(self):
        self.record_dict["workflow_action_id"] = 7
        self.record_dict["parameter1"] = "2"
        self.record_dict["variable1_id"] = 22
        self.action.record = DialogWorkflowRecord(self.record_dict)

        result = self.action.increment_variable_action(self.action.record)
        self.assertEqual(result, (True, None))

    def test_menu_action_got_respone_false(self):
        self.action.got_response = False
        self.record_dict["workflow_action_id"] = 10
        self.record_dict["parameter1"] = ""
        self.record_dict["variable1_id"] = None
        self.action.record = DialogWorkflowRecord(self.record_dict)

        result = self.action.menu_action(self.action.record, False, "incoming")
        self.assertEqual(self.action.accumulated_message, result[1])
        
    def test_menu_action_got_respone_true(self):
        self.record_dict["state_id"] = 4
        self.record_dict["workflow_action_id"] = 10
        self.record_dict["parameter1"] = ""
        self.record_dict["variable1_id"] = None
        self.action.record = DialogWorkflowRecord(self.record_dict)
        incoming_message = "1"
        cursor.execute("""SELECT parameter1, next_state_id FROM dialog_workflow_state_view WHERE parent_state_id = %s""", [self.record_dict["state_id"]])
        child_nodes = cursor.fetchall()
        result = self.action.menu_action(self.action.record, True, incoming_message)
        self.assertEqual(self.action.profile_curr_state, (child_nodes[int(incoming_message)-1])["next_state_id"])
    
    def test_age_detection(self):
        self.record_dict["workflow_action_id"] = 11
        self.record_dict["parameter1"] = "middle"
        self.record_dict["variable1_id"] = 7
        self.action.record = DialogWorkflowRecord(self.record_dict)        
        _, json_message = self.action.age_detection(COMMUNICATION_TYPE, self.record)
        self.assertEqual(json_message, self.record.parameter1)

    def test_multi_choice_poll_got_response_true(self): #Also tests the generic_user_choice_action function
        self.action.incoming_message = "1,2,3"
        ret = self.action.multi_choice_poll()
        self.assertEqual(ret, (False, None))
    
    def test_replace_fields_with_values(self):
        message = "My age is {Age}"
        replace_fields_with_values_class = replace_fields_with_values(message, "en", Variable())
        formatted_message = replace_fields_with_values_class.get_variable_values_and_chosen_option()
        self.assertEqual(formatted_message, "My age is 25")

if __name__ == '__main__':
    unittest.main()


