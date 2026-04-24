import argparse
import json
import sys

import requests


def sample_payload() -> dict:
    return {
        "age": 39,
        "workclass": "Private",
        "fnlwgt": 77516,
        "education": "Bachelors",
        "education.num": 13,
        "marital.status": "Never-married",
        "occupation": "Adm-clerical",
        "relationship": "Not-in-family",
        "race": "White",
        "sex": "Male",
        "capital.gain": 2174,
        "capital.loss": 0,
        "hours.per.week": 40,
        "native.country": "United-States",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Call the prediction API and print response")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    target = f"{args.base_url.rstrip('/')}/predict"
    try:
        response = requests.post(target, json=sample_payload(), timeout=15)
        print(f"status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return 0 if response.ok else 1
    except requests.RequestException as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
