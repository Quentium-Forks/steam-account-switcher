import aiohttp
import shutil
import os
import sys
import asyncio
from packaging import version
from io import BytesIO
from bs4 import BeautifulSoup

PY_VERSION = version.parse(f'{sys.version_info[0]}.{sys.version_info[1]}')

if PY_VERSION >= version.parse('3.8') and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

elif PY_VERSION <= version.parse('3.4'):
    print('Not supported Python version. At least 3.5 is required.')
    sys.exit(0)


def download_avatar(steamid_list):
    '''Downloads avatar images through Steam API.
    param steamid_list: A list containing steamid64'''

    if not os.path.isdir('avatar'):
        os.mkdir('avatar')

    async def download_image(session, steamid64):
        try:
            async with session.get(f'https://steamcommunity.com/profiles/{steamid64}') as r:
                soup = BeautifulSoup(await r.read(), 'html.parser')

                image_url = soup.select('.playerAvatarAutoSizeInner > img')[0].get('src')
                print(f'Found image URL for {steamid64}')

            async with session.get(image_url) as r:
                print(f'Downloading {image_url} for {steamid64}...')

                with open(f'avatar/{steamid64}.jpg', 'wb') as f:
                    shutil.copyfileobj(BytesIO(await r.read()), f)
        except (aiohttp.ClientError, OSError):
            print(f'Exception while downloading image for {steamid64}')

    if PY_VERSION >= version.parse('3.7'):
        async def main():
            async with aiohttp.ClientSession() as session:
                tasks = [asyncio.create_task(download_image(session, steamid)) for steamid in steamid_list]
                await asyncio.gather(*tasks)

        asyncio.run(main())
    else:
        async def main():
            async with aiohttp.ClientSession as session:
                futures = [asyncio.ensure_future(download_image(session, steamid)) for steamid in steamid_list]
                await asyncio.gather(*futures)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
