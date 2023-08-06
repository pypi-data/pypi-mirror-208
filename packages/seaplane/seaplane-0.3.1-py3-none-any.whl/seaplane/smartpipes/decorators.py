import functools
import json
import traceback

from ..logging import log
from ..model.errors import HTTPError
from .coprocessor import Coprocessor, CoprocessorEvent
from .smartpipe import SmartPipe, SmartPipeEvent


def format_exception(e):
    if e is None:
        return None

    return traceback.format_exception(type(e), e, e.__traceback__)


def event_json(event):
    return {
        "id": event.id,
        "smart_pipe_id": event.smart_pipe_id,
        "input": event.input,
        "status": event.status,
        "output": event.output,
        "error": format_exception(event.error),
        "coprocessors": [
            coprocessor_event_json(coprocessor) for coprocessor in event.coprocessors
        ],
    }


def coprocessor_event_json(event):
    return {
        "id": event.id,
        "input": event.input,
        "status": event.status,
        "output": event.output,
        "error": format_exception(event.error),
    }


def coprocessor_to_json(coprocessor):
    return {"id": coprocessor.id, "type": coprocessor.type, "model": coprocessor.model}


def smart_pipe_to_json(smart_pipe):
    return {
        "id": smart_pipe.id,
        "path": smart_pipe.path,
        "method": smart_pipe.method,
        "coprocessors": [
            coprocessor_to_json(coprocessor) for coprocessor in smart_pipe.coprocessors
        ],
    }


def smart_pipes_json(smart_pipes):
    return {
        "type": "smart_pipes",
        "payload": [smart_pipe_to_json(smart_pipe) for smart_pipe in smart_pipes],
    }


class Context:
    def __init__(self, smart_pipes=[], coprocessors=[]):
        self.smart_pipes = smart_pipes
        self.coprocessors = coprocessors
        self.actual_smart_pipe_index = -1
        self.on_change = lambda x: None
        self.events = []
        self.active_event = ["none"]

    def active_smart_pipe(self, id):
        for i, smart_pipe in enumerate(self.smart_pipes):
            if smart_pipe.id == id:
                self.actual_smart_pipe_index = i
                break

    def set_event(self, event):
        self.on_change = event

    def add_event(self, event):
        self.active_event[0] = event.id
        self.events.append(event)

        self.on_change({"type": "add_request", "payload": event_json(event)})

    def update_event(self, event):
        for i, e in enumerate(self.events):
            if e.id == self.active_event[0]:
                self.events[i] = event

                self.on_change({"type": "update_request", "payload": event_json(event)})
                break

    def coprocessor_event(self, coprocessor_event):
        for i, event in enumerate(self.events):
            if event.id == self.active_event[0]:
                event.add_coprocessor_event(coprocessor_event)

                self.events[i] = event

                self.on_change({"type": "update_request", "payload": event_json(event)})
                break

    def get_actual_smart_pipe(self):
        if self.actual_smart_pipe_index == -1:
            return None

        return self.smart_pipes[self.actual_smart_pipe_index]

    def add_smart_pipe(self, smart_pipe):
        if len(self.smart_pipes) == 1 and self.smart_pipes[0].id == "temporal":
            self.smart_pipes[0] = smart_pipe
        else:
            self.actual_smart_pipe_index = len(self.smart_pipes)
            self.smart_pipes.append(smart_pipe)

        log.info(f"🧠 Smart Pipe: {smart_pipe.id}, Path: {smart_pipe.path}")
        self.on_change(smart_pipes_json(self.smart_pipes))

    def add_coprocessor(self, coprocessor):
        log.info(f"⌛️ Coprocessor {coprocessor.id} of type: {coprocessor.type}")
        self.coprocessors.append(coprocessor)

    def set_coprocessor_function(self, id, func):
        for smart_pipe in self.smart_pipes:
            for coprocessor in smart_pipe.coprocessors:
                if coprocessor.id == id:
                    coprocessor.set_func(func)
                    return coprocessor

        return None

    def assign_to_active_smart_pipe(self, coprocessor):

        self.smart_pipes[self.actual_smart_pipe_index].add_coprocessor(coprocessor)
        smart_pipe = context.get_actual_smart_pipe()
        log.info(f"⌛️ Assign Coprocessor {coprocessor.id} to Smart Pipe: {smart_pipe.id}")
        self.on_change(smart_pipes_json(self.smart_pipes))


context = Context()


def smartpipe(
    _func=None,
    path=None,
    method=None,
    id=None,
):
    def decorator_smartpipes(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"SmartPipe Path: {path}, Method: {method}, ID: {id}")
            context.active_smart_pipe(id)

            args_str = tuple(arg.decode() if isinstance(arg, bytes) else arg for arg in args)
            args_json = json.dumps(args_str)

            event = SmartPipeEvent(smart_pipe_id=id, input=args_json)
            context.add_event(event)
            result = None

            try:
                result = func(*args, **kwargs)
                event.set_ouput(result)
            except HTTPError as err:
                log.error(f"Smart Pipe error: {err}")
                event.set_error(err)

            context.update_event(event)
            return result

        smart_pipe = SmartPipe(wrapper, path, method, id)
        context.add_smart_pipe(smart_pipe)
        return wrapper

    if not _func:
        return decorator_smartpipes
    else:
        return decorator_smartpipes(_func)


def import_coprocessor(_func=None, coprocessor=None):
    def decorator_coprocessor(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_str = tuple(arg.decode() if isinstance(arg, bytes) else arg for arg in args)
            args_json = json.dumps(args_str)

            event = CoprocessorEvent(coprocessor.id, args_json)
            context.coprocessor_event(event)

            result = coprocessor.process(*args, **kwargs)

            event.set_ouput(result)
            context.coprocessor_event(event)

            return func(result)

        return wrapper

    context.add_coprocessor(coprocessor)

    if not _func:
        return decorator_coprocessor
    else:
        return decorator_coprocessor(_func)


def coprocessor(_func=None, type=None, model=None, id=None):
    def decorator_coprocessor(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context.assign_to_active_smart_pipe(coprocessor)

            args_str = tuple(arg.decode() if isinstance(arg, bytes) else arg for arg in args)
            args_json = json.dumps(args_str)

            event = CoprocessorEvent(coprocessor.id, args_json)
            context.coprocessor_event(event)
            result = None

            try:
                result = coprocessor.process(*args, **kwargs)
                event.set_ouput(result)
            except HTTPError as err:
                log.error(f"Coprocessor HTTPError: {err}")
                event.set_error(err)
            except Exception as e:
                log.error(f"Coprocessor error: {e}")
                event.set_error(e)

            context.coprocessor_event(event)

            if event.error is not None:
                raise event.error

            return result

        coprocessor = Coprocessor(func, type, model, id)
        context.add_coprocessor(coprocessor)

        return wrapper

    if not _func:
        return decorator_coprocessor
    else:
        return decorator_coprocessor(_func)
