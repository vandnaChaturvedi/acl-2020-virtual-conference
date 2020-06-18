import argparse
import csv
import json

import yaml
from requests import sessions
from rocketchat_API.rocketchat import RocketChat


def parse_arguments():
    parser = argparse.ArgumentParser(description="MiniConf Portal Command Line")
    parser.add_argument(
        "--config",
        required=True,
        help="config file containing API user_id, auth_token and server details",
    )
    parser.add_argument(
        "--sponsors", required=True, help="yaml file containing details of sponsors",
    )
    parser.add_argument("--test", default=False, action="store_true")
    parser.add_argument(
        "--delete",
        default=False,
        action="store_true",
        help="use this flag to delete the sponsor channels",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    with open(args.config, "r") as fin:
        config = yaml.load(fin)
    with open(args.sponsors, "r") as fin:
        sponsors = yaml.load(fin)

    with sessions.Session() as session:
        rocket = RocketChat(
            user_id=config["user_id"],
            auth_token=config["auth_token"],
            server_url=config["server"],
            session=session,
        )

        created_channels = set()
        for sponsor_level in sponsors:
            for sponsor in sponsor_level["sponsors"]:
                sponsor_name = sponsor["name"]
                sponsor_channel = sponsor.get("channel")
                if sponsor_channel in [None, "example_sponsor"]:
                    sponsor_channel = (
                        sponsor_name.split("/")[0].strip().lower().replace(" ", "_")
                    )
                if sponsor_channel in created_channels:
                    print(f"Already created channel for {sponsor_channel}")
                    continue

                print(sponsor_name, sponsor_channel)
                created_channels.add(sponsor_channel)
                if args.delete:
                    resp = rocket.channels_delete(channel=sponsor_channel).json()
                    print(resp)
                else:
                    if not args.test:
                        created = rocket.channels_create(
                            sponsor_channel, readOnly=True, broadcast=True
                        ).json()
                        print(sponsor_channel, created)
                    topic = sponsor_name
                    description = sponsor["description"]
                    if not args.test:
                        channel_id = rocket.channels_info(
                            channel=sponsor_channel
                        ).json()["channel"]["_id"]
                        rocket.channels_set_topic(channel_id, topic).json()
                        rocket.channels_set_description(channel_id, description)
                    print(
                        f"Creating channel for {sponsor_name} with channel name {sponsor_channel}, \
                        topic {topic} and description {description}"
                    )


if __name__ == "__main__":
    main()
