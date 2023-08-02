import requests


def PayloadParams(payload) -> dict:
    """
    :param payload: Example "csrftoken=89udh283yruh9e2dij9sj&name=albertTest2"
    :return : str to dict,  dict to str
    """
    if type(payload) is str:
        return _PayloadJson(payload)
    else:
        return _PayloadHTTP(payload)


def _PayloadJson(params: str) -> dict:
    payload: dict = {}
    for js in params.split("&"):
        kv = js.split("=")
        payload[kv[0]] = kv[1]

    # /* finish */
    return payload


def _PayloadHTTP(params: dict) -> str:
    payload: str = ""
    for k, v in params.items():
        payload += f"{k}={v}&"

    return payload[0:-1]

