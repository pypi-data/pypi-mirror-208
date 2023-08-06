import json
import os
import sys
import tempfile

import edge_tts
import requests
from dotenv import load_dotenv

load_dotenv()


async def requestAudioID(word: str, locale: str = "en-GB", by: str = "default") -> str:
    """

    :param word:
    :param locale:
        - en-GB or en-US
    :param by:
        - default 使用Markji自带的tts
          youdao 使用有道的发音api
    :return:
    """
    try:
        if by == "default":
            return f"[Audio#ID/{_getIdFromUrl(_tts(word, locale))}#]"
        if by == "youdao":
            codes = {"en-GB": 1, "en-US": 2}
            return f"[Audio#ID/{_uploadVoice(_getYoudaoVoice(word, codes[locale]))}#]"
        if by == "edge":
            return f"[Audio#ID/{_uploadVoice(await _get_edge_tts(word))}#]"

    except ValueError as e:
        print(e)
        sys.exit(1)


def _tts(word: str, locale: str = "en-GB"):
    token = os.getenv("MARKJI_TOKEN")
    if token is None:
        raise ValueError("【错误】MARKJI_TOKEN未提供")
    url = "https://www.markji.com/api/v1/files/tts"

    payload = json.dumps({
        "content_slices": [
            {
                "text": word,
                "locale": locale
            }
        ]
    })
    headers = {
        'token': token,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if (response.status_code == 400):
        raise ValueError("【错误】请检查输入的单词文件是否有问题")
    if (response.status_code == 401):
        raise ValueError("【错误】MARKJI_TOKEN错误，请检查")
    return json.loads(response.text)['data']['url']


def _getIdFromUrl(wordUrl: str):
    token = os.getenv("MARKJI_TOKEN")
    url = "https://www.markji.com/api/v1/files/url"

    payload = json.dumps({"url": wordUrl})
    headers = {
        'token': token,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)['data']['file']['id']


def _getYoudaoVoice(word: str, types: int = 1):
    import requests

    url = f"https://dict.youdao.com/dictvoice?audio={word}&type={types}"

    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(response.content)
    return temp_file.name


async def _get_edge_tts(text: str, voice: str = "en-GB-SoniaNeural", rate: str = "+25%") -> str:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name


def _uploadVoice(filepath: str):
    token = os.getenv("MARKJI_TOKEN")
    if token is None:
        raise ValueError("【错误】MARKJI_TOKEN未提供")

    url = "https://www.markji.com/api/v1/files"

    payload = {}
    files = [
        ('file', (os.path.basename(filepath), open(filepath, 'rb'), 'audio/mpeg'))
    ]
    headers = {
        'token': token,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if (response.status_code == 401):
        raise ValueError("【错误】MARKJI_TOKEN错误，请检查")

    return json.loads(response.text)['data']['file']['id']


if __name__ == '__main__':
    print(_uploadVoice(_getYoudaoVoice("apple")))
