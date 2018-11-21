import requests

if __name__ == '__main__':
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    r = requests.get('https://aweme.snssdk.com/aweme/v1/play/?video_id=v0200f580000bfomov5ds133ngaohj50&line=0&ratio=540p&media_type=4&vr_type=0&test_cdn=None&improve_bitrate=0&iid=51050168070&idfa=887748FC-0DA1-4984-B87F-F2FC9AC5D14B&version_code=3.1.0&device_type=iPhone5%2C2&aid=1128&os_version=10.3.3&screen_width=640&pass-region=1&vid=AECABC99-0F66-4086-86BC-EC4E01B4DEA1&device_id=59415024289&os_api=18&app_name=aweme&build_number=31006&device_platform=iphone&js_sdk_version=1.3.0.1&app_version=3.1.0&ac=WIFI&openudid=75a4bc255848cd7901e166e5c168b23e3e9394a8&channel=App%20Store',headers=headers)
    with open('test.mp4','wb') as f:
        f.write(r.content)
    # print(r.text)
