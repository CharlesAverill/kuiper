import asyncio
import json
import random
import smtplib
import websockets

from email.mime.text import MIMEText
from ..db import *
from ..tui.utils import validate_email

sess = None
quiet = False
cfg = None

email_verification_codes = {}

date_format = "%Y-%m-%d %H:%M:%S.%f"


async def websocket_main_loop(websocket, path):
    global sess, cfg

    data = await websocket.recv()
    data = json.loads(data)

    if not quiet:
        print(f"{datetime.datetime.now().strftime(date_format)} - Received {data['ACTION']} request", end="")

    response = {"STATUS": "UNSUCCESSFUL"}

    if "USER_ID" in data and is_logged_in(data["USER_ID"]):
        if data["ACTION"] == "CREATE_POST":
            try:
                create_post(data["TITLE"], data["CONTENT"], data["USER_ID"], sess)
                response["STATUS"] = "SUCCESSFUL"
            except Exception as e:
                print(f"Error during post creation: {e}")
        elif data["ACTION"] == "GET_POST":
            query = get_post(data["POST_ID"], sess)
            if query:
                response.update(json.loads(query))
                response["STATUS"] = "SUCCESSFUL"
        elif data["ACTION"] == "GET_ALL_POSTS":
            dump = get_all_posts(sess)
            response.update({"POSTS_JSON": dump})
            response["STATUS"] = "SUCCESSFUL"
        elif data["ACTION"] == "UPDATE_USER":
            if update_user(data["USER_ID"], data, sess):
                response["STATUS"] = "SUCCESSFUL"
        elif data["ACTION"] == "DELETE_POST":
            if delete_post(data["POST_ID"], sess):
                response["STATUS"] = "SUCCESSFUL"
    else:
        if data["ACTION"] == "LOGIN":
            query = login(data["USERNAME"], data["PASSWORD"], sess)
            if query:
                response.update(json.loads(query))
                response["STATUS"] = "SUCCESSFUL"
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
        elif data["ACTION"] == "GET_USER_ID":
            query = get_user_by_id(data["USER_ID"], sess)
            if query:
                response.update(json.loads(query))
                response["STATUS"] = "SUCCESSFUL"
        elif data["ACTION"] == "VERIFY_EMAIL":
            code = verify_email(data["EMAIL"], data["USERNAME"])
            if code is not None:
                response["STATUS"] = "SUCCESSFUL"
        elif data["ACTION"] == "CHECK_VERIFICATION_CODE":
            success, verification = check_verification_code(data["EMAIL"], data["CODE"])
            if not success:
                response["ERROR_CODE"] = verification
            else:
                try:
                    register(data["EMAIL"], data["USERNAME"], data["PASSWORD"], data["AGE"], data["MAJOR"], sess)
                    response["STATUS"] = "SUCCESSFUL"
                except Exception as e:
                    print(f"Error during registration: {e}")

    if not quiet:
        print(f" - {response['STATUS']} at {datetime.datetime.now().strftime(date_format)}")

    await websocket.send(json.dumps(response))


def check_verification_code(email, code):
    global email_verification_codes

    # Remove old values from dict
    remove = []
    for k, v in email_verification_codes.items():
        if (datetime.datetime.now() - v[2]).seconds // 60 > 30:
            remove.append(k)
    for k in remove:
        del email_verification_codes[k]

    if email not in email_verification_codes.keys():
        return False, "Verification failed. Another code will be sent."

    verification_tuple = email_verification_codes[email]
    verification_tuple = (verification_tuple[0], verification_tuple[1] + 1, verification_tuple[2])

    if verification_tuple[1] >= 3:
        return False, "Too many tries used. Another code will be sent."

    email_verification_codes[email] = verification_tuple

    if str(code) == str(email_verification_codes[email][0]):
        del email_verification_codes[email]
        return True, "Success"

    return False, "Code does not match"


def verify_email(email, username):
    global cfg, email_verification_codes

    if not cfg["server_email_address"]:
        print("Email verification not set up!")
        return False, "Email verification not set up!"

    if not validate_email(email, cfg) and email not in cfg["email_whitelist"]:
        return False, "That domain is not permitted"

    try:
        code = random.randint(10000, 99999)

        email_template = f"""
Hi there {username}!

Your verification code for Kuiper is {code}

Enter this code into the "Registration Code" field on the registration page, then click "Continue Registration"

Thank you for using Kuiper!
        """

        message = MIMEText(email_template)

        with smtplib.SMTP_SSL(cfg["server_email_smtp_addr"], cfg["server_email_smtp_port"]) as smtp_server:
            smtp_server.ehlo()
            smtp_server.login(cfg["server_email_address"], cfg["server_email_password"])
            smtp_server.sendmail(cfg["server_email_address"], email, message.as_string())

        email_verification_codes[email] = (code, 0, datetime.datetime.now())

        return True
    except:
        return False


def start_server(configs, session, q=False):
    global sess, quiet, cfg
    sess = session
    quiet = q
    cfg = configs

    if not quiet:
        print("Setting up server")
    server = websockets.serve(websocket_main_loop, cfg["bind_host"], int(cfg["port"]))

    if not quiet:
        print("Starting server")
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
