# Author: Andrea Querci
# version: 1.0.0
# project: https://github.com/pyquerci/sfetchapi
# license: GPLv2

import argparse
import json
import sys
from pathlib import Path
import pwinput
import requests
import yaml


class ApiFetcher:
    def __init__(self, username: str, password: str, items: dict[str, str]) -> None:
        self.auth = (username, password)
        self.items = items

    def fetch(self) -> None:
        for filename, url in self.items.items():
            try:
                print(f"[+] Fetching {url}")
                response = requests.get(
                    url,
                    auth=self.auth,
                    verify=False,
                    timeout=10,
                )

                if response.status_code == 401:
                    print(f"[!] Unauthorized (401): {filename}")
                    continue

                response.raise_for_status()
                content = self._format_content(response)

                with open(filename, "w", encoding="utf-8") as fp:
                    fp.write(content)

                print(f"[✓] Saved {filename}")

            except requests.exceptions.RequestException as exc:
                print(f"[!] Error downloading {filename}: {exc}")

    @staticmethod
    def _format_content(response: requests.Response) -> str:
        try:
            data = response.json()
            return json.dumps(data, indent=4, ensure_ascii=False)

        except (ValueError, json.JSONDecodeError):
            return response.text


def load_config(filename: str) -> dict:
    path = Path(filename)

    if not path.is_file():
        print(f"error: file not found: {filename}")
        sys.exit(1)

    with path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        usage=("%(prog)s [-h] "
            "[-a] "
            "[-c CONFIG] "
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "description:\n"
            "  download data from REST APIs\n\n"
        ),
    )

    parser.add_argument(
        "-a",
        "--about",
        action="store_true",
        help="show author, version, project URL and license information",
    )

    parser.add_argument(
        "-c",
        "--config",
        default="default.yaml",
        metavar="CONFIG",
        help="YAML configuration file (default: %(default)s)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.about:
        print(
            "author: Andrea Querci\n"
            "version: 1.0\n"
            "project: https://github.com/pyquerci/sfetchapi\n"
            "license: GPLv2"
        )
        return

    requests.packages.urllib3.disable_warnings()

    config = load_config(args.config)
    credentials = config.get("credentials", {})
    username = credentials.get("username")
    password = credentials.get("password")

    if username is None:
        username = input("Username: ")

    if password is None:
        password = pwinput.pwinput(
            prompt="Password: ",
            mask="*",
        )

    print("", end="\n")

    fetcher = ApiFetcher(
        username=username,
        password=password,
        items=config["items"],
    )
    fetcher.fetch()


if __name__ == "__main__":
    main()
