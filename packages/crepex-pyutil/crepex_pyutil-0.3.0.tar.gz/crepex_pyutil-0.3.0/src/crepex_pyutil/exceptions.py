class CodeMessageException(Exception):
    """
    내부 모듈에 사용
    """

    def __init__(self, code, msg):
        message = f"code{code}.{msg}"
        super().__init__(message)


class LoginException(CodeMessageException):
    def __init__(self, code: int):
        super().__init__(code, msg="로그인 실패")


class NoAttrException(CodeMessageException):
    def __init__(self, code=404, msg="필수 속성이 없습니다"):
        super().__init__(code=code, msg=msg)


class NotOkException(CodeMessageException):
    def __init__(self, code=400, msg="요청응답이 올바르지 않습니다"):
        super().__init__(code=code, msg=msg)
