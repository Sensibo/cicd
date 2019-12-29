import subprocess
import os
import sys

PHASES_STATE_FILE = "build_phases.tmp"


def state_is_failed():
    return "FAILED" in read_state()


def build_phase(name, command):
    content = read_state()
    if state_is_failed():
        content += f"SKIPPED: {name}\n"
        with open(PHASES_STATE_FILE, "w") as writer:
            writer.write(content)
        banner(f"SKIPPED: {name}\n")
        return
    banner(f"STARTED: {name}")
    sys.stdout.flush()
    result = subprocess.call(command, shell=True)
    if result == 0:
        banner(f"DONE: {name}")
        content += f"DONE: {name}\n"
    else:
        banner(f"FAILED: {name}")
        content += f"FAILED: {name}\n"
    with open(PHASES_STATE_FILE, "w") as writer:
        writer.write(content)


def banner(text):
    print("*"*120)
    print("*"*120)
    print("*"*120)
    print("***", text)
    print("*"*120)
    print("*"*120)
    print("*"*120)


def read_state():
    if not os.path.exists(PHASES_STATE_FILE):
        return ""
    with open(PHASES_STATE_FILE) as reader:
        return reader.read()
