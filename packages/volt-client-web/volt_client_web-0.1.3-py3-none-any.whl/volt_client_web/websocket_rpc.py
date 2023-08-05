from pyee.base import EventEmitter
import json
import asyncio

class WebSocketRPC(EventEmitter):
    """
    Represents a WebSocket RPC client used to communicate with a WebSocket server.

    Parameters
    ----------
    id : str
        The identifier for this WebSocket RPC.
    websocket : WebSocket
        The WebSocket used to send and receive messages.
    method_name : str
        The name of the RPC method being called.
    metadata : dict
        Additional metadata associated with the RPC call.
    target_fingerprint : str
        A unique identifier for the target service.
    service : dict
        The service to which this RPC is addressed.
    send_func : function
        The function used to send messages over the WebSocket.
    recv_func : function
        The function used to receive messages over the WebSocket.

    Attributes
    ----------
    id : str
        The identifier for this WebSocket RPC.
    websocket : WebSocket
        The WebSocket used to send and receive messages.
    method_name : str
        The name of the RPC method being called.
    metadata : dict
        Additional metadata associated with the RPC call.
    target_fingerprint : str
        A unique identifier for the target service.
    service : dict
        The service to which this RPC is addressed.
    send_func : function
        The function used to send messages over the WebSocket.
    recv_func : function
        The function used to receive messages over the WebSocket.
    sent_count : int
        The number of messages sent by the client.
    response_count : int
        The number of messages received by the client.
    complete : bool
        Whether the RPC call has been completed.
    server_ended : bool
        Whether the server has ended the RPC call.
    client_ended : bool
        Whether the client has ended the RPC call.
    call_started : bool
        Whether the RPC call has started.
    receiving_task : asyncio.Task
        The task used to receive messages over the WebSocket.
    
    Methods
    -------
    async on_message()
        Receives messages over the WebSocket and forwards them to on_response().
    async on_response(response)
        Handles the response message from the server.
    finished()
        Returns True if the RPC call has been completed by both the client and the server.
    async end()
        Sends the client end message to the server to indicate the RPC call is over.
    async send(payload)
        Sends a message to the server.
    """
    def __init__(self, id, websocket, method_name, metadata, target_fingerprint, service, send_func, recv_func, quiet_mode = True) -> None:
        """
        Initializes the WebSocketRPC object.
        """
        super().__init__()
        self.id = id
        self.websocket = websocket
        self.method_name = method_name
        self.metadata = metadata
        self.target_fingerprint = target_fingerprint
        self.service = service
        self.send_func = send_func
        self.recv_func = recv_func

        self.sent_count = 0
        self.response_count = 0
        self.complete = False
        self.server_ended = False
        self.client_ended = False
        self.call_started = False
        self.quiet_mode = quiet_mode

        self.receiving_task = asyncio.create_task(self.on_message(), name=f"on_message for responder {self.id}")
        return
    
    async def on_message(self):
        """
        Coroutine that listens for incoming messages from the server.
        """
        while not self.complete:
            try:
                message = await self.websocket.recv()
                await self.recv_func(message)
            except Exception as err:
                return None # if problem receiving message, return and try again
        return

    async def on_response(self, response):
        """
        Handles responses received from the server.

        Parameters
        ----------
        response : dict
            The response received from the server, in the form of a dictionary.

        Raises
        ------
        Exception
            If the response contains a non-empty status message, an exception with the error message is raised.

        Returns
        -------
        None
        """
        self.response_count += 1

        if "method_payload" in response:
            # Received a payload for a live RPC call.
            response["method_payload"]["json_payload"] = json.loads(response["method_payload"]["json_payload"])

            # Interpret a non-empty status message as an error.
            if ("json_payload" in response["method_payload"] and
            "status" in response["method_payload"]["json_payload"] and
            "message" in response["method_payload"]["json_payload"]["status"]):
                raise Exception(response["method_payload"]["json_payload"]["status"]["message"])
            else:
                # Notify the callee that a payload has been received.
                self.emit("data", response["method_payload"]["json_payload"])
        elif "method_end" in response:
            # The server has closed their side of the stream.
            self.server_ended = True

            # Send client end.
            await self.end()

            if "error" in response["method_end"]:
                print(f"received error for call {self.id}: {response['method_end']['error']}")#
                self.emit("error", Exception(response['method_end']['error']))
            else:
                # Notify the callee that the RPC has ended.
                self.emit("end")
                self.complete = True # set complete flag so self.receiving_task may complete
        
    def finished(self):
        """
        Checks if both the client and server have ended the RPC.

        Returns
        -------
        bool
            True if both the client and server have ended the RPC, False otherwise.
        """
        return self.client_ended and self.server_ended

    async def end(self):
        """
        Sends the client end message to the server if the client has not already ended the RPC.

        Returns
        -------
        None
        """
        if self.client_ended:
            # Do nothing.
            return
        
        self.client_ended = True

        call_payload = {
            "id": self.id,
            "payload": {
                "method_end": {
                    "ended": True,
                }
            },
            "client_end": True,
        }
        if not self.quiet_mode:
            print("Server ended rpc call, sending client end message")
        await self.send_func(self.metadata, call_payload)

    async def send(self, payload):
        """
        Sends the given payload to the server.

        Parameters
        ----------
        payload : Any
            The payload to send to the server.

        Returns
        -------
        None
        """
        self.sent_count += 1
        if self.call_started:
            # We've already sent the initial request, so just send the payload.
            call_payload = {
                "id": self.id,
                "payload": {
                    "method_payload": {
                        "payload": payload,
                    }
                }
            }
        else:
            """We haven't sent the initial request yet, so send the call credentials and the payload.
            This is equivalent to the call metadata on a conventional grpc call."""
            call_payload = {
                "id": self.id,
                "token": self.metadata["token"],
                "target_fingerprint": self.target_fingerprint,
                "payload": {
                    "method_invoke": {
                        "method_name": self.method_name,
                        "service_id": self.service["service_description"]["host_service_id"] if self.service is not None else None,
                        "request": payload,
                    }
                }
            }

            self.call_started = True
        await self.send_func(self.metadata, call_payload)