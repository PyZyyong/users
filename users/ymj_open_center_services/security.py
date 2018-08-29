import base64
import json
import textwrap
from urllib import parse
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import logging

# from ymj_open_center_services import config
from config.settings.base import YMJ_CONFIG

# logger = logging.getLogger('django')


def encrypt(content):
    json_text = json.dumps(content)
    url_encode_str = parse.quote(json_text)
    encode_str = url_encode_str.encode()
    public_path = 'b2c/users/ymj_open_center_services/keys/public_key.txt'
    private_path = 'b2c/users/ymj_open_center_services/keys/private_key.txt'

    with open(public_path) as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        encrypt_str = b''.join([cipher.encrypt(x.encode()) for x in textwrap.wrap(url_encode_str, 117)])
        encoded_params = base64.b64encode(encrypt_str)
        encoded_params = encoded_params.decode()
        encoded_params = parse.quote(encoded_params)

    with open(private_path) as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        signer = Signature_pkcs1_v1_5.new(rsakey)
        digest = SHA.new()
        digest.update(encode_str)
        sign = signer.sign(digest)
        encoded_sign = base64.b64encode(sign)
        encoded_sign = encoded_sign.decode()
        encoded_sign = parse.quote(encoded_sign)
    # logger.info(encoded_params)
    # logger.info(encoded_sign)
    # ymj_dict = config.yimeijian()
    dt = {"encrypted": True, "project_name": YMJ_CONFIG['project_name'],
          "encrypted_params": {"encrypted_info": encoded_params, "sign_info": encoded_sign}}
    dct = json.dumps(dt)
    return dct


def decrypt(content):

    if content == '':
        return {"status": 0, "status_text": "请求错误，请联系相关负责人"}

    obj_json = json.loads(content)
    status = obj_json['status']
    if int(status) == 0:
        data_json = obj_json['data']
        sign = data_json['sign_info']
        sign = parse.unquote(sign)
        result = data_json['encrypted_info']
        unquote_result = parse.unquote(result)
        result = base64.b64decode(unquote_result.encode('utf-8'))
        public_path = 'b2c/users/ymj_open_center_services/keys/public_key.txt'
        private_path = 'b2c/users/ymj_open_center_services/keys/private_key.txt'

        with open(private_path) as f:
            key = f.read()
            rsakey = RSA.importKey(key)
            cipher = Cipher_pkcs1_v1_5.new(rsakey)
            random_generator = Random.new().read
            default_length = 128
            len_content = len(result)
            offset = 0
            params_lst = []
            while len_content - offset > 0:
                if len_content - offset > default_length:
                    params_lst.append(cipher.decrypt(result[offset: offset + default_length], random_generator))
                else:
                    params_lst.append(cipher.decrypt(result[offset:], random_generator))
                offset += default_length
            decrypt_result = b''.join(params_lst)
            decrypt_unquote_result = parse.unquote(decrypt_result.decode())

        with open(public_path) as f:
            key = f.read()
            rsakey = RSA.importKey(key)
            verifier = Signature_pkcs1_v1_5.new(rsakey)
            digest = SHA.new()
            digest.update(decrypt_result)
            is_verify = verifier.verify(digest, base64.b64decode(sign))
            status_text = '验签失败'
    else:
        status_text = obj_json['status_text']
        is_verify = False

    if is_verify:
        return {"status": 1, "status_text": "ok", "data": decrypt_unquote_result}
    else:
        return {"status": 0, "status_text": status_text}
