import threading


class EmailThread(threading.Thread):
    # overriding constructor
    def __init__(self, email_object):
        # calling parent class constructor
        threading.Thread.__init__(self)
        self.email_object = email_object

    # overriding run method
    def run(self):
        self.email_object.send()
