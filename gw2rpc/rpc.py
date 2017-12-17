"""
This is a modified version of GiovanniMCMXCIX's PyDiscordRPC
https://github.com/GiovanniMCMXCIX/PyDiscordRPC

MIT License

Copyright (c) 2017 GiovanniMCMXCIX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import asyncio
import json
import struct
import time
import logging

log = logging.getLogger(__name__)


class DiscordRPC:
    def __init__(self, client_id):
        self.ipc_path = r'\\?\pipe\discord-ipc-0'
        self.loop = asyncio.ProactorEventLoop()
        self.sock_reader: asyncio.StreamReader = None
        self.sock_writer: asyncio.StreamWriter = None
        self.client_id = client_id
        self.running = False
        self.last_update = time.time()
        self.last_payload = {}
        self.last_pid = None

    async def read_output(self):
        data = await self.sock_reader.read(1024)
        code, length = struct.unpack('<ii', data[:8])
        log.debug(f'OP Code: {code}; Length: {length}\nResponse:\n{json.loads(data[8:].decode("utf-8"))}\n')

    def send_data(self, op: int, payload: dict):
        payload = json.dumps(payload)
        data = self.sock_writer.write(struct.pack('<ii', op, len(payload)) + payload.encode('utf-8'))

    async def handshake(self):
        self.sock_reader = asyncio.StreamReader(loop=self.loop)
        reader_protocol = asyncio.StreamReaderProtocol(self.sock_reader, loop=self.loop)
        self.sock_writer, _ = await self.loop.create_pipe_connection(lambda: reader_protocol, self.ipc_path)
        self.send_data(0, {'v': 1, 'client_id': self.client_id})
        data = await self.sock_reader.read(1024)
        code, length = struct.unpack('<ii', data[:8])
        log.debug(f'OP Code: {code}; Length: {length}\nResponse:\n{json.loads(data[8:].decode("utf-8"))}\n')

    def send_rich_presence(self, activity, pid, force=False):
        if self.compare_payloads(activity, self.last_payload) and not force:
            return self.refresh()
        current_time = time.time()
        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "activity": activity,
                "pid": pid
            },
            "nonce": f'{current_time:.20f}'
        }
        self.send_data(1, payload)
        self.last_update = current_time
        self.last_payload = activity
        self.last_pid = pid
        self.loop.run_until_complete(self.read_output())

    def compare_payloads(self, p1, p2):
        def asset_compare(asset):
            return p1.get("assets", {}).get(asset) == p2.get("assets", {}).get(asset)
        assets = asset_compare("large image") and asset_compare("small_image_text")
        return p1.get("state") == p2.get("state") and assets and p1.get("details") == p2.get("details")

    def refresh(self):
        if time.time() - self.last_update >= 900:
            self.send_rich_presence(self.last_payload, self.last_pid, force=True)

    def close(self):
        self.running = False
        self.sock_writer.close()
        self.sock_writer: asyncio.StreamWriter = None
        self.loop.close()

    def start(self):
        self.loop = asyncio.ProactorEventLoop()
        self.running = True
        self.loop.run_until_complete(self.handshake())
