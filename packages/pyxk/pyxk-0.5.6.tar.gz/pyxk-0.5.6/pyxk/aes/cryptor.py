"""
AES 加解密
"""
from pyxk.utils import LazyLoader

copy = LazyLoader("copy", globals(), "copy")
AES = LazyLoader("AES", globals(), "Crypto.Cipher.AES")
typing = LazyLoader("typing", globals(), "typing")
fmtdata = LazyLoader("fmtdata", globals(), "pyxk.aes._fmtdata")



def no_padding(data, remove=False, pad=b"\x00"):
    """
    NoPadding填充模式
    """
    # 消除 padding 字符
    if remove:
        return data.rstrip(pad)
    remainder = len(data) % AES.block_size or AES.block_size
    data += pad * (AES.block_size - remainder)
    return data

def zero_padding(data, remove=False, pad=b"\x00"):
    """
    ZeroPadding填充模式
    """
    # 消除 padding 字符
    if remove:
        return data.rstrip(pad)
    remainder = len(data) % AES.block_size
    # 不填充
    data += pad * (AES.block_size - remainder)
    return data

PADDING_ALL = {
    "Raw": lambda data, *args, **kwagrs: data,
    "NoPadding": no_padding,
    "ZeroPadding": zero_padding,
}


class Cryptor(fmtdata.FormatData):
    """AES加解密"""
    def __init__(
        self, key, iv=None, mode="CBC", padding="NoPadding", **kwargs
    ):
        self._cipher = None
        self._padding = padding
        self.__padding_fmt()
        super().__init__(key, iv, mode, **kwargs)

    def __padding_fmt(self):
        """加解密数据的填充方式"""
        padding = getattr(self, "_padding", None)
        if padding is None:
            setattr(self, "_padding", "NoPadding")
            return

        if (
            not isinstance(padding, str)
            or padding not in PADDING_ALL
        ):
            raise ValueError(
                f"\033[31m'padding' must exist in the {list(PADDING_ALL)},"
                f" not '{padding}'\033[0m")

    def encrypt(self, plaintext):
        """加密"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode(self._encode)

        elif not isinstance(plaintext, bytes):
            raise TypeError(
                "\033[31m'plaintext' type must be 'str' or 'bytes',"
                f" not '{type(plaintext).__name__}'\033[0m")

        # 创建 cipher - 加密
        self.__create_cipher()
        padding_func = PADDING_ALL[self.padding]
        return self._cipher.encrypt( padding_func(plaintext) )

    def decrypt(self, ciphertext):
        """解密"""
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode(self._encode)

        elif not isinstance(ciphertext, bytes):
            raise TypeError(
                "\033[31m'plaintext' type must be 'str' or 'bytes',"
                f" not '{type(ciphertext).__name__}'\033[0m")

        # 创建 cipher - 解密
        self.__create_cipher()
        padding_func = PADDING_ALL[self.padding]
        return padding_func(self._cipher.decrypt(ciphertext), True)

    def __create_cipher(self):
        """创建 cipher"""
        state = copy.deepcopy(self._state)
        state["key"]  = self.key
        state["mode"] = self.mode
        if self.iv is not None:
            state["iv"] = self._iv
        setattr(self, "_cipher", AES.new(**state))

    @property
    def padding(self):
        if not hasattr(self, "_padding"):
            setattr(self, "_padding", "NoPadding")
        return getattr(self, "_padding")

    @padding.setter
    def padding(self, value):
        setattr(self, "_padding", value)
        self.__padding_fmt()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            raise
        self._cipher = None


def encrypt(
    key: typing.Union[str, bytes],
    plaintext: typing.Union[str, bytes],
    *,
    mode: typing.Union[int, str]="CBC",
    iv: typing.Union[str, bytes]=None,
    **kwargs
) -> bytes:
    """AES 加密

    :params: key: 加密密钥
    :params: plaintext: 加密明文
    :params: mode: 加密模式
    :params: iv: 加密偏移量(部分加密模式不需要偏移量)
    :params: **kwargs: 可选关键字参数
    """
    with Cryptor(key=key, mode=mode, iv=iv, **kwargs) as _cipher:
        return _cipher.encrypt(plaintext)

def decrypt(
    key: typing.Union[str, bytes],
    ciphertext: typing.Union[str, bytes],
    *,
    mode: typing.Union[int, str]="CBC",
    iv: typing.Union[str, bytes]=None,
    **kwargs
) -> bytes:
    """AES 解密

    :params: key: 解密密钥
    :params: ciphertext: 解密密文
    :params: mode: 解密模式
    :params: iv: 解密偏移量(部分解密模式不需要偏移量)
    :params: **kwargs: 可选关键字参数
    """
    with Cryptor(key=key, mode=mode, iv=iv, **kwargs) as _cipher:
        return _cipher.decrypt(ciphertext)
