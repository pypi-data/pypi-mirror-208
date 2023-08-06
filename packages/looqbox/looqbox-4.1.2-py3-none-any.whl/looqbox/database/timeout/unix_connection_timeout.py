from looqbox.database.database_exceptions import alarm_handler
import signal


class UnixConnectionTimeout:
    @staticmethod
    def set_timeout(response_timeout: int) -> None:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(response_timeout)

    @staticmethod
    def reset_timeout() -> None:
        signal.alarm(0)

