import binascii
import os
import requests


class VerifyRequestStatusCode:

    def __init__(self, setting_fuzzer, parent_setting, kwargs):

        self.kw = kwargs
        self.url = parent_setting['url']
        self.req = requests.Session()
        self.setting_fuzzer = setting_fuzzer
        self.parent_setting = parent_setting
        self.step = 0
        self.critical_error = {}
        self.default = {"allow_redirects":True, "verify":True,
                        "headers":{"User-Agent":"Mozilla/5.0 (compatible; MSIE 10.0; "
                              "Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)"}}

    def run(self) -> tuple[bool, str]:
        # /* step 0: check connection */
        # pass
        # /* step 1: check ssl is valid*/
        if not self._check_ssl_and_conn():
            return False, "ssl"
        # /* step 2: change url */
        self._set_url()
        # /* step 3: check status code is not 403 */
        if not self._check_denied(cls=0):
            return False, 'waf'

        # * == SETTING == */
        if not self._check_redirect(cls=0):
            # /* step 4: check status code is not 301, 302 */
            self.kw['allow_redirects'] = True
            self.setting_fuzzer['allow_redirects'] = True
            # return False, 'moved'

        if not self._check_random_page(cls=0):
            # /* step 5: check status code is not 200 (verify by random index name)*/
            self.setting_fuzzer['content_and_length'] = True

        if not self._check_moved_captcha(cls=0):
            # /* step 6: None */
            return False, "captcha"

        self.parent_setting['url'] = self.url
        return True, "OK"

    def _check_random_page(self, cls):
        return self._test_request(cls, [200], 5)

    def _check_redirect(self, cls):
        return self._test_request(cls, [302, 301], 5)

    def _check_denied(self, cls=1):
        return self._test_request(cls, [403, 401, 429], 5)

    def _test_request(self, cls, status_code:list, rng):
        for i in range(rng):
            page = binascii.b2a_hex(os.urandom(6)).decode()
            _Request = self._get(page, cls=cls)
            if _Request.status_code in status_code and i == rng-1:
                self.setting_fuzzer['length'] = _Request.text.__len__()
                return False
        return True

    def _check_moved_captcha(self, cls=1):
        captcha = 0
        for page in range(0, 2):
            response = self._get("", cls)
            # /* WORDPRESS */
            if "/.well-known/captcha/" in response.url or "/.well-known/captcha/" in response.text:
                captcha += 1

        if captcha >= 2:
            return False

        return True

    def _set_url(self):
        # /* step 0: change url*/
        old = self.default['allow_redirects']
        self.default['allow_redirects'] = False
        res = self._get("", cls=1)
        self.default['allow_redirects'] = old
        print(res.url, res.status_code)
        if not res.status_code == 302:
            self.url = res.url
        return True

    def _check_ssl_and_conn(self):
        for i in range(0, 3):
            try:
                self._get("", cls=1)
            except requests.exceptions.SSLError:
                self.changeProto()
                if i: self.edit_www()
                if i == 2:
                    self.default['verify'] = False
                    self.kw['verify'] = False
                    self.changeProto()
            except requests.exceptions.ConnectionError:
                self.edit_www()
                if i: return False
            except requests.exceptions.InvalidSchema:
                return False

        return True

    def _get(self, index, cls=0):
        if cls:
            res = requests.get(self.url, **self.default)
        else:
            res = self.req.get(url=self.url+index, **self.kw)

        return res

    def edit_www(self):
        self.url = self.url.replace("www.", "")

    def changeProto(self):
        if "https://" in self.url:
            self.url = self.url.replace("https://", "http://")
        else:
            self.url = self.url.replace("http://", "https://")
