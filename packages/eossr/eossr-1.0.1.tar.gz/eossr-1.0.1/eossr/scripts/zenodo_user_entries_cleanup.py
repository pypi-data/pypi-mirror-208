#!/usr/bin/env python
"""
Simple code to delete all user entries that have not been published
"""
import argparse
import os
import warnings

from eossr.api.zenodo import ZenodoAPI
from eossr.api.zenodo.http_status import HTTPStatusError


def zenodo_cleanup(token, sandbox=True):
    """
    Delete user unpublished entries

    :param token: str
        Zenodo access token
    :param sandbox: bool
        True to use sandbox
    """
    zen = ZenodoAPI(token, sandbox=sandbox)
    use = zen.query_user_deposits()

    for rec in use.json():
        if not rec['submitted']:
            print(f"Record {rec['id']} ... ")
            try:
                zen.erase_deposit(rec['id'])
            except HTTPStatusError as e:
                warnings.warn(f"Error deleting record {rec['id']}:\n{e}")
                continue


def build_argparser():
    """
    Construct main argument parser for the ``codemet2zenodo`` script

    :return:
    argparser: `argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(description="Delete user unpublished entries. Working on sandbox by default.")

    parser.add_argument(
        '--token',
        '-t',
        type=str,
        default=os.getenv('SANDBOX_ZENODO_TOKEN'),
        help='Access token',
    )
    parser.add_argument('--not-sandbox', action='store_false', help="To work on the actual Zenodo instead of sandbox")
    return parser


def main():

    parser = build_argparser()
    args = parser.parse_args()
    zenodo_cleanup(args.token, args.not_sandbox)


if __name__ == '__main__':
    main()
