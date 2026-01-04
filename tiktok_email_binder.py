import requests
import time
import uuid
import secrets
import string
import json
from urllib.parse import urlencode
from SignerPy import sign, ttencrypt, get
from hsopyt import Argus, Ladon, Gorgon, md5

class TikTokEmailBinder:
    def __init__(self, proxy: str = None):
        """
        تهيئة الربط مع TikTok
        
        Args:
            proxy: بروكسي اختياري (صيغة: user:pass@ip:port)
        """
        self.proxy = proxy
        self.proxies = self._setup_proxy()
        
    def _setup_proxy(self):
        """تهيئة إعدادات البروكسي"""
        if self.proxy:
            return {
                "http": f"http://{self.proxy}",
                "https": f"http://{self.proxy}"
            }
        else:
            # بروكسي افتراضي
            default = '8c85946d55686edcaa7f:a6b7aa8175c17bd5@gw.dataimpulse.com:823'
            return {
                "http": f"http://{default}",
                "https": f"http://{default}"
            }
    
    def _device_register(self):
        """تسجيل الجهاز"""
        params = {
            "aid": "1233",
            "app_name": "musical_ly",
            "app_type": "normal",
            "channel": "googleplay",
            "device_platform": "android",
            "device_brand": "sony",
            "device_type": "SO-51A",
            "ssmix": "a",
            "version_code": "360505",
            "version_name": "36.5.5",
            "manifest_version_code": "2023605050",
            "update_version_code": "2023605050",
            "build_number": "36.5.5",
            "ab_version": "36.5.5",
            "language": "ar",
            "region": "IQ"
        }
        
        params.update(get(params))
        
        session = requests.Session()
        secret = secrets.token_hex(16)
        session.cookies.update({
            "passport_csrf_token": secret,
            "passport_csrf_token_default": secret
        })
        
        sig = sign(params=params, payload="", cookie="", version=4404, sdk_version=2)
        
        payload = ttencrypt.Enc().encrypt(data=json.dumps({
            "magic_tag": "ss_app_log",
            "header": {
                "display_name": "TikTok",
                "aid": 1233,
                "channel": "googleplay",
                "package": "com.zhiliaoapp.musically",
                "app_version": params["version_name"],
                "version_code": int(params["version_code"]),
                "sdk_version": "3.10.3-tiktok.1",
                "os": "Android",
                "os_version": "12",
                "device_model": params["device_type"],
                "device_brand": params["device_brand"],
                "cpu_abi": "arm64-v8a",
                "language": "ar",
                "access": "wifi",
                "mcc_mnc": "41820",
                "cdid": params.get("cdid", ""),
                "openudid": params.get("openudid", ""),
                "google_aid": str(uuid.uuid4()),
                "req_id": str(uuid.uuid4()),
                "region": "IQ",
                "tz_name": "Asia/Baghdad",
                "device_platform": "android",
                "apk_first_install_time": int(time.time()),
                "custom": {
                    "web_ua": f"Dalvik/2.1.0 (Linux; U; Android 14; {params['device_type']} Build/UP1A.231005.007)",
                    "priority_region": "IQ",
                    "dark_mode_setting_value": 1
                }
            },
            "_gen_time": int(time.time())
        }, separators=(',', ':')))
        
        headers = {
            "User-Agent": f"com.zhiliaoapp.musically/2023605050 (Linux; U; Android 14; ar_IQ; {params['device_type']}; Build/UP1A.231005.007)",
            "x-tt-passport-csrf-token": secret,
            "content-type": "application/octet-stream;tt-data=a",
        }
        headers.update(sig)
        
        request_params = {
            "tt_data": "a",
            "ac": "WIFI",
            "channel": "googleplay",
            "aid": "1233",
            "app_name": "musical_ly",
            "version_code": "360505",
            "version_name": "36.5.5",
            "device_platform": "android",
            "os": "android",
            "ab_version": "36.5.5",
            "ssmix": "a",
            "language": "ar",
            "is_pad": "0",
            "app_type": "normal",
            "carrier_region_v2": "418",
            "app_language": "ar",
            "timezone_offset": "10800",
            "build_number": "36.5.5",
            "locale": "ar",
            "region": "IQ",
        }
        request_params.update(params)
        
        url = "https://log-boot.tiktokv.com/service/2/device_register/"
        response = session.post(url, params=request_params, data=payload, headers=headers, proxies=self.proxies)
        
        try:
            data = response.json()
            return data.get("device_id"), data.get("install_id")
        except:
            return None, None
    
    def _sign_request(self, params: str, payload: str, sec_device_id: str):
        """توقيع الطلب"""
        x_ss_stub = md5(payload.encode('utf-8')).hexdigest()
        unix = time.time()
        
        result = Gorgon(params, unix, payload, None).get_value()
        result.update({  
            'content-length': str(len(payload)),
            'x-ss-stub': x_ss_stub.upper(),
            'x-ladon': Ladon.encrypt(int(unix), 1611921764, 1233),
            'x-argus': Argus.get_sign(
                params, x_ss_stub, int(unix),
                platform=0,
                aid=1233,
                license_id=1611921764,
                sec_device_id=sec_device_id,
                sdk_version='v05.00.06-ov-android',
                sdk_version_int=167775296
            )
        })
        return result
    
    def bind_email(self, sessionid: str, email: str):
        """
        ربط البريد الإلكتروني بحساب TikTok
        
        Args:
            sessionid: معرف الجلسة من TikTok
            email: البريد الإلكتروني لربطه
            
        Returns:
            dict: نتيجة العملية
        """
        # تسجيل الجهاز أولاً
        device_id, install_id = self._device_register()
        if not device_id:
            device_id = "7247151522348632578"
        if not install_id:
            install_id = "7247151723484751362"
        
        # إعدادات الطلب
        url = "https://api22-normal-c-alisg.tiktokv.com/passport/email/bind_without_verify/"
        
        params = {  
            "passport-sdk-version": "19",  
            "iid": install_id,
            "device_id": device_id,
            "ac": "mobile",  
            "ac2": "mobile",  
            "channel": "googleplay",  
            "aid": "1233",  
            "app_name": "musical_ly",  
            "version_code": "310503",  
            "version_name": "31.5.3",  
            "ab_version": "31.5.3",  
            "build_number": "31.5.3",  
            "app_version": "31.5.3",  
            "manifest_version_code": "2023105030",  
            "update_version_code": "2023105030",  
            "device_platform": "android",  
            "os": "android",  
            "os_api": "28",  
            "os_version": "9",  
            "device_type": "NE2211",  
            "device_brand": "OnePlus",  
            "host_abi": "arm64-v8a",  
            "resolution": "900*1600",  
            "dpi": "240",  
            "openudid": "7a59d727a58ee91e",  
            "language": "en",  
            "app_language": "en",  
            "locale": "en-GB",  
            "content_language": "en,",  
            "region": "GB",  
            "sys_region": "US",  
            "current_region": "TW",  
            "op_region": "TW",  
            "carrier_region": "TW",  
            "carrier_region_v2": "466",  
            "residence": "TW",  
            "mcc_mnc": "46692",  
            "timezone_name": "Asia/Baghdad",  
            "timezone_offset": "10800",  
            "_rticket": int(time.time() * 1000),  
            "ts": int(time.time()),  
            "app_type": "normal",  
            "is_pad": "0",  
            "uoo": "0",  
            "support_webview": "1",  
            "cronet_version": "2fdb62f9_2023-09-06",  
            "ttnet_version": "4.2.152.11-tiktok",  
            "use_store_region_cookie": "1",  
            "cdid": str(uuid.uuid4()),  
        }  
        
        payload_data = {  
            'account_sdk_source': 'app',  
            'multi_login': '1',  
            'email_source': '9',  
            'email': email,  
            'mix_mode': '1'  
        }
        
        # توقيع الطلب
        sec_device_id = "AadCFwpTyztA5j9L" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(9))
        signed_headers = self._sign_request(
            urlencode(params), 
            urlencode(payload_data),  
            sec_device_id
        )  
        
        headers = {  
            "User-Agent": "com.zhiliaoapp.musically/2023105030 (Linux; U; Android 9; en; OnePlus NE2211; Build/PKQ1.180716.001; Cronet/2fdb62f9 2023-09-06)",  
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",  
            "cookie": f"sessionid={sessionid}",  
            "sdk-version": "2",  
            "passport-sdk-version": "19",  
            "x-ss-dp": "1233",  
        }  
        
        headers.update(signed_headers)
        
        # إرسال الطلب
        response = requests.post(
            url, 
            params=params, 
            data=urlencode(payload_data), 
            headers=headers, 
            proxies=self.proxies
        )
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text,
            "email": email
        }


# مثال للاستخدام
def example_usage():
    """مثال لكيفية استخدام الكود"""
    
    # الطريقة 1: بدون بروكسي
    binder = TikTokEmailBinder()
    
    # الطريقة 2: مع بروكسي
    # binder = TikTokEmailBinder(proxy="user:pass@ip:port")
    
    result = binder.bind_email(
        sessionid="004c8dfde0d24682bcdeda6869e13f59",
        email="hwrwmloh@hi2.in"
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    example_usage()
