import json
import threading
import time
from functools import partial
from threading import Thread, Event
from typing import TypedDict, Callable, Optional

from websocket import WebSocketApp, ABNF


class EulithSubscriptionException(Exception):
    pass


class SubscribeRequest(TypedDict):
    subscription_type: str
    args: dict


def global_on_error(ws, error, ew3):
    print(f'Websocket ERROR: message {error} on endpoint {ew3.eulith_data.eulith_url.replace("https://", "wss://")}')
    raise error


def global_on_close(ws, close_status_code, close_msg, ew3):
    print(f'Websocket connection closed with code {close_status_code} '
          f'and message {close_msg} on endpoint {ew3.eulith_data.eulith_url}')


def close_on_trigger(ws, message, kill_switch: Event):
    if kill_switch.is_set():
        ws.send(None, opcode=ABNF.OPCODE_CLOSE)


def subscribe_on_open(ws, ew3):
    ws.sock.ping(b'')
    try:
        for key, val in ew3.websocket_conn.subscriptions.items():
            resubscribe_payload = val.get('subscribe_payload', None)
            if resubscribe_payload:
                request_id = ew3.websocket_conn.next_request_id()
                resubscribe_payload['id'] = request_id
                ws.send(json.dumps(resubscribe_payload))
                ew3.websocket_conn.awaiting_subscription_id[request_id] = val
                ew3.websocket_conn.subscriptions.pop(key)
    except:
        pass


def global_message_handler(ws, message, ew3):
    result_dict = json.loads(message)
    request_id = result_dict.get('id', None)

    # there's currently no case where we would pass back an error and a subscription ID
    # should we pass subscription ID back if there's an error after a subscription is established?
    if 'error' in set(result_dict.keys()):
        with ew3.websocket_conn.lock:
            sub_info = ew3.websocket_conn.awaiting_subscription_id.get(request_id, None)
            if sub_info:
                ew3.websocket_conn.awaiting_subscription_id.pop(request_id)
                error_handler = sub_info.get('error_handler')
                error_handler(ws, message, ew3)
                return

    for rid, sub_id in ew3.websocket_conn.awaiting_unsub:
        if request_id == rid:
            status = result_dict.get('result', False)
            if status:
                ew3.websocket_conn.subscriptions.pop(sub_id)
                ew3.websocket_conn.awaiting_unsub.remove((rid, sub_id))
            return

    result = result_dict.get('result', {})
    if type(result) == dict:
        subscription_id = result.get('subscription')
    elif type(result) == str:
        subscription_id = result
    else:
        subscription_id = None

    with ew3.websocket_conn.lock:
        sub_info = ew3.websocket_conn.awaiting_subscription_id.get(request_id, None)
        if sub_info and subscription_id:
            subscription_handle = sub_info.get('subscription_handle', None)
            if subscription_handle:
                subscription_handle.set_sub_id(subscription_id)

            ew3.websocket_conn.subscriptions[subscription_id] = sub_info
            ew3.websocket_conn.awaiting_subscription_id.pop(request_id)

    message_handler = ew3.websocket_conn.subscriptions.get(subscription_id, {}).get('message_handler', None)
    error_handler = ew3.websocket_conn.subscriptions.get(subscription_id, {}).get('error_handler', None)
    if message_handler:
        message_handler(ws, message, ew3)
    else:
        error_handler(ws, {
            'error': f'did not find a valid message handler for subscription {subscription_id}'
        }, ew3)


class SubscriptionHandle:
    def __init__(self, request_id, eulith_ws_connection):
        self.rid = request_id
        self.sub_id = None
        self.wsc = eulith_ws_connection

    def set_sub_id(self, subscription_id: str):
        self.sub_id = subscription_id

    def unsubscribe(self):
        if not self.sub_id:
            raise EulithSubscriptionException("cant unsubscribe before the subscription ID is known. "
                                        "Must wait for the server to respond with a confirmed subscription ID.")
        else:
            with self.wsc.lock:
                rid = self.wsc.next_request_id()
                unsub_payload = {
                    'jsonrpc': '2.0',
                    'method': 'eth_unsubscribe',
                    'params': [self.sub_id],
                    'id': rid
                }
                self.wsc.socket.send(json.dumps(unsub_payload))
                self.wsc.awaiting_unsub.add((rid, self.sub_id))


class EulithWebsocketConnection:
    def __init__(self, ew3):
        self.ew3 = ew3
        self.socket = None
        self.thread_handle = None
        self.kill_event = None
        self.subscriptions = {}
        self.lock = threading.Lock()
        self.awaiting_subscription_id = {}
        self.awaiting_unsub = set()
        self.request_id = 5145

    def is_connected(self):
        return True if self.socket else False

    def next_request_id(self):
        self.request_id += 1
        return self.request_id

    def connect(self, on_error: Optional[Callable] = None,
                on_close: Optional[Callable] = None, reconnect_secs=5) -> (WebSocketApp, Thread, Event):
        kill_switch = Event()

        om = partial(global_message_handler, ew3=self.ew3)
        oe = partial(on_error if on_error else global_on_error, ew3=self.ew3)
        oc = partial(on_close if on_close else global_on_close, ew3=self.ew3)
        op = partial(close_on_trigger, kill_switch=kill_switch)
        oo = partial(subscribe_on_open, ew3=self.ew3)

        endpoint = self.ew3.eulith_data.eulith_url
        endpoint = endpoint.replace('http', 'ws')

        auth_headers = {
            'Authorization': f'Bearer {self.ew3.eulith_data.api_access_token.token}'
        }

        ws = WebSocketApp(endpoint, header=auth_headers, on_message=om,
                          on_close=oc, on_error=oe, on_open=oo, on_ping=op)

        thread = Thread(target=ws.run_forever, kwargs={
            'reconnect': reconnect_secs,
            'suppress_origin': True,
            'ping_interval': 5,
            'ping_timeout': 4
        })

        thread.start()

        while ws.last_pong_tm == 0:
            time.sleep(0.1)

        self.socket = ws
        self.thread_handle = thread
        self.kill_event = kill_switch

    def subscribe(self, subscribe_request: SubscribeRequest,
                  message_handler: Callable, error_handler: Callable) -> SubscriptionHandle:
        with self.lock:
            rid = self.next_request_id()
            subscription_handle = SubscriptionHandle(rid, self)

            if not self.is_connected():
                self.connect()

            subscribe_payload = {
                'jsonrpc': '2.0',
                'method': 'eulith_subscribe',
                'params': [subscribe_request],
                'id': rid
            }

            self.socket.send(json.dumps(subscribe_payload))

            self.awaiting_subscription_id[rid] = {
                'subscribe_payload': subscribe_payload,
                'message_handler': message_handler,
                'error_handler': error_handler,
                'subscription_handle': subscription_handle
            }

        return subscription_handle

    def disconnect(self):
        self.kill_event.set()
        self.thread_handle.join()
        self.socket = None
        self.thread_handle = None
        self.kill_event = None
