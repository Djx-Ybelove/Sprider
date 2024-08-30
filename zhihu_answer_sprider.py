import requests
import pandas as pd
from lxml import etree
import json
import re
import datetime
from bs4 import BeautifulSoup
import time


# 定义一个知乎评论爬虫类
class ZhihuCommentSpider(object):
    def __init__(self, url, filename):
        self.url = url  # 视频页面的URL
        self.filename = filename  # 保存评论数据的文件名
        self.answer_url = ""  # 用于存储回答数据的URL
        self.comment_url = ""  # 用于存储评论数据的URL
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            # 如若报错，请更改自己的cookie在运行
            "cookie": "SESSIONID=ZxTYQEzlUpTE4qM2z3woz6GYNjjtAneQzg9paatkRT4; JOID=VlsXBE9y8jhx_TKdTXDVbeVuc-dcVtAeUd4Wv2tR1hpX3RG5b-kY8BT6NJlLm17PssQxFTr6IhK0t6vHTFZqLR0=; osd=UFAUAU90-Tt0_TSWTnXVa-5tdudaXdMbUdgdvG5R0BFU2BG_ZOod8BLxN5xLnVXMt8Q3Hjn_IhS_tK7HSl1pKB0=; _zap=c8554ff3-5517-4ae3-9961-055b08db6229; d_c0=AMDZuxx-RxiPToI1LkACSD-1EVSod6zRl58=|1709894649; _xsrf=bR7dEUPunBI4vwzqB5AGh0jUlPR3vnsV; __snaker__id=n5Qi2Xoi0wPjxhAS; q_c1=5db63780530642fc84893bcc80d94d27|1720697971000|1720697971000; z_c0=2|1:0|10:1724404256|4:z_c0|80:MS4xUTJDUFNBQUFBQUFtQUFBQVlBSlZUVHVEcUdjZGlkS1I2bDRGaS00bF9oM1lwZkRpTm5vSWl3PT0=|aca394bf021ae8f699bca43db783d72a645bfb5cf9c1112f2f6b765d3d7512cd; tst=r; __zse_ck=001_oC7YPr8gq7jImdkdI+Q04KCLKRToq=Px8R75dWpVfsJuD3uqWyXESdh0k/1H+g2WskNcP5QPXSxV39xU8afpRaSE5H9bj5fi9ikNvUMO6VufZhLYpGZz=AKpaGR7e/FL; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1724567733,1724579104,1724633163,1724837531; HMACCOUNT=06CFD66F0024C981; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1724932428; BEC=4589376d83fd47c9203681b16177ae43"
        }
        # 初始化存储数据的列表
        self.uname = []
        self.created_time = []
        self.comments_counts = []
        self.like = []
        self.content = []

    # 获取回答的URL
    def get_answer_url(self):
        response = requests.get(url=self.url, headers=self.headers)
        html = response.text
        tree = etree.HTML(html)
        script = tree.xpath('/html/body/script[2]/text()')  # 使用xpath和正则表达式获取问题ID和回答的初始URL
        cursor_json = json.loads(script[0])
        question_id = re.findall(r".*/question/(\d+).*", self.url)
        print(question_id[0])
        self.answer_url = cursor_json['initialState']["question"]["answers"][question_id[0]]["next"]
        self.answer_url = re.sub(r"limit=(\d)", "limit=20", self.answer_url)  # 修改回答的limit参数为20
        self.get_answer_front(cursor_json)

    # 获取回答的前段部分
    def get_answer_front(self, cursor_json):
        for value in cursor_json['initialState']['entities']["answers"].values():
            self.uname.append(value["author"]["name"])
            self.created_time.append(str(datetime.date.fromtimestamp(value["createdTime"])))
            self.comments_counts.append(value["commentCount"])
            self.like.append(value["voteupCount"])
            content = ""
            text = value["content"]
            soup = BeautifulSoup(text, 'lxml')
            p_tags = soup.find_all('p')
            for p in p_tags:
                content = content + p.get_text()
            self.content.append(content)
            if value["commentCount"] > 0:
                self.comment_url = f"https://www.zhihu.com/api/v4/answers/{value['id']}/comments?limit=20&offset=0"
                self.get_comment()
        print(f"===================================已存储第{1}页回答=========================================")

    # 获取评论的方法
    def get_comment(self):
        res_comment = requests.get(url=self.comment_url, headers=self.headers)
        comment_json = res_comment.json()
        comments = comment_json["data"]
        for com in comments:
            self.uname.append(com["author"]["member"]["name"])
            self.created_time.append(str(datetime.date.fromtimestamp(com["created_time"])))
            self.comments_counts.append(0)
            self.like.append(com["vote_count"])
            self.content.append(com["content"])
        if comment_json["paging"]["is_end"]:
            return True
        else:
            self.comment_url = comment_json["paging"]["next"]
            time.sleep(2)
            self.get_comment()

    # 获取回答数据的方法
    def get_answer(self):
        response_answer = requests.get(url=self.answer_url, headers=self.headers)  # 发起请求获取回答数据
        answer_json = response_answer.json()
        answers = answer_json["data"]
        for ans in answers:  # 遍历回答数据，提取所需的字段
            target = ans["target"]
            self.uname.append(target["author"]["name"])
            self.created_time.append(str(datetime.date.fromtimestamp(target["created_time"])))
            self.comments_counts.append(target["comment_count"])
            self.like.append(target["voteup_count"])
            content = ""
            text = target["content"]
            soup = BeautifulSoup(text, 'lxml')
            p_tags = soup.find_all('p')
            for p in p_tags:
                content = content + p.get_text()
            self.content.append(content)
            if target["comment_count"] > 0:  # 如果回答有评论，则获取评论的URL并调用get_comment方法
                self.comment_url = f"https://www.zhihu.com/api/v4/answers/{target['id']}/comments?limit=20&offset=0"
                self.get_comment()
        if answer_json["paging"]["is_end"]:  # 如果回答数据还有下一页，则继续获取
            return True
        else:
            self.answer_url = answer_json["paging"]["next"]
            print(
                f"===================================已存储第{answer_json['paging']['page']}页回答=========================================")
            time.sleep(2)  # 等待2秒，避免过快请求被封IP
            self.get_answer()

    # 主函数，用于启动爬虫
    def main(self):
        self.get_answer_url()
        self.get_answer()
        # 将爬取的数据存储到pandas的DataFrame中
        df = pd.DataFrame({
            "用户名称": self.uname,
            "发表时间": self.created_time,
            "评论数": self.comments_counts,
            "点赞数": self.like,
            "回答内容": self.content
        })
        print(len(df))
        # 将DataFrame保存到Excel文件中
        df.to_excel(rf"{self.filename}.xlsx", index=False)


# 程序入口
if __name__ == '__main__':
    # 从用户那里获取问题页面的URL和保存文件的名称
    sprider = ZhihuCommentSpider(url=input("请输入视频链接:"), filename=input("请输入保存文件名:"))
    # 启动爬虫
    sprider.main()
