from src.MessageSeverity import MessageSeverity
from src.Writer import Writer


class LoggerService:

    def __init__(self):
        self._writer = Writer()

    def info(self, *args, **kwargs):
        if args:
            self._writer.add_message(args[0], MessageSeverity.Information.value)
        else:
            if 'object' in kwargs:
                kwargs['object']['severity_id'] = MessageSeverity.Information.value
                self._writer.add(**kwargs)

    def error(self, *args, **kwargs):
        if args:
            self._writer.add_message(args[0], MessageSeverity.Error.value)
        else:
            if 'object' in kwargs:
                kwargs['object']['severity_id'] = MessageSeverity.Error.value
                self._writer.add(**kwargs)

    def warn(self, *args, **kwargs):
        if args:
            self._writer.add_message(args[0], MessageSeverity.Warning.value)
        else:
            if 'object' in kwargs:
                kwargs['object']['severity_id'] = MessageSeverity.Warning.value
                self._writer.add(**kwargs)

    def debug(self, *args, **kwargs):
        if args:
            self._writer.add_message(args[0], MessageSeverity.Debug.value)
        else:
            if 'object' in kwargs:
                kwargs['object']['severity_id'] = MessageSeverity.Debug.value
                self._writer.add(**kwargs)

    def verbose(self, *args, **kwargs):
        if args:
            self._writer.add_message(args[0], MessageSeverity.Verbose.value)
        else:
            if 'object' in kwargs:
                kwargs['object']['severity_id'] = MessageSeverity.Verbose.value
                self._writer.add(**kwargs)

