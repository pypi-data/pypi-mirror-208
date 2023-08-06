import secrets
import string


def randomId():
    alphabet = string.ascii_letters + string.digits
    random_string = "".join(secrets.choice(alphabet) for i in range(10))
    return random_string


class SmartPipeEvent:
    def __init__(self, smart_pipe_id=None, input=None):
        self.id = randomId()
        self.smart_pipe_id = smart_pipe_id
        self.status = "in_progress"
        self.input = input
        self.output = None
        self.coprocessors = []
        self.error = None

    def add_coprocessor_event(self, event):
        for i, cp in enumerate(self.coprocessors):
            if cp.id == event.id:
                self.coprocessors[i] = event
                return
        self.coprocessors.append(event)

    def set_ouput(self, output):
        self.output = output
        self.status = "completed"

    def set_error(self, error):
        self.error = error
        self.status = "error"


class SmartPipe:
    def __init__(self, func=None, path=None, method=None, id=None):
        self.func = func
        self.path = path
        self.method = method
        self.id = id
        self.coprocessors = []
        self.events = []

    def add_coprocessor(self, coprocessor):
        for i, cp in enumerate(self.coprocessors):
            if cp.id == coprocessor.id:
                self.coprocessors[i] = coprocessor
                return
        self.coprocessors.append(coprocessor)
