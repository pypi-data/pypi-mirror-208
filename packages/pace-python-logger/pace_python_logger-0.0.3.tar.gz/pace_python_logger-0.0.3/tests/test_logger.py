import unittest
from dotenv import load_dotenv
import src.pace_py_log_lib.logger as logger
import os
import uuid
import time

load_dotenv()

class TestLoggingFramework(unittest.TestCase):

    def test_simple_logging(self):
        test_url = os.environ["TEST_INFRA_URL"]
        
        print(f"Setting the test URL to {test_url}....")
        logger.set_socket_url(f"{test_url}?test")

        request = str(uuid.uuid1())
        session = str(uuid.uuid1())
        experience= "unit_test"
        snippetVal = "Finalized snippet for unit test"
        duration = 2.5

        print(f"\t Event marker started waiting {duration} seconds")
        logger.start_event_marker(session=session,
                                  request=request,
                                  experience=experience)
        time.sleep(duration)

        logger.log_final_snippet(snippetVal)
        print("\t Event marker ended")
        
        last_val = logger.peek_last_test_url()
        
        print("\t Closing open connection")
        logger.close_open_connection()

        self.assertEqual(last_val["request_id"],
                         request,
                         "RequestID lost in translation")
        
        self.assertEqual(last_val["session_id"],
                         session,
                         "SessionID lost in translation")
        
        self.assertEqual(last_val["experience_id"],
                         experience,
                         "ExperienceID lost in translation")
        
        self.assertGreater(last_val["duration"],
                         duration,
                         "Duration lost in translation")
        
        self.assertEqual(last_val["snippet"],
                         snippetVal,
                         "Snippet issue")
        
if __name__ == '__main__':
    unittest.main()