import sys

import pexpect
from gns3fy import Node
from loguru import logger

from src.logger import def_context


def connect(context_name: str, section: str, part: str, node: Node, rules: list[list[str]], log: bool):
    with def_context(name=context_name, section=section, part=part):
        logger.info(f'Telnet start transmission')

        try:
            client = pexpect.spawn(f'telnet {node.console_host} {node.console}')

            client.logfile = None
            #client.logfile = sys.stdout.buffer
            client.sendline()

            for expect, send in rules:
                if log and client.logfile_read is None and expect == ':~':
                    client.logfile_read = sys.stdout.buffer
                client.expect(expect, timeout=600)

                if send is None:
                    break

                if send != '\n':
                    print('\r', end='', flush=True)
                    logger.info(f'> {send}')

                client.sendline(send)

            client.logfile = None
            client.sendline()
            client.close(force=True)
            print('\r', end='', flush=True)
            logger.info('Telnet end transmission')
        except Exception as e:
            logger.error(e)
            exit(1)