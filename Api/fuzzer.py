from threading import Thread
from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal

from Api.analyzeAddr import MECHANISM_ERROR
from Api.payloads import *
from Api.status_code import VerifyRequestStatusCode


class FuzzerUI(QThread):
    emitStatus = pyqtSignal(int, int, int, list)
    emitFinish = pyqtSignal(int, str, list)
    emitErrors = pyqtSignal(dict, str)
    emitSetting = pyqtSignal(dict)

    def __init__(self, parent_setting, setting_fuzz, listFuzzer, parent, **kwargs):
        super(FuzzerUI, self).__init__(parent)

        self.fuzz = MGetFuzzer(parent_setting, setting_fuzz, listFuzzer, **kwargs)

    # noinspection PyUnresolvedReferences
    def run(self) -> None:

        self.fuzz.Start()
        self.emitErrors.emit(MECHANISM_ERROR, self.fuzz.mech_error_key)
        if not self.fuzz.cancel:
            self.emitSetting.emit(self.fuzz.setting_fuzz)
        while self.fuzz.total < self.fuzz.size and not self.fuzz.cancel:
            # self.msleep(200)
            self.emitStatus.emit(self.fuzz.total, self.fuzz.size, self.fuzz.indexes.__len__(), self.fuzz.indexes)
        self.fuzz.killFuzz()

        self.emitFinish.emit(1, self.fuzz.about_cancel, self.fuzz.indexes)

    def Cancel(self):
        self.fuzz.cancel = 1


# /* pages to status code */
PAGES_TSC = ['.exe',
             '.asp',
             '.aspx',
             '.php',
             '.phtml',
             '.html',
             '.py',
             'sjcksdc.',
             '.goi9384u02fdmkn',
             '.jdfnjkvndfkjnv',
             '.pem',
             "oksasjnencwvniwioenv"]


class MGetFuzzer:

    def __init__(self, parent_setting, setting_fuzz, listFuzzer, *args, **kwargs):
        self.req = requests.Session()
        self.arg = args
        self.kw = kwargs
        self.url = parent_setting['url']
        self.LFuzzer = listFuzzer
        self.size = listFuzzer.__len__()
        self.total = 0
        self.indexes = []
        self.mech_error_key = "ok"
        self.setting_fuzz = {'length': 0, "length_redirect": 0} | setting_fuzz
        self.parent_setting = parent_setting
        self.status_code_valid = {"denied":0, 'crashed':0, "captcha":0, "moved": 0}
        self.about_cancel: str = "ok"
        self.cancel = 0

        # /* set on **kwargs of requests.get method */
        self.kw['allow_redirects'] = setting_fuzz['allow_redirects']
        self.kw['headers'] = {"User-Agent": setting_fuzz['User-Agent']}
        self.kw['cookies'] = setting_fuzz['cookies']

    def Start(self):

        # /* auto setting by some conditions */
        setup = self.checkStatusCode()

        if not setup[0]:
            MECHANISM_ERROR[setup[1]] = 1
            self.mech_error_key = setup[1]
            self.cancel = 1
            return
        # /* START */
        Thread(target=self._check_status_code).start()
        s, e = 0, 0
        for i in range(self.setting_fuzz['threads']):
            e += len(self.LFuzzer) // self.setting_fuzz['threads']
            Thread(target=self.fuzzing, args=(self.LFuzzer[s:e],)).start()
            s = e

        Thread(target=self.fuzzing,
               args=(self.LFuzzer[e: e + len(self.LFuzzer) % self.setting_fuzz['threads']],)).start()

    def _check_status_code(self):
        while self.total < self.size or not self.cancel:
            if self.status_code_valid['crashed'] > 200:
                self.cancel = 1
                self.about_cancel = "server return 500/501/502,\nmaybe server crashed!"
                break
            elif self.status_code_valid['denied'] > 200:
                self.cancel = 1
                self.about_cancel = "server return 403,\nmaybe your ip denied!"
                break
            elif self.status_code_valid['captcha'] > 200:
                self.cancel = 1
                self.about_cancel = "server moved to captcha?,\n200 blocked fuzzer"
                break
            elif self.status_code_valid['moved'] > 300:
                self.cancel = 1
                self.about_cancel = "server moved to another page, \n*redirect block fuzzer!"
                break
            sleep(0.8)

    def fuzzing(self, indexes: list):
        for index in indexes:
            self.total += 1
            if self.cancel:
                break

            # /* careful */
            try:
                response = self.req.get(*self.arg, **self.kw, url=f"{self.url}{index}")
            except Exception as Err:
                print(f'{Err}')
                sleep(1)
                continue

            data = {'ind': index, 'stat': response.status_code, 'typ': ("File" if "." in index else 'dir'),
                    'size': response.text.__len__()}
            if not self.setting_fuzz['content_and_length']:
                if self.validToAppend(response.status_code, response.text.__len__()):
                    self.indexes.append(data)
            else:
                if not self.setting_fuzz['length'] - 40 < response.text.__len__() < self.setting_fuzz['length'] + 40:
                    if self.validToAppend(response.status_code, response.text.__len__()):
                        self.indexes.append(data)

    def validToAppend(self, code, length) -> bool:
        if code == 200 and not self.setting_fuzz['content_and_length']:
            self.status_code_valid['captcha'] += 1
            return True
        elif code == 302 or code == 301 and self.setting_fuzz['show_302']:
            self.status_code_valid['moved'] += 1
            return True
        elif code == 403:
            self.status_code_valid['denied'] += 1
            if self.setting_fuzz['show_403']:
                return True
            return False
        elif code == 502 or code == 500 or code == 501:
            self.status_code_valid['crashed'] += 1
            return True
        return False

    def checkStatusCode(self):
        return VerifyRequestStatusCode(self.setting_fuzz, self.parent_setting, self.kw).run()

    def killFuzz(self):
        self.cancel = 1

