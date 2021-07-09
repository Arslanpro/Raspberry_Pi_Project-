import unittest
from alarm_function.clock_multi import check_time_format
from alarm_function.active import active
from alarm_function.clock_multi import check_alarm_status

# because in clock_multi file and active file we edit the external text, so for some function we chose to test manually
# rather than automatically, also to avoid interfering with the ability of non-testing programs to read external text.


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("only called once. \n")

    @classmethod
    def tearDownClass(cls):
        print("only called once.\n")

    def setUp(self):
        print("prepare.\n")

    def tearDown(self):
        print("after test.\n")

    def test_check_time_format(self):
        self.assertEqual(False, check_time_format("64", "50"))

    def test_count(self):
        check = "1800"
        with open("set_alarm_time.txt", "a+") as file2:
            file2.seek(0)
            # add_new_alarm.seek(0)
            count = 0
            for line in file2:
                str = line.split(" ", 1)
                if str[0] == check:
                    count += 1
        self.assertEqual(1, count)

    def test_str(self):
        with open("set_alarm_time.txt") as file3:
            file3.seek(0)
            test = file3.readline()
            test = test.rstrip("\n").rstrip("E")
            str = test.split(" ", 1)
        self.assertEqual("1800", str[0])
        self.assertEqual("1801", str[1])

    def test_active1(self):
        active("18", "00", "18", "01")
        with open("set_alarm_time.txt") as file4:
            file_active = file4.readline()
        check = "1800 1801\n"

        self.assertNotEqual(check, file_active)

    def test_check_alarm_status(self):
        test1 = check_alarm_status("06", "00", "06", "17")
        test2 = check_alarm_status("07", "00", "07", "25")
        self.assertEqual(True, test1)
        self.assertEqual(0, test2)

    def test_alarm(self):
        Time = "0600"
        check_alarm =0
        with open("set_alarm_time.txt") as file5:
            file5.seek(0)
            form_alarm = file5.readline()
            one_alarm = file5.readline()
            str = one_alarm.split(" ", 1)
            str[1] = str[1].rstrip("\n")
            str1_without_state = str[1].rstrip("E")
            if Time == str[0] and one_alarm.find("E"):
                check_alarm = 1
            else:
                check_alarm = 0
        self.assertEqual(1, check_alarm)


if __name__ == '__main__':
    unittest.main()
