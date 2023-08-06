"""
AES加解密 数据初始化
"""
from pyxk.utils import LazyLoader

AES = LazyLoader("AES", globals(), "Crypto.Cipher.AES")



# 目前支持的模式
MODES = {
    "ECB": 1,
    "CBC": 2,
    "CFB": 3,
    "OFB": 5,
    "CTR": 6,
    "OPENPGP": 7,
    "EAX": 9,
    "CCM": 8,
    "SIV": 10,
    "GCM": 11,
    "OCB": 12
}



class FormatData:
    """
    AES数据初始化
    """
    def __init__(
        self, key, iv=None, mode="CBC", encode="UTF-8", **kwargs
    ):
        self._key  = key
        self._mode = mode
        self._iv   = iv
        self._encode = encode
        self._state = kwargs
        self.__initialization()

    def __initialization(self):
        """
        初始化 key mode iv
        """
        self.__key_to_bytes()
        self.__mode_fmt()
        self.__iv_to_bytes()

    def __key_to_bytes(self):
        """
        key 转换为 bytes
        """
        key = self.key
        if isinstance(key, str):
            key = key.encode(self._encode)

        elif not isinstance(key, bytes):
            raise TypeError(
                "\033[31m'key' type must be 'str' or 'bytes',"
                f" not '{type(key).__name__}'\033[0m")

        # key 长度判断
        key_lenght = len(key)
        if key_lenght not in AES.key_size:
            raise ValueError(
                f"\033[31m'key' lenght must be {AES.key_size},"
                f" not '{key_lenght}'\033[0m")
        setattr(self, "_key", key)

    def __mode_fmt(self):
        """
        mode 判断
        """
        mode = self.mode
        if (
            isinstance(mode, str)
            and MODES.__contains__(mode.upper())
        ):
            mode = MODES[mode.upper()]

        if  (
            not isinstance(mode, int)
            or mode not in MODES.values()
        ):
            mode_val = list(MODES.keys())
            mode_val.extend(list(MODES.values()))
            raise TypeError(
                f"\033[31mmode must exist in the {mode_val},"
                f" not '{mode}'\033[0m")
        setattr(self, "_mode", mode)

    def __iv_to_bytes(self):
        """
        iv 转换为 bytes
        """
        iv = self.iv
        if iv is None:
            if self._mode != MODES["CBC"]:
                return
            iv = self.key[:16]

        if isinstance(iv, str):
            iv = iv.encode(self._encode)

        elif not isinstance(iv, bytes):
            raise TypeError(
                "\033[31m'iv' type must be 'str' or 'bytes',"
                f" not '{type(iv).__name__}'\033[0m")

        # iv 长度判断
        iv_lenght = len(iv)
        if iv_lenght != AES.block_size:
            raise ValueError(
                f"\033[31m'iv' lenght must be equal to '{AES.block_size}'"
                f", not '{iv_lenght}'\033[0m")
        setattr(self, "_iv", iv)

    @property
    def key(self):
        if not hasattr(self, "_key"):
            raise ValueError("\033[31m缺少'key'\033[0m")
        return getattr(self, "_key")

    @key.setter
    def key(self, value):
        setattr(self, "_key", value)
        self.__key_to_bytes()

    @property
    def mode(self):
        if not hasattr(self, "_mode"):
            setattr(self, "_mode", MODES["CBC"])
        return getattr(self, "_mode")

    @mode.setter
    def mode(self, value):
        setattr(self, "_mode", value)
        self.__mode_fmt()

    @property
    def iv(self):
        if not hasattr(self, "_iv"):
            setattr(self, "_iv", None)
        return getattr(self, "_iv")

    @iv.setter
    def iv(self, value):
        setattr(self, "_iv", value)
        self.__iv_to_bytes()
