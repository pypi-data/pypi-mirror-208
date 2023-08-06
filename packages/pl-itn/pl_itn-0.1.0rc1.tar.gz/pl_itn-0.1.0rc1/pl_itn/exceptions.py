class InterruptException(BaseException):
    pass


def gentle_interrupt_handler(_, __) -> None:
    raise InterruptException
