import re
import json
import requests
from contextlib import closing
import pprint
from tqdm import tqdm
import subprocess
from parsel import Selector
import os

def download(url: str, fname: str, headers: dict):
    # 用流stream的方式获取url的数据
    resp = requests.get(url=url, stream=True, headers=headers)
    # print(resp)
    # 拿到文件的长度，并把total初始化为0
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
        dynamic_ncols=True,
        ascii=True     # 添加此，解决在win10终端多行显示
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def resolveAddress(url: str, sessdata:str,name=""):
    querystring = {"spm_id_from": "333.337.top_right_bar_window_history.content.click",
                "vd_source": "da4751b192e677889bcadc540e607ebb"}
    headers = {
        "referer": "https://search.bilibili.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        'Cookie': f'SESSDATA={sessdata}'}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if len(name)>0:
        title = name
    else:
        title = re.findall(
            '<h1 title="(.*?)" class="video-title tit">', response.text)[0]
    title = re.sub('[^\w\-_\. ]', '', title)
    title = re.sub(' +', '', title).strip()
    play_info = re.findall(
        '<script>window.__playinfo__=(.*?)</script>', response.text)[0]
    # print(type(play_info))
    json_data = json.loads(play_info)
    # print(type(json_data))
    # pprint.pprint(json_data)
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    # 带进度条写入
    download(audio_url, title+'.mp3', headers)
    download(video_url, title+'.mp4', headers)
    video_name = f'{title}'
    command = f'ffmpeg -i {video_name}.mp4 -i {video_name}.mp3 -c:v copy -c:a aac -strict experimental {video_name}-out.mp4'
    print(command)
    subprocess.run(command, shell=True)
    print(title, ":转码完毕")
    os.remove(f'{video_name}.mp4')
    os.remove(f'{video_name}.mp3')
    print(title, ":合并前文件删除完毕")


def bifirstResolve(url: str,sessdata:str,fanju:bool=0):
    if ("?p=" in url) and fanju:
        headers = {
            "referer": "https://search.bilibili.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            'Cookie': f'SESSDATA={sessdata}'}
        response = requests.request("GET", url, headers=headers).text
        match = re.search(r'"pages":(\[.*?\])', response)
        base_url = url.split("=")[0]
        if match:
        # 打印匹配到的 JSON 数据字符串
            videos_json = json.loads(match.group(1))
            # print(videos_json)
        else:
            print('No match found.')
        for i in videos_json:
            s_url = base_url+"="+str(i['page'])
            print(s_url)
            name = i['part']
            resolveAddress(s_url, sessdata,name)
    elif "?p=" in url:
        page = url.split("=")[1]
        name = ''
        headers = {
            "referer": "https://search.bilibili.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            'Cookie': f'SESSDATA={sessdata}'}
        response = requests.request("GET", url, headers=headers).text
        match = re.search(r'"pages":(\[.*?\])', response)
        base_url = url.split("=")[0]
        if match:
        # 打印匹配到的 JSON 数据字符串
            videos_json = json.loads(match.group(1))
            # print(videos_json)
        else:
            print('No match found.')
        for i in videos_json:
            if int(page)==i['page']:                    
                s_url = base_url+"="+str(i['page']) 
                name = i['part']               
                print("name的值是",name)
                resolveAddress(s_url, sessdata,name)
                break
    else:
        resolveAddress(url, sessdata)

# url = "https://www.bilibili.com/video/BV11S4y1a7X9/"
# url = "https://www.bilibili.com/video/BV1ha4y1H7sx?p=59"
# sess = "e5f15dfb%2C1699577107%2C7a241%2A51"
# bifirstResolve(url,sess,1)