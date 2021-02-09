# Python Logging Library, written with security and rapid debugging in mind.
# Written by github.com/Mersair

import os
import inspect

class WaterLog:
    __init__(self):
        waterlog_tag = "[WaterLog] "
        stack = inspect.stack()
        self.class_name = stack[1][0].f_locals["self"].__class__.__name__
        log_mode = os.getenv('LOG_MODE')
        if (log_mode is None):
            print("""{waterlog_tag}'LOG_MODE' environment variable not found. 
            For the sake of security, no debug logging information will
            be printed out. Please configure this and restart your app.""")
        elif (log_mode is "DEV"):
            ensure_development()
            print("""{waterlog_tag}Logging at a DEVELOPMENT level. This means 
            sensitive information may be displayed. If this is a mistake, 
            it is crucial that you re-configure.""")
            self.log_mode = log_mode
        elif (log_mode is "PROD"):
            print("""{waterlog_tag}Logging at a PRODUCTION level. This means 
            only performance information will be displayed.""")
            self.log_mode = log_mode
        else:
            print("""{waterlog_tag}Environmental variable '{log_mode}' was 
            not matched to either 'DEV' or 'PROD'. Please reconfigure this to be one 
            of the two and restart your app.""")

    def debug(log_message):
        if (self.log_mode == "DEBUG"):
            print("[{self.class_name}] {log_message}")

    def log(log_message):
        if (self.log_mode == "PROD" or self.log_mode = "DEBUG"):
            print("[{self.class_name}] {log_message}")
