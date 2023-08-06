import sys
from pathlib import Path
importpath = str(Path(__file__).parent.parent)
sys.path[0] = importpath
import argparse
from shared_atomic.atomic_activation import activation, modify_proxy

if sys.platform not in ('darwin', 'linux','win32'):
    raise NotImplementedError('Unsupported platform!')

def test_activation():
    activation()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="user tools for Shared Atomic Enterprise")
    parser.add_argument('-a','--action',
                        choices=['a','p'],
                        help="a for activation, p for proxy setting",
                        required=True,
                        dest='action')
    parsed = parser.parse_args()
    if parsed.action == 'a':
        activation()

    elif parsed.action == 'p':
        modify_proxy()
    else:
        sys.exit(255)

