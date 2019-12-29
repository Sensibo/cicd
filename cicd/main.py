#!/usr/bin/env python3
# pylint: disable=C0103
import argparse
import os
import pprint
import datetime
import re
import logging
from cicd import secrets
from cicd import buildphase
from cicd import slack

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
slack_cmd = subparsers.add_parser(
    "slack",
    help="slack subcommands")
subsubparsers = slack_cmd.add_subparsers(dest="subcmd")
post_cmd = subsubparsers.add_parser("post")
post_cmd.add_argument("--text", required=True)
post_cmd.add_argument("--icon_emoji")
post_cmd.add_argument("--channel", default="#feed-ci")
report_cmd = subsubparsers.add_parser("report_script_result")
report_cmd.add_argument("--script-name", required=True)
report_cmd.add_argument("--log", required=True)
report_cmd.add_argument("--limit-log")
report_cmd.add_argument("--force-ascii-log", action="store_true")
report_cmd.add_argument("--channel", default="#feed-ci")
banner_cmd = subparsers.add_parser("banner")
banner_cmd.add_argument("text")
build_phase_cmd = subparsers.add_parser("build_phase")
build_phase_cmd.add_argument("name")
build_phase_cmd.add_argument("command")
args = parser.parse_args()

if args.cmd == "slack":
    secrets_instance = secrets.Secrets()
    slack_instance = slack.Slack(secrets_instance.slack_app_token())
    if args.subcmd == "post":
        slack_instance.post_message(text=args.text, channel=args.channel, icon_emoji=args.icon_emoji)
    elif args.subcmd == "report_script_result":
        successful = not buildphase.state_is_failed()
        if successful:
            title = f"{args.script_name} completed successfully"
            color = "good"
            icon_emoji = slack.EMOJI_V
        else:
            title = f"{args.script_name} failed:\n{buildphase.read_state()}"
            color = "danger"
            icon_emoji = slack.EMOJI_X
        message = []
        if 'CODEBUILD_START_TIME' in os.environ:
            started = datetime.datetime.fromtimestamp(int(os.environ['CODEBUILD_START_TIME'])/1000)
            message.append("Started at: %s" % started)
        slack_instance.post_message(text=message,
                                    channel=args.channel,
                                    title=title,
                                    color=color,
                                    icon_emoji=icon_emoji)
        if not successful:
            with open(args.log, 'rb') as reader:
                log = reader.read()
            if args.limit_log:
                assert args.limit_log.endswith('k')
                limit_bytes = int(args.limit_log[:-1]) * 1024
                log = log[-limit_bytes:]
            if args.force_ascii_log:
                log = re.sub(br'[^\x1f-\x7f\n\r]', b'', log)
            slack_instance.upload_file(filename="endoflog.txt", content=log, channel=args.channel)
            raise Exception("Build was unsuccessfull")
    else:
        raise AssertionError("Unknown command: %s" % args.subcmd)
elif args.cmd == "banner":
    buildphase.banner(args.text)
elif args.cmd == "build_phase":
    buildphase.build_phase(args.name, args.command)
else:
    raise AssertionError("Unknown command: %s" % args.cmd)


def entry_point():
    pass
