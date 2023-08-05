
import secrets
import string


class PasswordMake:
    @staticmethod
    def make_random_password(length:int=10,
                             allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                           'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                           '1234567890'
                                           '!@.#') -> str:
        """
        Generate a random password with the given length and given
        allowed_chars. The default value of allowed_chars does not have "I" or
        "O" or letters and digits that look similar -- just to avoid confusion.
        """
        return ''.join(secrets.choice(allowed_chars) for i in range(length))

class PasswordStrength:
    """
    检查是否弱密码
    """
    def is_weak_password(self, words_path="", pw_str="123456"):

        '''
            words_path: 字典库地址。

            字典格式:

                123456
                password
                12345678
                ...
                1234567
                dragon
        '''

        with open(words_path) as f:
            word_list = []
            for line in f.readlines():
                word_list.append(line.strip())

            if pw_str in word_list: 
                return True
            elif pw_str == pw_str.upper() and pw_str.lower() in word_list:
                return True
            elif pw_str == pw_str.title() and pw_str.lower() in word_list:
                return True
            else:
                return False

    def password_strength(self, pw_str):
        if len(pw_str) < 8 or self.is_weak_password(pw_str=pw_str):
            return 'WEAK'
        elif (len(pw_str) > 11 and 
                any(ch in string.ascii_lowercase for ch in pw_str) and
                any(ch in string.ascii_uppercase for ch in pw_str) and
                any(ch.isdigit() for ch in pw_str)):
            return 'STRONG'
        else:
            return 'MEDIUM'   