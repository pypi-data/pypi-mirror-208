[![PyPI version](https://badge.fury.io/py/volt_client_web.svg)](https://badge.fury.io/py/volt_client_web)

# TDX volt python websocket client API.

## Configuration

In order to be able to initialise a connection to a Volt, you will need to obtain a [client configuration](https://docs.tdxvolt.com/en/reference/connection).

Example client connection object, obtained from the **fusebox** identity dialog:

```python
BobsConfig = {
  "client_name": "Bob",
  "credential": {
    "client_id": "25d050b9-5270-441e-920b-de07578394a9",
    "key": "-----BEGIN ENCRYPTED PRIVATE KEY-----\nMIIFHDBOBgkqhkiG9w0BBQ0wQTApBgkqhkiG9w0BBQwwHAQIRalkrxf/Lt0CAggA\nMAwGCCqGSIb3DQIJBQAwFAYIKoZIhvcNAwcECADS3HqZSdqbBIIEyFH7ooxVlpVn\nxVWA/e32E322VDc/FnlDlUkBm7C4haHdbgIsLSa0AhbazAgI45ibCg9PapD4uKQO\nx1X8NyyxwqsFTYHtX3cxtgY7I3Q2iM7jvyDlvjzc68Q0o0eE7Xk7Et4hEd4aiD3I\nt9EgIsNnSIHXbnXKTYrYD3P939AyQE5wECgKrmEXq/6ymbeBkTcYRg6tqcW9otjs\nuvRgfl5+QFpxE9rydMn0Yjm+wp5L6j2oD/yVTPVNkEKBgefngeqaj3cCsPDxFVOa\n/zBBFb17Kyn6eGga4pUNyg0xKi8TjYHcH5k7GzN6MHjaIVlls0TbbBHk1/tfrfF3\nSL26162J2qHmR4vosOtTzPCNYVlT85NVL3PO/xN1OTsoz6mjP5sScgoTnzi48B1s\nqyl4BMjpkK7j/KwsaVnEdNog+UVO/4lSbrM86KzwH9O6Xuv4WeIIC3sET+v8nQwq\nVNc3vXjDleRJbPONollHt/CLErkhh2sh6CguDFqqJlr+HYyDhbVBzw57jLEmE51M\npeK+LyaX/N2TxrXlIF774TOuEV6NzbPldIn0I4XcCXZhXN0stTiH6LPKS3CMdZTy\nKNgyRAsFXRfQ3F0A9MPqbRcxmyA7v/kLtukZ6ib33B6eY049SlduhbI0eKWt1jqs\nv05o6gDiLyYsyAzzMzl+OvRsPXyRZ6xVhI59uWBM9/EW8JKWwZ09mJGJ1A3tEpT4\nidka0Vfvy3XYL3KZKYD6u/NqpqfS7KW37C4iwtXHWUCLuFsA0HLD4SZOCen2b8fZ\nTNcbfR+brR5KqCrkK40NuejheQWlQi/eLYsCooTHRfpXPF2mQZJRgKxefoPFD6MZ\nWtoW97u10lRCWB1vuTlkq79uwyY+sqY0qTuWxeBdD9zmJeBJkR/QpdTlBUwRTlaQ\nMw529N/5N0haA3PJfwDwEV1Gv5BMNGIda8zx8BG+qv3plvWSUS0YTTGRBTl8GLQ5\nHKMbmTP41544UpcFHKCTtlUKO04rM8U9y4tLSxQp4Xw84fVw4MFNYyd8MLtYqc9j\nH93MGjHY3jx8PedEE8EaSX+JAh3cRYkD9+k9CswDnWxeQ0SIvLz0qL7Y82davVdO\nyOvkvCM7WzuvgMjfIZDGEVsoh4zI7PmVluUXW5SNtrQJhcLn8DsA4FCAXYaWGKXR\ndTupWI9kfCA+7f31ZNkrGUQ+CQFIrDozZzLbNqFv+QODirMIGYNsgeiqbSo1CXHR\n+/L5dc5ZtCK5AWKglgXOgWo2qxTEq9LaYWa6MiPaH3rwMqp9/r7HVsxfDJI0v1z2\n0hGfSkO47NnhHKsjTHfHCoDi7vC3a+w9T4tS/zm1VL9+Ay9uHi4Svq9KVexKYv5J\nim4a91CSIxfsMhN4t3UiciZz8NgU8mfbaZOcL6T1NDFZhT+1HngifCoM8g/Al0J7\nILiT8qNx7e0+TSRKreeGiWSUCJrRykx5Wk/8dCKsKx4hNrXTDlTA6w/ByduO4zKq\n/lXQQfRik1rVSj2Vkt1Jp15hwTL9o7OarmqgpWB5P4iBchEg9hSB70BSM7axK1wS\nxX58fGAQaws4NvNquUxSG3QGuxA2I6AfZeYuyH8x/Vy2MjBtOEopmxVVWHpdGPzW\nf42MsgXLVz6+SBAIc+beTw==\n-----END ENCRYPTED PRIVATE KEY-----\n",
  },
  "volt": {
    "id": "9a5944eb-1942-406e-a553-39b4220cbf94",
    "display_name": "Bob's Volt",
    "address": "192.168.1.194:50393",
    "public_key":
      "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAshZ/IqKr1y0TeMgT4l4f\nc/LrCCjg+lIXD4FE9Na3kL0kRTSwda6FsGM4EmuU0NVK+UZ6ViFEhrgA4DCbMf8h\nefuFcWWfHq17zzkdI65vI1Lh9qdKzYNK0FZ3pKoVQyXtpdomZ8rChosFpdDRm1gS\nmV4sTPvKzsFHSTxcOlHRZ/CMtuS09cPvWuuJ4Lm3VmIr70wYSVfC/78SxJYHGYDj\nwkaBqqBwNxIamxO4dwJ8azpdNLnBEeSnhzt2OP2dLu82l1IdjzJlbEWWlL3R1pdG\n55lf/Y9CySAMQyupbiKX1sOPZ1MWWsweAZNMChQtt8hup67vJV4/MOuLeLEF8em9\ncwIDAQAB\n-----END PUBLIC KEY-----\n",
    "fingerprint": "5M1aCpnijWbmibq748AHnyG1qgpHMFmLi5UUeaGBGo8t",
    "ca_pem":
      "-----BEGIN CERTIFICATE-----\nMIIDojCCAoqgAwIBAgIEG/pk5zANBgkqhkiG9w0BAQsFADBxMQswCQYDVQQGEwJH\nQjEUMBIGA1UEBwwLU291dGhhbXB0b24xGjAYBgNVBAoMEW5xdWlyaW5nTWluZHMg\nTHRkMTAwLgYDVQQDDCdjYS45YTU5NDRlYi0xOTQyLTQwNmUtYTU1My0zOWI0MjIw\nY2JmOTQwHhcNMjIwOTE1MTQxNDI1WhcNMjMwOTE1MTQxNDI2WjBxMQswCQYDVQQG\nEwJHQjEUMBIGA1UEBwwLU291dGhhbXB0b24xGjAYBgNVBAoMEW5xdWlyaW5nTWlu\nZHMgTHRkMTAwLgYDVQQDDCdjYS45YTU5NDRlYi0xOTQyLTQwNmUtYTU1My0zOWI0\nMjIwY2JmOTQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCyFn8ioqvX\nLRN4yBPiXh9z8usIKOD6UhcPgUT01reQvSRFNLB1roWwYzgSa5TQ1Ur5RnpWIUSG\nuADgMJsx/yF5+4VxZZ8erXvPOR0jrm8jUuH2p0rNg0rQVnekqhVDJe2l2iZnysKG\niwWl0NGbWBKZXixM+8rOwUdJPFw6UdFn8Iy25LT1w+9a64ngubdWYivvTBhJV8L/\nvxLElgcZgOPCRoGqoHA3EhqbE7h3AnxrOl00ucER5KeHO3Y4/Z0u7zaXUh2PMmVs\nRZaUvdHWl0bnmV/9j0LJIAxDK6luIpfWw49nUxZazB4Bk0wKFC23yG6nru8lXj8w\n64t4sQXx6b1zAgMBAAGjQjBAMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQD\nAgEGMB0GA1UdDgQWBBQNruu/5F1KEvJYHz5hmlfyryQhOjANBgkqhkiG9w0BAQsF\nAAOCAQEAm7mtXgQTftbcN05wQlStJ9IY+PaKkrvXJbJyl9PXOVgw5XNb9qTBzRl+\nTuEdK9N054jxHmkH9bqXObCLp/mo2xbQoavG87tILGMilv2VxEyKKzUaYc2IshYR\nY3zGT+QqC7IIfZHjVOgdc3+wwgm8ntRCYS23Z10+sE5o4lZGxiUkrGod1kjEKOaD\n5AiJ9bC3rI/tAapn14GemzsCagvVY8WzP8GW6WVz+pQCoJvy9jsHkQIq9djpzx29\nJ0hg12H9d2InnsJ8QdUIzbSPwyD8H+upKVtQZ/fVcZd3NtAuR6xo2yG3aSumdhmV\nrBJ5F7SB7WXo5/z0aXxYvCcrUqLgxA==\n-----END CERTIFICATE-----\n",
  },
}
```

## Connection

Create a **tdx Volt** instance to enable Bob to connect to the Volt:

```python
import asyncio # needed for async / await calls
from volt_client_web import VoltClient

config = ...

volt_client = VoltClient(config)
```

Now attempt to initialise the **tdx Volt** connection, to run async code in a python script you will need to create an async function and run it using asyncio:

```python
import asyncio # needed for async / await calls
from volt_client_web import VoltClient

config = ...

async def main():
  volt_client = VoltClient(config)
  await volt_client.initialise()

asyncio.run(main())
```

If initialisation fails, an error will be thrown.

## API call

Once initialised successfully, you can issue any API call.

Refer to the [API documentation](https://docs.tdxvolt.com/en/api/volt_api) for details of the method names and corresponding request and response messages. Each API method expects a dictionary representing the request(s) as input, and returns a dictionary as indicated by the response message type. The dictionary of the protobuf message format is intuitive.

In the example below, we retrieve the resource associated with Bob’s home folder:

```python
import asyncio # needed for async / await calls
from volt_client_web import VoltClient

config = ...

async def main():
    volt_client = VoltClient(config)
    await volt_client.initialise()
    result = await volt_client.getResource({ "resourceId": config["credential"]["client_id"] })
    print(result["resource"])

asyncio.run(main())
```

## Unary calls

All unary calls return a promise that will either resolve with a dictionary matching that defined by the API protobuf, or reject if there is a problem with the grpc transport or an error status on the response object. The above API call example is a unary call.

## Streaming calls
The promise model does not fit well with streaming calls since they are long-lived.

For this reason, all streaming calls (client streaming, server streaming, and bi-directional streaming) return a call object that is used to manage the call.

The call object emits events as interactions with the underlying websocket occur, and there are 3 events of interest:

- “error” emitted when an error occurs on the call
- “data” emitted when a response is received from the Volt
- “end” emitted when the call ends

### Server streaming calls

The example below shows execution of an SQL statement on a database, the data event will be emitted for each row of data in the result set.

The end event is emitted when the call ends.

```python
import asyncio # needed for async / await calls
from volt_client_web import VoltClient

config = ...

async def main():
    volt_client = VoltClient(config)
    await volt_client.initialise()

    call = await volt_client.sqlExecute(
        {
            "database_id": "fc17c5a1-a858-45c6-804b-7e16af7c968d",
            "statement": "SELECT * FROM NETFLIX LIMIT 100"
        }
    )
    @call.on("error")
    def error_handler(error):
        print(error)
    
    @call.on("data")
    def data_handler(response):
        print(response)

    @call.on("end")
    def end_handler():
        print("complete")

asyncio.run(main())
```

### Client streaming calls
Client streaming calls have a similar syntax to server streaming calls, although the data event should only be emitted once rather than multiple times.

Clients can use the send method on the returned call object to send requests to the server (see bi-direction example below).

Clients use the end method of the returned call object to indicate to the server that the call has ended.

### Bi-directional streaming calls
As expected, bi-directional calls are a combination of client and server streaming calls, whereby the data event is emitted for each response from the server, and the client can send multiple requests using the call object send method.

```python
import asyncio # needed for async / await calls
from volt_client_web import VoltClient

config = ...

async def main():
    volt_client = VoltClient(config)
    await volt_client.initialise()

    sub = await volt_client.subscribeWire(
        {
        "wire_id": "59dceb36-fafb-4c9e-a4c7-710cd16e9188",
        }
    )

    @sub.on("error")
    def error_handler(error):
        print("error: ", error)
    
    @sub.on("data")
    def data_handler(payload):
        print("data: ", payload)

    @sub.on("end")
    def end_handler():
        print("end reached")

    #
    # ...
    #
    
    # Some time later, ask the server to end the subscription
    await sub.send({"stop": True})

asyncio.run(main())
```
