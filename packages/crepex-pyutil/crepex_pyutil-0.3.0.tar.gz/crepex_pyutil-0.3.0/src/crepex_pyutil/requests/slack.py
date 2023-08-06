import json
from typing import List, Union

import requests


class SlackMessageBuilder:
    """
    Slack message builder
    - Builder pattern 으로 구축, 사용
    - 생성 후 add_*** -> build -> send
    """

    def __init__(self, debug_channel: str, active=True, debug=False):
        self.active = active
        self.debug = debug
        self.debug_channel = debug_channel
        self.data = {}
        self.block = []

    @staticmethod
    def transform_text(text: str):
        return {"type": "mrkdwn", "text": text}

    def send(self, hook_url, **kwargs):
        url = hook_url

        if not self.active:
            return
        elif self.debug:
            url = self.debug_channel

        requests.post(
            url,
            data=self.data,
            headers={"Content-Type": "application/json"},
            **kwargs,
        )

    def build(self):
        self.data = json.dumps({"blocks": self.block})
        return self

    def add_divider(self):
        """
        구분선
        https://api.slack.com/reference/block-kit/blocks#divider
        """
        self.block.append({"type": "divider"})
        return self

    def add_text(self, text: Union[str, List[str]]):
        """
        섹션 형태로 텍스트 구성
        https://api.slack.com/reference/block-kit/blocks#section
        :param text: 문자열 목록 또는 문자열
        """
        if type(text) == list:
            fields = [self.transform_text(o) for o in text]
            self.block.append({"type": "section", "fields": fields})
        else:
            self.block.append({"type": "section", "text": self.transform_text(text)})

        return self

    def add_image(self, url, alt, **kwargs):
        """
        이미지 추가
        https://api.slack.com/reference/block-kit/blocks#image
        :param url: 이미지 URL (~3000)
        :param alt: 이미지 ALT text (~2000)
        :param kwargs: title, block_id (optional)
        """
        self.block.append(
            {
                "type": "image",
                "image_url": url,
                "alt_text": alt,
                **kwargs,
            }
        )
        return self
