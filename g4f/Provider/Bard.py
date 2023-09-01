import json
import random
import re
from aiohttp import ClientSession

from .base_provider import AsyncProvider, get_cookies, format_prompt

class Bard(AsyncProvider):
    url = "https://bard.google.com"
    needs_auth = True
    working = True

    @classmethod
    async def create_async(
        cls,
        model: str,
        messages: list[dict[str, str]],
        proxy: str = None,
        cookies: dict = None,
        **kwargs
    ) -> str:
        prompt = format_prompt(messages)
        if proxy and "://" not in proxy:
            proxy = f"http://{proxy}"
        if not cookies:
            cookies = get_cookies(".google.com")

        headers = {
            'authority': 'bard.google.com',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://bard.google.com',
            'referer': 'https://bard.google.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'x-same-domain': '1',
        }

        async with ClientSession(
            cookies=cookies,
            headers=headers
        ) as session:
            async with session.get(cls.url, proxy=proxy) as response:
                text = await response.text()

            match = re.search(r'SNlM0e\":\"(.*?)\"', text)
            if not match:
                raise RuntimeError("No snlm0e value.")
            snlm0e = match.group(1)
            
            params = {
                'bl': 'boq_assistant-bard-web-server_20230326.21_p0',
                '_reqid': random.randint(1111, 9999),
                'rt': 'c'
            }

            data = {
                'at': snlm0e,
                'f.req': json.dumps([None, json.dumps([[prompt]])])
            }

            intents = '.'.join([
                'assistant',
                'lamda',
                'BardFrontendService'
            ])

            async with session.post(
                f'{cls.url}/_/BardChatUi/data/{intents}/StreamGenerate',
                data=data,
                params=params,
                proxy=proxy
            ) as response:
                response = await response.text()
                response = json.loads(response.splitlines()[3])[0][2]
                response = json.loads(response)[4][0][1][0]
                return response

    @classmethod
    @property
    def params(cls):
        params = [
            ("model", "str"),
            ("messages", "list[dict[str, str]]"),
            ("stream", "bool"),
            ("proxy", "str"),
        ]
        param = ", ".join([": ".join(p) for p in params])
        return f"g4f.provider.{cls.__name__} supports: ({param})"
