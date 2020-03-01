import requests
import os
import re
import time
from fake_useragent import UserAgent
from lxml import etree

def get_link_list(content):
    pat = 'comics:\[{(id.*)recommendTopics'
    res = re.findall(pat, str(content))
    pat1 = re.compile('id:(.*?),title:"(.*?)"', re.S)
    chap_id_title_list = re.findall(pat1, str(res))
    for id, titles in chap_id_title_list[:-1]:
        mkdir_file(titles)
        get_img_list(id)

def get_img_list(id):
    img_start_url = "https://www.kuaikanmanhua.com/web/comic/"
    img_url = img_start_url + id + "/"
    img_path = img_start_url.replace("https://www.kuaikanmanhua.com", "") + id + "/"
    global headers
    headers["Path"] = img_path
    headers["Referer"] = cartoon
    req = requests.get(img_url, headers=headers)
    if req.status_code == 200:
        content = req.text
        contents = content.replace('\\u002F', '/')
        pat = '{width:[a-z],height:[a-z],url:"(.*?)"}'
        img_url_list = re.findall(pat, contents)
        for img_url in img_url_list:
            down_img(img_url)
    else:
        time.sleep(5)
        print("获取失败",req.status_code,img_url)

def mkdir_file(titles):
    path = "e:/python/%s/%s" %(title[0],titles)
    if not os.path.exists(path):
        os.makedirs(path)

def down_img(img_url):
    # id获取
    id_pat = 'https://p1.kkmh.com/image/[a-z]([1-9].{1,6})/'
    id_res = re.search(id_pat, img_url)
    referer = "https://www.kuaikanmanhua.com/web/comic/%s/" % id_res.group(1)
    #添加头请求消息
    global headers
    headers["Authority"] = "p1.kkmh.com"
    headers["Path"] = img_url.replace("https://p1.kkmh.com", "")
    headers["Referer"] = referer
    # titles获取
    title_req = requests.get(referer,headers=headers)
    title_content = title_req.text
    html = etree.HTML(title_content)
    chap_title = html.xpath('//h3[@class="title"]/text()')[2].replace("-", "").strip()
    # 文件命名
    img_name_pat = '[0-9]/(.*?)\?sign'
    img_name_pat1 = '/(.*)'
    res = re.search(img_name_pat, str(img_url))
    img_name = re.search(img_name_pat1, res.group(1))
    print(id_res.group(1),img_name.group(1))
    file_name = id_res.group(1) + " " + img_name.group(1)
    path = "e:/python/%s/%s" %(title[0],chap_title)
    req = requests.get(img_url, headers=headers)
    content = req.content
    if os.path.exists(path):
        os.chdir(path)
        if req.status_code == 200:
            try:
                with open(file_name, "wb") as f:
                    f.write(content)
            except:
                print("图片保存异常", img_url)
                time.sleep(2)
                down_img(img_url)
        else:
            time.sleep(2)
            down_img(img_url)
    else:
        mkdir_file(chap_title)

#主函数
def main():
    #1.获取漫画章节链接
    get_link_list(content)

    #2.获取每章节漫画源src
    # get_img_list()

    #3.创建储存文件夹
    # mkdir_file()

    #4.开始下载漫画
    #down_img()

#主线程
if __name__ == '__main__':
    print('\n' + " " * 43 + "此程序为获取快看漫画中的漫画图片" + " " * 43 + '\n')
    count = 1
    while True:
        if count > 3:
            print("!" * 43 + " 输入有误，自动程序退出 " + "!" * 43)
            break
        cartoon = input("请输入漫画链接地址(例:https://www.kuaikanmanhua.com/web/topic/1128/):")
        print(' ')
        pat = re.compile("https://www.kuaikanmanhua.com/web/topic/([1-9].*?)/", re.S)
        link = re.findall(pat, cartoon)
        ua = UserAgent()
        headers = {
            "Referer": "https://www.kuaikanmanhua.com/",
            "User-agent": ua.random
        }
        if link:
            req = requests.get(cartoon, headers=headers)
            content = req.text
            html = etree.HTML(content)
            title = html.xpath('//h3[@class="title"]/text()')
            print(" " * 39 + '将爬取《%s》,是否开始爬取（yes/no）：' % title[0] + ' ' * 43)
            infrom = input()
            print(' ')
            if infrom == 'yes' or infrom == 'y':
                print('\n' + "*" * 43 + ' 开始爬取《%s》 ' % title[0] + "*" * 43 + '\n')
                start = time.time()
                main()
                end = time.time()
                print("此次《%s》爬取所用时间为："%title[0],end-start)
                print('\n' + "*" * 43 + " 爬取《%s》结束 " % title[0] + "*" * 43 + '\n')
                next = input("是否继续进行爬取,默认回车退出（yes/no）:")
                if next == 'yes' or next == 'y':
                    print(' ')
                    continue
                else:
                    print('\n' + " " * 51 + "[ 退出爬取 ]" + "" * 43 + '\n')
                    break
            else:
                print(' ' * 46 + "放弃爬取《%s》" % title[0] + ' ' * 43 + '\n')
        else:
            count += 1
