# Shree KRISHNAya Namaha
# 
# Author: Nagabhushan S N
# Date: 22/05/21
import re
import time
import datetime
import traceback
from typing import List

import simplejson
import pdfkit

from pathlib import Path
from tqdm import tqdm
from urlextract import URLExtract

this_filepath = Path(__file__)
this_filename = this_filepath.stem

MESSAGE_START_PATTERN = r'\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2} [ap]m - '
MATCH_PATTERN = f'^{MESSAGE_START_PATTERN}[\s\S]+?(?={MESSAGE_START_PATTERN})'


class ChatParser:
    messages: List[str]

    def __init__(self, chat_path: Path, output_dirpath: Path, verbose_log: bool = True):
        self.messages = self.parse_chat(chat_path)
        self.output_dirpath = output_dirpath
        self.verbose_log = verbose_log
        self.url_extractor = URLExtract()
        self.pdfkit_options = {
            'images': '',
            'no-stop-slow-scripts': '',
        }
        return

    @staticmethod
    def parse_chat(chat_path: Path):
        with open(chat_path.as_posix(), 'r') as chat_file:
            lines = chat_file.readlines()
        all_content = ''.join(lines)
        messages = re.findall(MATCH_PATTERN, all_content, flags=re.MULTILINE)  # This misses the last message
        for message in messages:
            all_content = all_content.replace(message, '')
        messages.append(all_content)
        return messages

    def save_messages(self):
        for i, message in enumerate(self.messages):
            if 'quora.com' in message:
                self.parse_quora_message(message, i)
            elif ('Messages and calls are end-to-end encrypted' in message) or \
                    ('You created a broadcast list' in message) or \
                    ('added to the list' in message) or \
                    ('removed from the list' in message) or \
                    ('<Media omitted>' in message):
                pass
            else:
                print(f'Unable to parse message: {message}')
        return

    def parse_quora_message(self, message, num):
        urls = self.url_extractor.find_urls(message)
        assert len(urls) == 1
        url = urls[0]
        output_path = self.output_dirpath / f'{num}.pdf'

        # PDF kit
        pdfkit.from_url(url, output_path, options=self.pdfkit_options)
        return


def demo1():
    chat_path = Path('../Data/WhatsApp Chat with Marvel Broadcast Group.txt')
    output_dirpath = Path('../out/Marvel')
    output_dirpath.mkdir(parents=True, exist_ok=True)
    ChatParser(chat_path, output_dirpath).save_messages()
    return


def main():
    demo1()
    return


if __name__ == '__main__':
    print('Program started at ' + datetime.datetime.now().strftime('%d/%m/%Y %I:%M:%S %p'))
    start_time = time.time()
    try:
        main()
        run_result = 'Program completed successfully!'
    except Exception as e:
        print(e)
        traceback.print_exc()
        run_result = str(e)
    end_time = time.time()
    print('Program ended at ' + datetime.datetime.now().strftime('%d/%m/%Y %I:%M:%S %p'))
    print('Execution time: ' + str(datetime.timedelta(seconds=end_time - start_time)))
