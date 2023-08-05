#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档参考
# https://stackoverflow.com/questions/16899247/how-can-i-decode-a-ssl-certificate-using-python
# https://cryptography.io/en/latest/x509/reference/
"""

import ssl
import socket

class CertUtils:
    """
    获取证书信息

    # 同样的X.509证书,可能有不同的编码格式,目前有以下两种编码格式.

    # PEM - Privacy Enhanced Mail,打开看文本格式,以"-----BEGIN..."开头, "-----END..."结尾,内容是BASE64编码.
    # 查看PEM格式证书的信息:openssl x509 -in certificate.pem -text -noout
    # Apache和*NIX服务器偏向于使用这种编码格式.

    # DER - Distinguished Encoding Rules,打开看是二进制格式,不可读.
    # 查看DER格式证书的信息:openssl x509 -in certificate.der -inform der -text -noout
    # Java和Windows服务器偏向于使用这种编码格式.
    """

    def __init__(self):
        pass

    def get_ssl_file_info(self, cert_file):
        # import ssl
        try:
            ssl_info = ssl._ssl._test_decode_cert(cert_file)
        except ssl.SSLError as err:
            raise RuntimeError(err, cert_file)
        return ssl_info

    def load_x509_cert_use_openssl(self, cert_data: bytes, cert_format="pem"):
        import OpenSSL.crypto

        assert isinstance(cert_data, bytes)
        if cert_format == "der":
            cert_X509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1,
                                                        cert_data)
        else:
            cert_X509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                                        cert_data)
        cert_x509_data = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_TEXT,
                                                         cert_X509)
        return cert_x509_data

    def load_x509_cert_use_cryptography(self, cert_data: bytes, cert_format="pem"):
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend

        assert isinstance(cert_data, bytes)
        if cert_format == "der":
            cert_x509_data = x509.load_der_x509_certificate(cert_data,
                                                            default_backend())
        else:
            cert_x509_data = x509.load_pem_x509_certificate(cert_data,
                                                            default_backend())
        return cert_x509_data

    def get_ssl_url_info(self, hostname: str, port=443) -> dict:
        """
        https://lucasroesler.com/2017/06/ssl-expiry-quick-and-simple/
        https://github.com/LucasRoesler/ssl-expiry-check/blob/master/ssl_expiry.py
        https://serverlesscode.com/post/ssl-expiration-alerts-with-lambda/
        """
        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=hostname,
        )

        # self.logger.debug('Connect to {}'.format(hostname))
        try:
            # 3 second timeout because Lambda has runtime limitations
            conn.settimeout(3.0)
            conn.connect((hostname, port))
            ssl_info = conn.getpeercert()  
        except (ssl.SSLCertVerificationError, socket.timeout) as err:
            raise RuntimeError(err, hostname)
        return ssl_info
        # # parse the string from the certificate into a Python datetime object
        # return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
