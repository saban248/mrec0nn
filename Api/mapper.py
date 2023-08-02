import requests
from PyQt5.QtCore import QThread, pyqtSignal

from Api.status_code import VerifyRequestStatusCode
from Api.analyzeAddr import clsAddress, HTTP_ERROR

PUNCH = '!#$%&()*+,;<=>?@[]"^`{|}'


def replacer(payload:list[str], tagE, tagR):
    for index, rep in enumerate(payload):
        payload[index] = rep.replace(tagE, tagR)
    return payload


def Searcher(payload, STag, CTags) -> list[str]:
    """
    at bs4 library there is implementation, this function was built for fun.
    searching... letter by letter
    like `Reverse stack`

    :param payload:
    :param STag: name of Start tag
    :param CTags: list: OPTIONS  -> the string that can be Closing Tag
    :return: list
    """
    # DEBUG
    assert type(CTags) is list
    assert CTags and STag, "empty list (CTag or STag)"

    LCollector = []
    collector = ""
    OpenTeg_target = ""
    for index, tg in enumerate(payload):

        # Start Collect letters
        for CheckPerOpenTag in STag:
            condition = CheckPerOpenTag == payload[index:index + len(CheckPerOpenTag)]
            if condition:
                OpenTeg_target = CheckPerOpenTag
            if condition or collector:
                collector += tg
                break

        # finish collect letters
        for CheckPerCloseTag in CTags:
            p0y = payload[index:index+len(CheckPerCloseTag)]
            if CheckPerCloseTag == p0y and (OpenTeg_target != p0y or not collector.__len__() == 1):
                x1 = collector+payload[index+1:index+len(CheckPerCloseTag)]
                x2 = x1[len(OpenTeg_target):-len(CheckPerCloseTag)]
                LCollector.append(x2) if x2 else None
                collector = ""
    # / END */
    if not LCollector:
        return 0
    if not LCollector.__len__() > 1:
        return "".join(LCollector)

    return LCollector


class ThreadMapper(QThread):

    emitFinish = pyqtSignal(int)
    emitError = pyqtSignal(str)
    emitOutput = pyqtSignal(list)

    def __init__(self, parent_setting, *args, **kwargs):
        super(ThreadMapper, self).__init__(*args, **kwargs)

        self.parent_setting = parent_setting
        del kwargs['parent']
        self.mapper = Mapper(self.parent_setting, *args, **kwargs)

    # noinspection PyUnresolvedReferences
    def run(self) -> None:

        result = self.mapper.Start()
        if isinstance(result, list):
            self.emitOutput.emit(result)
        else:
            self.emitError.emit(result)

        self.emitFinish.emit(1)


class Mapper(VerifyRequestStatusCode):

    def __init__(self, parent_setting, setting_fuzz=None,  **kwargs):
        super(Mapper, self).__init__( ({} if setting_fuzz is None else setting_fuzz ), parent_setting, kwargs)

        self.cancel = 0
        self.Indexes = []

    def Start(self):
        valid = self.run()
        if not valid[0]:
            self.Cancel()
            return valid[1]

        hipar_links = Searcher(self._get("", cls=0).text, ['href=', "src="], ['/>', " ", ">", "?"])
        if hipar_links:
            cls_index = replacer(hipar_links, "\"", "")
            self.Indexes = self._clear_indexes(cls_index)
        else:
            return "no links found!"

        return self.Indexes

    def _clear_indexes(self, indexes: list):
        domain = clsAddress(self.url)[0]
        if "www" in domain:
            domain = ".".join(domain.split(".")[1::])

        result = []
        for url in indexes:
            if ("http://" in url or "https://" in url) and domain in url:
                result.append(clsAddress(url)[-1])

            elif "http" not in url:
                if "/" in url and url.__len__() > 1:
                    result.append(url)
        return result

    def Cancel(self):
        self.cancel = 1


# https://www.itsafe.co.il/ http://18.158.46.251:8700
# d = Mapper({"url": "http://127.0.0.1/dvir"}, {'length':0})
# for indexes in d.Start():
#     print(indexes)
#
