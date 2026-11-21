"""Update a Notion page cover from images stored in a public GitHub repository."""
import json
import os
from datetime import date, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
COVERS_DIR = Path(__file__).parent / 'covers'
# First scheduled Sunday. Subsequent Sundays advance one image, wrapping at the end.
START_SUNDAY = date(2026, 11, 22)


def select_image(today: date, files: list[Path]) -> tuple[Path, int]:
    if not files:
        raise ValueError('No supported images found in covers/. Add images and commit them.')
    weeks = max(0, (today - START_SUNDAY).days // 7)
    index = weeks % len(files)
    return files[index], index


def main():
    notion_token = os.environ.get('NOTION_TOKEN')
    notion_page_id = os.environ.get('NOTION_PAGE_ID')
    repository = os.environ.get('GITHUB_REPOSITORY')
    if not all((notion_token, notion_page_id, repository)):
        raise RuntimeError('Missing NOTION_TOKEN, NOTION_PAGE_ID or GITHUB_REPOSITORY.')

    files = sorted((p for p in COVERS_DIR.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS), key=lambda p: (p.name.lower(), p.name))
    local_today = datetime.now(ZoneInfo('America/New_York')).date()
    selected, index = select_image(local_today, files)
    # A public repository is required: Notion needs a direct, publicly reachable image URL.
    url = 'https://raw.githubusercontent.com/' + repository + '/main/covers/' + quote(selected.name)
    payload = json.dumps({'cover': {'type': 'external', 'external': {'url': url}}}).encode('utf-8')
    request = Request(
        'https://api.notion.com/v1/pages/' + notion_page_id.strip(),
        data=payload,
        method='PATCH',
        headers={
            'Authorization': 'Bearer ' + notion_token,
            'Notion-Version': '2025-09-03',
            'Content-Type': 'application/json',
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as e:
        detail = e.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'Notion returned HTTP {e.code}: {detail}') from e
    except URLError as e:
        raise RuntimeError(f'Could not connect to Notion: {e.reason}') from e
    print(f'Updated Notion page {result.get("id", notion_page_id)} with {selected.name} (image {index+1}/{len(files)}).')
    print(f'Image URL: {url}')


if __name__ == '__main__':
    main()
