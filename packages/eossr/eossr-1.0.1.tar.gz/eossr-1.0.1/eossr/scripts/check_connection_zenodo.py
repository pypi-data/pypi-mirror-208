#!/usr/bin/env python

import argparse

from eossr.api.zenodo import ZenodoAPI


def build_argparser():
    """
    Construct main argument parser for the ``codemet2zenodo`` script

    :return:
    argparser: `argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(description="Test the connection to zenodo and all the stages of a new upload.")

    parser.add_argument(
        '--token', '-t', type=str, dest='zenodo_token', help='Personal access token to (sandbox)Zenodo', required=True
    )

    parser.add_argument(
        '--sandbox',
        '-s',
        action='store_true',
        help='Use Zenodo sandbox.',
    )

    parser.add_argument(
        '--project_dir',
        '-p',
        action='store',
        dest='project_dir',
        help='Path to the root directory of the directory to be uploaded. ' 'DEFAULT; assumed to be on it, i.e., "./"',
        default='./',
    )
    return parser


def main():
    # Required arguments

    args = build_argparser().parse_args()

    zenodo = ZenodoAPI(access_token=args.zenodo_token, sandbox=args.sandbox)
    zenodo.check_upload_to_zenodo(args.project_dir)


if __name__ == '__main__':
    main()
