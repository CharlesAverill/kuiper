import asyncio
import json
import websockets


class Client:
    def __init__(self, host, port):
        self.uri = f"ws://{host}:{port}"

    async def _send(self, data):
        # Encode data into utf-8 json
        data = json.dumps(data)

        async with websockets.connect(self.uri) as websocket:
            await websocket.send(data)

            response = await websocket.recv()
            return json.loads(response)

    def send(self, data: dict):
        return asyncio.get_event_loop().run_until_complete(self._send(data))

    def login(self, username, password):
        response = self.send({
            "ACTION": "LOGIN",
            "USERNAME": username,
            "PASSWORD": password
        })

        return response["STATUS"] == "SUCCESSFUL"

    def register(self, email, username, password, age, major):
        response = self.send({
            "ACTION": "REGISTER",
            "EMAIL": email,
            "USERNAME": username,
            "PASSWORD": password,
            "AGE": age,
            "MAJOR": major
        })

        return response["STATUS"] == "SUCCESSFUL"

    def create_post(self, title, content, user_id, created_at):
        response = self.send({
            "ACTION": "CREATE_POST",
            "TITLE": title,
            "CONTENT": content,
            "USER_ID": user_id,
            "CREATED_AT": created_at
        })

        return response["STATUS"] == "SUCCESSFUL"

    def get_user_by_username(self, username):
        response = self.send({
            "ACTION": "GET_USER_USERNAME",
            "USERNAME": username
        })

        if response["STATUS"] == "SUCCESSFUL":
            return response

    def get_user_by_email(self, email):
        response = self.send({
            "ACTION": "GET_USER_EMAIL",
            "EMAIL": email
        })

        if response["STATUS"] == "SUCCESSFUL":
            return response

    def get_post(self, post_id):
        response = self.send({
            "ACTION": "GET_USER",
            "POST_ID": post_id
        })

        if response["STATUS"] == "SUCCESSFUL":
            return response
