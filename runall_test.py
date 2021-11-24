import unittest
import os
from multiprocessing import Process

class TestProcess(Process):
    def run(self):
        discover_store = unittest.defaultTestLoader.discover("./store", pattern="testsuites.py", top_level_dir=".")
        report_path = r"./test_report.txt"
        with open(report_path, "a") as report_file:
            runner = unittest.TextTestRunner(stream=report_file, verbosity=2)
            runner.run(discover_store)
class DBProcess(Process):
    def run(self):
        if os.path.exists(os.path.join(".", "store", "UCLH.db")):
            os.rename(os.path.join(".", "store", "UCLH.db"), os.path.join(".", "store", "UCLH_save.db"))
        from store.conn import create_database
        create_database()

if __name__ == "__main__":
    c = DBProcess()
    c.start()
    c.join()

    p = TestProcess()
    p.start()
    p.join()

    os.remove(os.path.join(".", "store", "UCLH.db"))
    os.rename(os.path.join(".", "store", "UCLH_save.db"), os.path.join(".", "store", "UCLH.db"))