import os
import requests
import json
import re
import time
import config
from lxml import etree
from bs4 import BeautifulSoup
from multiprocessing import Process
from contextlib import closing
from imagevideo import video_add_mp3  # need imagevideo.py under same folder
from fileoperate import deleteline  # need fileoperate.py under same folder
from fileoperate import add_content
from fileoperate import add_log
from fileoperate import read
from fileoperate import move_file




class Bilibili:
    def __init__(self):
        self.index = 'https://api.bilibili.com/pgc/season/index/result?season_version=1&area=-1&is_finish=1&copyright=-1&season_status=1&season_month=-1&year=-1&style_id=-1&order=3&st=1&sort=0&page=replace&season_type=1&pagesize=20&type=1'
        self.link = 'https://www.bilibili.com/bangumi/play/ssreplace'
        self.ep = 'https://www.bilibili.com/bangumi/play/epreplace'
        self.ep_num = ''
        self.path = ''
        self.video = []  # 视频下载链接
        self.grade1 = []  # 视频画质等级
        self.grade2 = []  # 音频等级
        self.music = []  # 音频地址
        self.name = ''  # 视频名字
        self.drama_name = ''  # 番剧名
        self.headers = {
            'Referer': 'https://www.bilibili.com/',
            'User-Agent': config.GL_User_Agent,
            'Cookie': config.GL_Cookie
        }

    def requestdemo(self, url):
        headers = self.headers
        trytimes = 5  # 重试的次数
        for i in range(trytimes):
            try:
                response = requests.get(url, headers=headers, verify=False, proxies=None, timeout=10)
                # 注意此处也可能是302等状态码
                if response.status_code == 200:
                    return response
            except():
                print(f'requests failed {i} time')
            time.sleep(1)

    def start(self):
        listsize = read('./undownload_list.txt')  # 获取下载列表文件大小判断是否需要添加新的任务
        if len(listsize) == 0:
            self.add_to_list()  # 添加新的任务
        else:
            self.getinfo()  # 继续上次下载

    def add_to_list(self):
        drama_id = []
        for i in range(1, 6):  # 遍历1-5页限免番剧号
            response = requests.get(url=self.index.replace('replace', str(i)), headers=self.headers)
            drama_list = response.json()
            drama_info = drama_list['data']['list']
            for info in drama_info:
                if info['badge'] == '限时免费':
                    drama_id.append(str(info['season_id']))
        with open('./downloaded_list.txt') as f:  # 排除已下载番剧号
            for line in f.readlines():
                downloaded_id = line.strip('\n')
                for id_1 in drama_id:
                    if id_1 == downloaded_id:
                        drama_id.remove(id_1)
        if drama_id.__len__() == 0:
            print('当前没有未下载限免番剧！')
        for id_2 in drama_id:  # 查找番剧所有ep号
            response = requests.get(url=self.link.replace('replace', id_2), headers=self.headers)
            time.sleep(1)
            bf = BeautifulSoup(response.text, 'lxml')
            self.drama_name = bf.find_all('h1')[0].text
            # self.name = self.name.replace(' ', '-')
            cont1 = bf.find_all("script")
            cont1 = cont1[7].contents[0].replace("window.__INITIAL_STATE__=", "")
            finding = cont1[cont1.find('newestEp')+36:cont1.find('newestEp')+39]
            id_num = re.findall(r'\d+', finding)[0]  # 匹配字符串确定总集数
            url_list = []
            for i in range(int(id_num)):  # 匹配字符串查询所有ep号
                ep = cont1[cont1.find('"loaded":false,"id"')+19:cont1.find('"loaded":false,"id"')+27]
                ep = re.findall(r'\d+', ep)[0]
                url = self.ep.replace('replace', ep)  # ep号转化为url
                url_list.append(url)
                cont1 = cont1.replace('"loaded":false,"id"', '', 1)
            with open('./undownload_list.txt', 'a') as f:
                for url in url_list:
                    f.write(url + '\n')
            self.path = os.getcwd() + '\\{}'.format(self.drama_name)
            if not os.path.exists(self.path):
                os.mkdir(self.path)
            with open('{}\\info.temp'.format(self.path), 'w') as f:
                f.write('{}'.format(url_list[-1]))
            # add_content('{}\\info.temp'.format(path), '{}'.format(url_list[0]))
            with open('{}\\id.temp'.format(self.path), 'w') as f:
                f.write('{}'.format(id_2))
            # add_content('{}\\id.temp'.format(path), '{}'.format(id_2))
            # print(url_list)
        self.getinfo()

    def getinfo(self):
        url_list = []
        with open('./undownload_list.txt', 'r') as f:
            for line in f.readlines():
                url_list.append(line.strip('\n'))
        for targeturl in url_list:
            self.ep_num = re.findall(r'\d+', targeturl)[0]
            req = self.requestdemo(targeturl)
            time.sleep(1)
            bf = BeautifulSoup(req.text, 'lxml')
            # self.name=bf.find_all('span',class_="tit")[0].text
            cont1 = bf.find_all("script")  # 寻找我们需要的东西
            cont1 = cont1[6].contents[0].replace("window.__playinfo__=", "")  # 把内容替换掉以便后面进行json数据解析
            cont1 = json.loads(cont1)  # json数据解析
            self.grade1 = []
            self.grade2 = []
            self.video = []
            self.music = []
            for each in cont1['data']['dash']['video']:  # 遍历json数据，获取视频下载地址
                self.grade1.append(each['id'])
                self.video.append(each['baseUrl'])
            for each in cont1['data']['dash']['audio']:  # 获取音频下载地址
                self.grade2.append(each['id'])
                self.music.append(each['baseUrl'])
            self.name = bf.find_all('h1')[0].text
            # self.name = self.name.replace(' ', '-')
            self.drama_name = self.name[0:self.name.rfind('：')]
            self.path = os.getcwd() + '\\{}'.format(self.drama_name)
            signal = read(self.path + '\\info.temp')
            vid = read(self.path + '\\id.temp')[0]
            print("视频名称:%s" % self.name)
            grade = []
            for i in range(len(self.grade1)):
                grade.append(str(i) + ':' + str(self.grade1[i]))
            a = 2
            # a = input("请选择下载画质：%s(数字越高越清晰，只需要输入序号)" % grade)
            grade.clear()
            for i in range(len(self.grade2)):
                grade.append(str(i) + ':' + str(self.grade2[i]))
            b = 0
            # b = input("请选择下载音质：%s(数字越高越音质好，只需要输入序号)" % grade)
            # 下面是多线程的代码，一个线程下视频，一个下音频
            p1 = Process(target=self.down, args=(a, 1))
            p1.start()
            p2 = Process(target=self.down, args=(b, 2))
            p2.start()
            p1.join()
            p2.join()
            video_add_mp3(self.ep_num + '.mp4', self.ep_num + '.mp3')  # 合并音频和视频文件
            os.rename(self.ep_num + '-txt.mp4', self.name + '.mp4')
            move_file(self.name + '.mp4', self.path + '\\')
            os.remove(self.ep_num + '.mp4')
            os.remove(self.ep_num + '.mp3')
            deleteline('./undownload_list.txt', 1)
            if targeturl == signal[0]:
                add_content('./downloaded_list.txt', vid)
                os.remove(self.path + '\\info.temp')
                os.remove(self.path + '\\id.temp')
                add_log('./logs.txt', '番剧 {} 下载完成'.format(self.drama_name))
            # else:
                # print('2')
            add_log('./logs.txt', '{}下载完成'.format(self.name))
            print("下载成功！")

    def down(self, v, a):
        # 判断下载的内容
        if a == 1:
            bv = self.ep_num+'.mp4'
            target = self.video[int(v)]
            print("正在下载视频.....")
        else:
            bv = self.ep_num+'.mp3'
            target = self.music[int(v)]
            print("正在下载音频......")
        # 下面是下载视频和音频的代码
        with closing(requests.get(url=target, stream=True, headers=self.headers)) as r:  # 这里就是下载图片的代码了
            with open(bv, 'ab+') as f:  # 这里是保存图片
                for chunk in r.iter_content(chunk_size=1024):  # 下面都是下载图片数据的代码，所以不解释
                    if chunk:
                        f.write(chunk)
                        f.flush()


if __name__ == "__main__":
    bi = Bilibili()
    bi.start()
