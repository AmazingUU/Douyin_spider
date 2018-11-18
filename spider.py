import json

import requests


def get_html(url):
    r = requests.get(url)
    # res = json.loads(r.text)
    return r.content

if __name__ == '__main__':
    # res = get_html('https://aweme-eagle.snssdk.com/aweme/v1/feed/?iid=51050168070&idfa=887748FC-0DA1-4984-B87F-F2FC9AC5D14B&version_code=3.1.0&device_type=iPhone5,2&aid=1128&os_version=10.3.3&screen_width=640&pass-region=1&vid=AECABC99-0F66-4086-86BC-EC4E01B4DEA1&device_id=59415024289&os_api=18&app_name=aweme&build_number=31006&device_platform=iphone&js_sdk_version=1.3.0.1&app_version=3.1.0&ac=mobile&openudid=75a4bc255848cd7901e166e5c168b23e3e9394a8&channel=App%20Store&count=6&feed_style=0&filter_warn=0&max_cursor=0&min_cursor=0&pull_type=0&type=0&volume=0.06&mas=0161b6c4a20babcf6829e30950a9f3a577adb04abc0c6da0eeca91&as=a105e18ff4e32b1a102320&ts=1542462004')
    res = get_html('https://aweme.snssdk.com/aweme/v1/play/?video_id=v0200fcb0000bfmm1640gfkossaturrg&line=0&ratio=540p&watermark=1&media_type=4&vr_type=0&test_cdn=None&improve_bitrate=0&logo_name=aweme')
    # res = get_html('https://aweme.snssdk.com/aweme/v1/playwm/?video_id=v0200fbd0000bfo14ccps0spa6014650&line=0')
    with open('test.mp4','wb') as f:
        f.write(res)
    # print(res)
    # aweme_list = res['aweme_list']
    # for aweme in aweme_list:
    #     desc = aweme['desc']
    #     print(desc)
