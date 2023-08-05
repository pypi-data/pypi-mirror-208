from .crypto_utils import (get_key, aes_encrypt, aes_decrypt, get_public_key_pem, 
calc_fingerprint, get_identity_token, load_public_key, load_x509_certificate)
from .websocket_rpc import WebSocketRPC

from copy import deepcopy
import json
import asyncio
from websockets.client import connect

class VoltClient():
    def __init__(self, config):
        self.config = config

    async def initialise(self,  overrideAddress: str = None, quietMode = True):
        self.keyPair = get_key(self.config["credential"]["key"])
        self.quietMode = quietMode

        if "public_key" in self.config["volt"]:
            self.voltPublicKey = load_public_key(self.config["volt"]["public_key"])
        elif "ca_pem" in self.config["volt"]:
            # extract the target Volt public key from the Volt CA X.509 certificate.
            certDecoded = load_x509_certificate(self.config["volt"]["ca_pem"])
            self.voltPublicKey = certDecoded.public_key()

        if "fingerprint" in self.config["volt"]:
            self.voltFingerprint = self.config["volt"]["fingerprint"]
        else:
            # Create a fingerprint of the Volt public key. We currently use this to route to the correct
            # Volt when tunnelling, but eventually we will use a DID here.
            pem_binary = get_public_key_pem(self.voltPublicKey)
            self.voltFingerprint = calc_fingerprint(pem_binary).decode()

        # Keep track of all active RPCs.
        self.activeRPCs = {}
        self.invokeId = 0
        return await self.initialise_socket(overrideAddress)
    
    async def initialise_socket(self, overrideAddress: str = None):
        """
        Initialises the base websocket. If no Relay address is given, the Volt local address
        is used, as specified in the configuration, but it will be assumed that the web socket
        server port is the Volt GRPC server port + 2.
        """
        self.relaying = "relay" in self.config["volt"]

        connectURL = overrideAddress
        if connectURL is None:
            if self.relaying:
                if "http_address" in self.config["volt"]["relay"]:
                    connectURL = self.config["volt"]["relay"]["http_address"]
                else:
                    connectURL = self.config["volt"]["relay"]
            else:
                connectURL = self.config["volt"]["http_address"]
        
        if connectURL is None:
            raise ValueError("no Volt address and no relay")
        
        # Determine the websocket protocol to use.
        hasProtocal = "://" in connectURL
        if not hasProtocal:
            raise(f"missing protocol in connect URL {connectURL}")
    
        # Transform any http protocol into the websocket equivalent.
        parts = connectURL.split(":")
        parts[0] = parts[0].replace("http", "ws")
        wsURL = ":".join(parts)

        self.wsApiUrl = f"{wsURL}/api"
        
        self.websocket = await connect(self.wsApiUrl)
        return

    async def send_encrypt(self, metadata: dict, msg: dict):
        """
        Modify the outgoing message to use the json_request or json_payload properties as appropriate.
        This allows clients to use the interfaces as defined by the protobuf (and documentation) and
        transparently converts the payloads into a format required by the Volt websocket server.

        """
        payload = deepcopy(msg["payload"])
        if "method_invoke" in payload:
            if "request" in payload["method_invoke"]:
                # Stringify the invocation payload in 'method_invoke.json_request'
                payload["method_invoke"]["json_request"] = json.dumps(payload["method_invoke"]["request"])
                del payload["method_invoke"]["request"]
            else:
                payload["method_invoke"]["json_request"] = json.dumps({})
        elif "method_payload" in payload:
            if "payload" in payload["method_payload"]:
                # Stringify the in-flight payload in 'method_payload.json_payload'.
                payload["method_payload"]["json_payload"] = json.dumps(payload["method_payload"]["payload"])
                del payload["method_payload"]["payload"]
            else:
                payload["method_payload"]["json_payload"] = json.dumps({})


        # Now stringify the entire payload.
        payloadJSON = json.dumps(payload)
        msg_to_send = deepcopy(msg)
        del msg_to_send["payload"]

        # Encrypt the payload using the symmetric key in the call metadata.
        msg_to_send["json_payload"] = aes_encrypt(
            metadata["shared_key"]["key"],
            metadata["shared_key"]["iv"],
            payloadJSON.encode("utf-8")
        ).decode()

        await self.websocket.send(json.dumps(msg_to_send))
        return
    
    async def receive_decrypt(self, msg: dict):
        """
        Decrypts a message received from the volt, retrieves the associated RPC, if active, using the invoke_id
        and passes the message to the on_response method of the RPC.
        
        Parameters:
        -----------
        msg : dict
            The message received from the remote endpoint.

        Raises:
        -------
        Exception:
            If there is an error in the response message or there is no active RPC with the received invoke_id.

        Returns:
        --------
        None
        """
        try:
            invoke_response = json.loads(msg)
            if "error" in invoke_response:
                raise(Exception(invoke_response["error"]))
            else:
                # Lookup the RPC this message is destined for.
                try:
                    rpc = self.activeRPCs[int(invoke_response["invoke_id"])]
                except KeyError:
                    print(f"received packet for non-active call with id: {invoke_response['invoke_id']}")
                    raise(ValueError(f"received packet for non-active call with id: {invoke_response['invoke_id']}"))
            # Decrypt the payload using the symmetric key in the call metadata.
            digest = aes_decrypt(
                rpc.metadata["shared_key"]["key"],
                rpc.metadata["shared_key"]["iv"],
                invoke_response["json_payload"],
            )
            response = json.loads(digest)

            # Notify the RPC callee of the response.
            await rpc.on_response(response)

            # If the call has ended, remove it from the active RPCs.
            if rpc.finished():
                if not self.quietMode:
                    print(f"RPC call with id: {rpc.id} ended after {rpc.sent_count} sent messages and {rpc.response_count} responses")
                del self.activeRPCs[rpc.id]

        except Exception as error:
            print(f"failure decrypting message: {error}")
            raise(error)

    def get_call_metadata(self, target_host_audience = None, target_host_key = None):
        # Default the audience to the Volt id.
        target_audience = self.config["volt"]["id"]
        if target_host_audience is not None:
            target_audience = target_host_audience
        
        # Default the encryption key to the Volt public key.
        target_key = self.voltPublicKey
        if target_host_key is not None:
            target_key = load_public_key(target_host_key)
        # Create a Volt identity token using the client key pair.
        return get_identity_token(self.keyPair, target_key, target_audience, True)

    async def call_internal(self, method_name: str, request: object = None, service: object = None):
        """
        Packages the provided request into a JSON object, encrypts it and sends it to the Volt websocket server.
        
        Parameters
        ----------
        method_name: string
            The fully-qualified method name, e.g. "/tdx.volt_api.volt.v1.VoltAPI/GetResource"
        request: object, optional
            The request object matching the interface defined in the method protobuf.
        service: object, optional
            Service definition, only required for external services, i.e. those not hosted on the Volt.
        
        Returns
        -------
        WebSocketRPC: WebSocketRPC
            The WebSocketRPC object created for this call
        """
        try:
            # Determine if the service is relayed. A relayed service is one that is hosted by a different 'server' than the Volt.
            # In this case, the RPC is relayed through the Volt.
            if service is not None:
                is_service_relayed = service["service_description"]["host_type"] == "SERVICE_HOST_TYPE_RELAYED"

                # Create a token for the method invocation, use the service host details if the service is relayed, otherwise
                # the credentials will default to those of the Volt.
                meta_token = self.get_call_metadata(
                    service["service_description"]["host_client_id"],
                    service["service_description"]["host_public_key"],
                )
                if is_service_relayed:
                    target_fingerprint.append(service["service_description"]["host_fingerprint"])
            else:
                meta_token = self.get_call_metadata()

            target_fingerprint = []
            if self.relaying:
                # If we are relaying, we need to add the relay Volt fingerprint as an interim target (the first hop).
                target_fingerprint.append(self.voltFingerprint)

            self.invokeId += 1
            # instantiate rpc class instance
            rpc = WebSocketRPC(
                self.invokeId,
                self.websocket,
                method_name,
                meta_token,
                target_fingerprint,
                service,
                self.send_encrypt,
                self.receive_decrypt,
            )
            self.activeRPCs[rpc.id] = rpc

            # There may not be an initial request, e.g. in the case of a streaming call.
            if request is not None:
                # Allow callee to attach event handlers before we actually send the initial payload.
                await rpc.send(request)
        except Exception as error:
            print("Error in call_internal: ", error)
            # self.receiving_task.cancel() # This task must be cancelled for the error to be raised!
            raise(error)
        return rpc

    async def unary_call(self, method_name: str, request: object, service: object = None) -> asyncio.Future:
        """
        Issues a unary call to the Volt websocket server.

        Parameters
        ----------
        method_name : string
            The fully-qualified method name, e.g. "/tdx.volt_api.volt.v1.VoltAPI/GetResource"
        request : object
            request the request object matching the interface defined in the method protobuf.
        service : object, optional
            service optional service definition, only required for external services, i.e. those not hosted on the Volt.

        Returns
        -------
        response_future: asyncio.Future
            future which will resolve to the response received from the RPC.
        """
        future = asyncio.Future()
        if method_name is None and request is None:
            raise(ValueError("Invalid Arguments"))
        response = None

        rpc = await self.call_internal(method_name, request, service)

        @rpc.on("error")
        def error_handler(error):
            nonlocal future
            future.set_exception(error)
        
        @rpc.on("data")
        def data_handler(payload):
            nonlocal response
            response = payload

        @rpc.on("end")
        def end_handler():
            nonlocal future
            future.set_result(response)

        return future
    
    async def streaming_call(self, method_name: str, request: object = None, service: object = None) -> asyncio.Future:
        """
        Issues a streaming (i.e. client-stream, or bi-directional) call to the Volt websocket server.

        Parameters
        ----------
        method_name : string
            The fully-qualified method name, e.g. "/tdx.volt_api.data.v1.SqliteDatabaseAPI/Execute"
        request : object, optional
            request the request object matching the interface defined in the method protobuf.
        service : object, optional
            service optional service definition, only required for external services, i.e. those not hosted on the Volt.

        Returns
        -------
        response_future: asyncio.Future
            future which will resolve to the response received from the RPC.
        """
        if method_name is None:
            raise(ValueError("Invalid Arguments"))
        rpc = await self.call_internal(method_name, request, service)
        return rpc

    """
    RESOURCE API
    """

    async def CanAccessResource(self, request: dict) -> asyncio.Future:
        future = await self.unaryCall("/tdx.volt_api.volt.v1.VoltAPI/CanAccessResource", request)
        return await future
    
    async def Connect(self) -> asyncio.Future:
        return await self.streaming_call("/tdx.volt_api.volt.v1.VoltAPI/Connect")
    

    async def DeleteResource(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/DeleteResource", request)
        return await future

    async def DiscoverServices(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/DiscoverServices", request)
        return await future

    async def GetResource(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetResource", request)
        return await future

    async def GetResources(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetResources", request)
        return await future

    async def GetResourceAncestors(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetResourceAncestors", request)
        return await future

    async def GetResourceDescendants(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetResourceDescendants", request)
        return await future

    async def RequestAccess(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/RequestAccess", request)
        return await future

    async def SaveResource(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SaveResource", request)
        return await future

    async def SaveResourceAttribute(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SaveResourceAttribute", request)
        return await future

    async def SetServiceStatus(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SetServiceStatus", request)
        return await future

    """
    FILE API
    """

    async def DownloadFile(self, request: dict) -> asyncio.Future:
        return await self.server_streaming_call("/tdx.volt_api.volt.v1.FileAPI/DownloadFile", request)

    async def GetFile(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.FileAPI/GetFile", request)
        return await future

    async def GetFileDescendants(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.FileAPI/GetFileDescendants", request)
        return await future

    async def UploadFile(self) -> asyncio.Future:
        return await self.streaming_call("/tdx.volt_api.volt.v1.FileAPI/UploadFile")

    """
    VOLT MANAGEMENT API
    """

    async def Bind(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/Bind", request)
        return await future

    async def DeleteAccess(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/DeleteAccess", request)
        return await future

    async def DeleteVolt(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/DeleteVolt", request)
        return await future

    async def GetAccess(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetAccess", request)
        return await future

    async def GetBindings(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetBindings", request)
        return await future

    async def GetIdentities(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetIdentities", request)
        return await future

    async def GetIdentity(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetIdentity", request)
        return await future

    async def GetIdentityToken(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetIdentityToken", request)
        return await future

    async def GetPolicy(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetPolicy", request)
        return await future

    async def GetSettings(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/GetSettings", request)
        return await future

    async def Invoke(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/Invoke", request)
        return await future

    async def SaveAccess(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SaveAccess", request)
        return await future

    async def SaveIdentity(self, request: dict) -> asyncio.Future:
        future = self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SaveIdentity", request)

    async def SaveSettings(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SaveSettings", request)
        return await future

    async def SetAccessRequestDecision(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SetAccessRequestDecision", request)
        return await future

    async def SetBindingDecision(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SetBindingDecision", request)
        return await future

    async def Shutdown(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/Shutdown", request)
        return await future

    async def SignVerify(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.volt.v1.VoltAPI/SignVerify", request)
        return await future

    """
    Wire API
    """

    async def PublishWire(self, request: dict) -> asyncio.Future:
        return await self.streaming_call("/tdx.volt_api.volt.v1.WireAPI/PublishWire", request)

    async def SubscribeWire(self, request: dict) -> asyncio.Future:
        return await self.streaming_call("/tdx.volt_api.volt.v1.WireAPI/SubscribeWire", request)


    """
    Database API
    """

    async def BulkUpdate(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.data.v1.SqliteDatabaseAPI/BulkUpdate", request)
        return await future

    async def CreateDatabase(self, request: dict) -> asyncio.Future:
        future = await self.unary_call("/tdx.volt_api.data.v1.SqliteServerAPI/CreateDatabase", request)
        return await future

    async def SqlExecute(self, request: dict, service: dict = None) -> asyncio.Future:
        return await self.streaming_call("/tdx.volt_api.data.v1.SqliteDatabaseAPI/Execute", request, service)

    async def SqlExecuteJSON(self, request: dict, service: dict = None) -> asyncio.Future:
        future = asyncio.Future()
        call = await self.SqlExecute(request, service)

        header = None
        rows = []
        @call.on("error")
        def error_handler(error):
            nonlocal future
            future.set_exception(error)
        
        @call.on("data")
        def data_handler(response):
            nonlocal header, rows
            if "header" in response:
                header = response["header"]
            elif "row" in response:
                row = response["row"]
                
                dictionary = {}

                for i in range(0, len(header["column"])):
                    column = header["column"][i]
                    cell = row["column"][i]

                    if "null" in cell:
                        dictionary[column["name"]] = None
                    elif "text" in cell:
                        dictionary[column["name"]] = cell["text"]
                    elif "integer" in cell:
                        dictionary[column["name"]] = int(cell["integer"])
                    elif "real" in cell:
                        dictionary[column["name"]] = float(cell["real"])
                    elif "blob" in cell:
                        dictionary[column["name"]] = cell["blob"]
                    else:
                        dictionary[column["name"]] = f"unrecognised data type: {column['type']}"

                rows.append(dictionary)

        @call.on("end")
        def end_handler():
            nonlocal future, rows
            future.set_result(rows)

        return await future

    async def ImportCSV(self, request: dict) -> asyncio.Future:
        return await self.streaming_call("/tdx.volt_api.data.v1.SqliteDatabaseAPI/ImportCSV", request)


