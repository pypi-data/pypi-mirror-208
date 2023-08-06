import typing

class VLPError(Exception):
    pass

class VLPTypeError(VLPError):
    """数据类型异常:
    """
    def __init__(self, value, *typeargv:type):
        """数据需为指定的类型
        """
        self._value = value
        self._type = [str(i).split("\'")[1] for i in list(typeargv)]
    
    def __str__(self):
        s = str(type(self._value)).split("\'")[1]
        return repr(f"The value must be of type {self._type}, but this value is of type {s}.")

class VLPSequenceLenError(VLPError):
    """序列长度异常
    """
    def __init__(self,value:typing.Sequence,length:int):
        """序列需固定的长度
        """
        self._value = value
        self._len = length
    def __str__(self) -> str:
        return repr(f"The length of the Sequence has to be {self._len}, but this Sequence has length {len(self._value)}.")

class VLPValueError(VLPError):
    """数据取值异常
    """
    def __init__(self,value,*argv):
        """数据应指定的取值
        """
        self._value = value
        self._argv = list(argv)
    def __str__(self) -> str:
        return repr(f"The value {self._value} is not in {self._argv}.")

class VLPValueRangeError(VLPError):
    """数据取值范围异常
    """
    def __init__(self,value,low,hignt):
        """数据应在指定的范围内,可能不包括端点处的取值
        """
        self._value = value
        self._range = (low,hignt)
    def __str__(self) -> str:
        return repr(f"The value {self._value} must be in the range {self._range}.")



