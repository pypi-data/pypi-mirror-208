import unittest

import time as time_module
import src.hkkang_utils.time as time_utils

TEST_TIME = 2

class Test_time_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_time_utils, self).__init__(*args, **kwargs)
        
    @classmethod
    def setUpClass(cls):
        cls.timer = time_utils.Timer()
        with cls.timer.measure():
            time_module.sleep(TEST_TIME)
    
    def test_timer_measure(self):
        timer = time_utils.Timer()
        timer.start()
        time_module.sleep(TEST_TIME)
        timer.stop()
        assert timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME+1, f"Timer is not working properly: {timer.elapsed_time} sec is measured."
    
    def test_timer_measure_as_decorator(self):
        timer = time_utils.Timer()
        with timer.measure():
            time_module.sleep(TEST_TIME)
        assert timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME+1, f"Timer is not working properly: {timer.elapsed_time} sec is measured."
    
    def test_timer_loading_by_name(self):
        timer_name = self.timer.name
        timer = time_utils.Timer(timer_name)
        assert timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME+1, f"Timer is not working properly: {timer.elapsed_time} sec is measured."

if __name__ == "__main__":
    unittest.main()
    
    