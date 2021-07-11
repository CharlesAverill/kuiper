import asyncio
import datetime
import json
import websockets

from ..db import login, register, get_user_by_username, get_user_by_email, get_post

sess = None
quiet = False
date_format = "%Y-%m-%d %H:%M:%S.%f"


async def websocket_main_loop(websocket, path):
    global sess

    data = await websocket.recv()
    data = json.loads(data)

    if not quiet:
        print(f"{datetime.datetime.now().strftime(date_format)} - Received {data['ACTION']} request", end="")

    response = {"STATUS": "UNSUCCESSFUL"}

    if data["ACTION"] == "LOGIN":
        query = login(data["USERNAME"], data["PASSWORD"], sess)
        if query:
            response.update(json.loads(query))
            response["STATUS"] = "SUCCESSFUL"
    elif data["ACTION"] == "REGISTER":
        try:
            register(data["EMAIL"], data["USERNAME"], data["PASSWORD"], int(data["AGE"]), data["MAJOR"], sess)
            response["STATUS"] = "SUCCESSFUL"
        except Exception as e:
            print(f"Error during registration: {e}")
    elif data["ACTION"] == "GET_USER_USERNAME":
        query = get_user_by_username(data["USERNAME"], sess)
        if query:
            response.update(json.loads(query))
            response["STATUS"] = "SUCCESSFUL"
    elif data["ACTION"] == "GET_USER_EMAIL":
        query = get_user_by_email(data["EMAIL"], sess)
        if query:
            response.update(json.loads(query))
            response["STATUS"] = "SUCCESSFUL"
    elif data["ACTION"] == "GET_POST":
        query = get_post(data["POST_ID"], sess)
        if query:
            response.update(json.loads(query))
            response["STATUS"] = "SUCCESSFUL"

    if not quiet:
        print(f" - {response['STATUS']} at {datetime.datetime.now().strftime(date_format)}")

    await websocket.send(json.dumps(response))


def start_server(cfg, session, q=False):
    global sess, quiet
    sess = session
    quiet = q

    if not quiet:
        print("Setting up server")
    server = websockets.serve(websocket_main_loop, cfg["bind_host"], int(cfg["port"]))

    if not quiet:
        print("Starting server")
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
