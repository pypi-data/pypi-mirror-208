import argparse

from . import example
from . import __VERSION__

def main():
    print("It begins")
    parser = argparse.ArgumentParser(description="MosaBay")
    parser.add_argument(
        "-I",
        "--inputs",
        type=int,
        default=1,
        help="inputs (default: 1)",
    )
    args = parser.parse_args()
    res=example.add_one(args.inputs)
    print(res)
    print("It ends")

if __name__ == "__main__":
    main()