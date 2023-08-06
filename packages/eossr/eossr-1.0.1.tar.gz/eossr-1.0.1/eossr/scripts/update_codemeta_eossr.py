import argparse
import os
from pathlib import Path

import requests

from eossr import ROOT_DIR
from eossr import __version__ as eossr_version
from eossr.utils import update_codemeta


def build_argparser():
    """
    Construct main argument parser for the ``codemet2zenodo`` script

    :return:
    argparser: `argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(description="Update Codemeta")

    parser.add_argument(
        '--codemeta_path',
        '-c',
        type=Path,
        dest='codemeta_path',
        help='Path to codemeta.json',
        default=Path(ROOT_DIR).joinpath('codemeta.json'),
        required=False,
    )

    parser.add_argument(
        '--no-release',
        action='store_true',
        help="Use when making a release. "
        "Do not update the publication date, the zip archive URL and remove release notes.",
    )

    return parser


def get_gitlab_releases(api_url, project_id, token):
    """
    Get the releases from Gitlab

    Parameters
    ----------
    api_url: str
    project_id: int or str
    token: str

    Returns
    -------
    releases: list[dict]
    """
    releases_url = f"{api_url}/projects/{project_id}/releases"
    req = requests.get(releases_url, params={"PRIVATE-TOKEN": token})
    req.raise_for_status()
    return req.json()


if __name__ == '__main__':
    parser = build_argparser()
    args = parser.parse_args()

    project_id = os.getenv('CI_PROJECT_ID')
    api_url = os.getenv('CI_API_V4_URL')
    token = os.getenv('CI_JOB_TOKEN')

    if args.no_release:
        publication_date = False
        release_notes = ""
        download_url = ""
    else:
        publication_date = True
        last_gitlab_release = get_gitlab_releases(api_url, project_id, token)[0]
        release_notes = last_gitlab_release['description']
        download_url = last_gitlab_release['assets']['sources'][0]['url']

    html = update_codemeta(
        codemeta_path=args.codemeta_path,
        readme_path=Path(__file__).parent.joinpath('../../README.md').resolve(),
        version=eossr_version,
        download_url=download_url,
        publication_date=publication_date,
        release_notes=release_notes,
        overwrite=True,
    )
