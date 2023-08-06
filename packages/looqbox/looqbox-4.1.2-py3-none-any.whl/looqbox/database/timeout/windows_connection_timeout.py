class WindowsConnectionTimeout:
    @staticmethod
    def set_timeout(response_timeout: int) -> None:
        # Since Windows OS doesn't support signal usage and is use only in a local development scenario
        # no timeout will be set for this OS.
        pass

    @staticmethod
    def reset_timeout() -> None:
        # Since Windows OS doesn't support signal usage and is use only in a local development scenario
        # no timeout will be set for this OS.
        pass

