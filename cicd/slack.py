import os
import io
import requests
import slackclient

EMOJI_V = ":heavy_check_mark:"
EMOJI_X = ":x:"


class Slack:
    def __init__(self, token):
        self._token = token

    def upload_file(self, filename, content, channel):
        response = requests.post(
            "https://slack.com/api/files.upload",
            params=dict(
                filename=filename,
                token=self._token,
                channels=[channel]),
            files=dict(file=(filename, io.BytesIO(content), os.path.splitext(filename)[1])))
        response.raise_for_status()
        parsed = response.json()
        if not parsed['ok']:
            raise Exception("Unable to upload file to slack: %s" % parsed)
        return parsed

    def post_message(self, text, channel, title=None, color=None, icon_emoji=None):
        attachment = dict(text=text, fallback=text)
        if title is not None:
            attachment['title'] = title
        if color is not None:
            attachment['color'] = color
        params = dict(
            method="chat.postMessage",
            channel=channel,
            attachments=[attachment])
        if icon_emoji is not None:
            params['icon_emoji'] = icon_emoji
        client = slackclient.SlackClient(self._token)
        response = client.api_call(**params)
        if not response['ok']:
            raise Exception("Unable to post message: %s" % response)
        return response


class Message:
    class Section(dict):
        def __init__(self, *args, **kwargs):
            super(Message.Section, self).__init__(*args, **kwargs)
            self['type'] = 'section'

        def empty(self):
            return 'text' not in self and 'fields' not in self

        def add_text(self, text, markdown=True, newline=True):
            line_feed = '\n' if newline else ''
            if 'text' not in self:
                self['text'] = dict(type="mrkdwn" if markdown else 'plain_text',
                                    text=text + line_feed)
            else:
                self['text']['text'] += text + line_feed

        def add_row(self, left, right, markdown=True):
            if 'fields' not in self:
                self['fields'] = []
            self['fields'].append(dict(type='mrkdwn' if markdown else 'plain_text',
                                       text=left))
            self['fields'].append(dict(type='mrkdwn' if markdown else 'plain_text',
                                       text=right))

    def __init__(self, token, **params):
        self._token = token
        self._blocks = []
        self._params = params

    def add_section(self, text=None, markdown=True):
        section = self.Section()
        if text is not None:
            section.add_text(text, markdown)
        self._blocks.append(section)
        return section

    def set(self, key, value):
        self._params[key] = value
        return self

    def post(self, **params):
        self._params.update(params)
        client = slackclient.SlackClient(self._token)
        blocks_to_send = [block for block in self._blocks if not block.empty()]
        response = client.api_call(method="chat.postMessage", blocks=blocks_to_send, **self._params)
        if not response['ok']:
            raise Exception("Unable to post message: %s" % response)
        return response
