from subprocess import PIPE, Popen
from urllib.parse import urlparse

import api
import pexpect


def login(houstonURL, email, password, duration):
    client = api.getClient(houstonURL, email, password, duration)

    endpoint_parsed = urlparse(client.endpoint)
    hostname = endpoint_parsed.hostname.replace("houston.", "")

    child = pexpect.spawn(f"astro auth login {hostname}")
    child.expect("Username .*: ", timeout=3)
    child.sendline(email)
    child.expect("Password: ", timeout=3)
    child.sendline(password)
    index = child.expect([pexpect.EOF, "> "], timeout=6)
    print("INDEX", index)
    if index == 1:
        child.sendline("")
        child.expect(pexpect.EOF)

    print("BEFORE", child.before)
    print("AFTER", child.after)

    result = child.before.decode("utf-8")
    print("RESULT", result)

    assert "Successfully authenticated" in result
    return client


def getClient(houstonURL, email, password, duration):
    client = api.getClient(houstonURL, email, password, duration)

    endpoint_parsed = urlparse(client.endpoint)
    hostname = endpoint_parsed.hostname.replace("houston.", "")
    args = ["auth", "login", hostname]

    def checkOAuth(process, stream, character):
        if character == ":":
            if "leave blank for oAuth" in stream:
                process.stdin.write(b"\n")
            return True
        return False

    process, _ = cliRunOld(args, checkOAuth)

    result, err = process.communicate(f"{client.token}\n\n".encode())
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    assert "Successfully authenticated" in result
    return client


def cliRun(args, check=None):
    cmd = "astro " + " ".join(args)
    print("CMD", cmd)
    child = pexpect.spawn(cmd)
    child.expect(pexpect.EOF, timeout=30)

    return None, child.before.decode("utf-8")


def cliRunOld(args, check=None):
    process = Popen(["astro"] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stream = ""
    while True:
        character = process.stdout.read(1).decode("utf-8")
        if not character:
            break
        # sys.stdout.write(character)
        stream += character
        if check is not None and check(process, stream, character):
            break

    return process, stream
