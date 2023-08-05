# -*- coding: utf-8 -*-

import hmac

class HmacUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def sign(key, msg=None, digestmod=''):
        """
        跟 sign_02 的区别是可以额外支持OS本身所支持的所有算法，但是速度不如sign_02快。

        algorithms: 允许访问hashlib列出的哈希算法以及你的 OpenSSL 库可能提供的任何其他算法。 
                    常用的算法 - 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
                                'blake2b', 'blake2s',
                                'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                                'shake_128', 'shake_256'
        PS： 同名的构造器要比 new()， 更快所以应当优先使用
    
        data： 数据
        """
        h = hmac.new(key, msg=msg, digestmod=digestmod)
        return h.hexdigest().encode('utf-8')

    @staticmethod
    def verify(a, b):
        """
        返回 a == b。 此函数使用一种经专门设计的方式通过避免基于内容的短路行为来防止定时分析，使得它适合处理密码。 
        a 和 b 必须为相同的类型：或者是 str (仅限 ASCII 字符，如 HMAC.hexdigest() 的返回值)，或者是 bytes-like object。

        PS: 在验证例程运行期间将 hexdigest()/digest() 的输出与外部提供的摘要进行比较时，建议使用 compare_digest() 函数而不是 == 运算符以减少定时攻击防御力的不足。
        """
        return hmac.compare_digest(a, b)