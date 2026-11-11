import argparse
import json
from datetime import datetime

from dataset_v3 import build_v3_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cutoff", required=True)
    args = parser.parse_args()
    print(json.dumps(build_v3_dataset(args.source, args.output, datetime.fromisoformat(args.cutoff))))


if __name__ == "__main__":
    main()
