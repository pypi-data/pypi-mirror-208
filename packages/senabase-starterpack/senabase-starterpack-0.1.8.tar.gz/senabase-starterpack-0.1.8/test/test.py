import json
import os
import shutil
import unittest
from pathlib import Path

import yaml

from senabase.starterpack.database import PostgreSQLHandler
from senabase.starterpack.log import SimpleLogger
from senabase.starterpack.telegram import TelegramHandler


class TestStarterpack(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestStarterpack, self).__init__(*args, **kwargs)

        self.cfg = {}  # configuration

        # Create config file if not exists
        cfgfile_path = 'dist/cfg.yaml'
        cfgfile_parentpath = Path(cfgfile_path).parent
        os.makedirs(cfgfile_parentpath, exist_ok=True)
        if not os.path.exists(cfgfile_path):
            with open(cfgfile_path, 'a+') as f:
                cfg_str = """
pg:
    host: 127.0.0.1
    port: 5432
    dbname: postgres
    usrid: userid
    pwd: userpassword
log:
    filename_prefix: senabase-starterpack
telegram:
    token: token_str
    chat_id: 1234
    """
                f.write(cfg_str)

        # Load config file
        with open(cfgfile_path, 'r') as f:
            self.cfg = yaml.load(f, Loader=yaml.FullLoader)

    def test_database(self):
        cfg = self.cfg['pg']

        pgh = PostgreSQLHandler()
        pgh.configure(**cfg)

        test_str = 'ABC'
        q1 = f"select '{test_str}' as str"
        rs = pgh.get(q1)

        # Check for expected value is returned.
        self.assertEqual(len(rs), 1)
        self.assertEqual(rs[0]['str'], test_str)

    def test_log(self):

        cfg = self.cfg['log']
        log_path = './logs'
        log_filename_prefix = cfg['filename_prefix']
        log_file = os.path.join(log_path, f'{log_filename_prefix}.log')

        #  Delete log files first.
        if os.path.exists(log_path):
            shutil.rmtree(log_path)

        log = SimpleLogger()
        log.configure(log_filename_prefix)

        # Check for log file is created.
        self.assertTrue(os.path.exists(log_file), 'Log file does not exists.')

    def test_telegram(self):
        cfg = self.cfg['telegram']
        token = cfg['token']
        chat_id = cfg['chat_id']
        message = 'Test message'
        telegram_handler = TelegramHandler()
        telegram_handler.configure(token)
        res = telegram_handler.send_message(chat_id, message)

        # Check for response status is HTTP OK
        self.assertEqual(res.status_code, 200)

        res_val = json.loads(res.text)

        # Check for returned message is same as requested message.
        self.assertEqual(res_val['ok'], True)
        self.assertEqual(res_val['result']['text'], message)


if __name__ == '__main__':
    unittest.main()
