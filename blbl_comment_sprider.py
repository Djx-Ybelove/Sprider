import re
import requests
import time
import pandas as pd


# 定义一个类，用于爬取Bilibili视频的评论
class BilibiliCommentSpider(object):
    def __init__(self, url, filename):
        self.url = url  # 视频页面的URL
        self.filename = filename  # 保存评论数据的文件名
        self.comment_url = "https://api.bilibili.com/x/v2/reply/main"  # 获取评论的API
        self.rp_url = "https://api.bilibili.com/x/v2/reply/reply"  # 获取回复的API
        self.oid = ""  # 视频的ID
        self.headers = {
            # 请求头，模拟浏览器访问
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
            # 如果报错，请修改cookie值
            "cookie": "buvid3 = ED3B4971 - 9906 - 2D56 - DB22 - EEEB842EE4D367574infoc;b_nut = 1709876266;rpdid = | (u)~m~Y | ~R | 0J'u~|m)~YkY~; _uuid=96C82E55-3BAE-1068F-EA10F-57A392E10D2B251146infoc; DedeUserID=300634435; DedeUserID__ckMd5=5d4fc03fcbe1acc4; enable_web_push=DISABLE; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW2; header_theme_version=CLOSE; buvid4=96B01A6B-4755-7756-ACAB-D7C93A25A55516150-023100517-uLsJXXTv6Dq8%2BM10qRlm%2Fg%3D%3D; buvid_fp_plain=undefined; hit-dyn-v2=1; LIVE_BUVID=AUTO8117166272818811; CURRENT_BLACKGAP=0; is-2022-channel=1; PVID=1; home_feed_column=5; browser_resolution=1699-943; CURRENT_QUALITY=80; CURRENT_FNVAL=4048; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjUwMDg2MjIsImlhdCI6MTcyNDc0OTM2MiwicGx0IjotMX0._OppP7wGjAK43yD7pWXQAQlLsevYlvhP9KP3LlzgGho; bili_ticket_expires=1725008562; SESSDATA=2d3c76dc%2C1740357249%2C1e88d%2A81CjDNYu9u6SZMc7P9ZtVOUrN0kav-GnnHpuuPfv8xgyOjOH6lqZqTxUgnjF0f4NF9NfUSVjlQRXFNT1VPeF9WSVhsM2E1b0ptTFZvTVlMUnd6YldsZmhXSFJhZ3ZpUU4xUXU2R09RcDh3azV5Z2k4Vm1OdmNqamRUdjlQRlVaWUUwU0lGRm1qM0dBIIEC; bili_jct=3f1c2e67a5e5d654bdfbf454545c10da; sid=6w6yus7u; share_source_origin=copy_web; bp_t_offset_300634435=970658747720400896; bsource=search_bing; fingerprint=926dac40d5c0d4543bd5d01e90c9956d; buvid_fp=926dac40d5c0d4543bd5d01e90c9956d; b_lsid=A9896C76_1919D503D33"
        }
        self.uname = []  # 存储用户名
        self.sex = []  # 存储用户性别
        self.like = []  # 存储点赞数
        self.comment = []  # 存储评论内容

    def get_oid(self):  # 获取视频的OID以及评论数（视频ID）
        response = requests.get(url=self.url, headers=self.headers)
        html = response.text
        oid = re.findall('window.__INITIAL_STATE__={.*,"aid":(.*?),', html)
        reply_num = re.findall('window.__INITIAL_STATE__={.*,"reply":(.*?),', html)
        self.oid = oid[0]
        return int(reply_num[0])

    def get_top_comment(self):  # 获取热评
        params = {
            "oid": self.oid,
            "type": 1,
            "next": 1
        }
        res = requests.get(url=self.comment_url, params=params, headers=self.headers).json()
        comments = res['data']["top_replies"]
        if comments != []:
            for com in comments:
                self.uname.append(com['member']['uname'])
                self.sex.append(com['member']['sex'])
                self.like.append(com['like'])
                self.comment.append(com['content']['message'])
                if com["rcount"] != 0:  # 获取评论的回复
                    rpid = com['rpid']
                    for i in range(1, com["rcount"] // 20 + 2):
                        time.sleep(2)
                        params_rp = {
                            'oid': self.oid,
                            'root': rpid,
                            'type': 1,
                            'pn': i}
                        res_rp = requests.get(url=self.rp_url, params=params_rp, headers=self.headers).json()
                        comments_rp = res_rp['data']['replies']
                        if comments_rp != []:
                            for com_rp in comments_rp:
                                self.uname.append(com_rp['member']['uname'])
                                self.sex.append(com_rp['member']['sex'])
                                self.like.append(com_rp['like'])
                                self.comment.append(com_rp['content']['message'])
                        else:
                            break

    def get_comment(self, reply_num):  # 获取所有评论
        for page in range(1, reply_num // 20 + 2):
            time.sleep(2)
            params = {
                "oid": self.oid,
                "type": 1,
                "next": page,
            }
            res = requests.get(url=self.comment_url, params=params, headers=self.headers).json()
            comments = res['data']["replies"]
            if comments != []:
                for com in comments:
                    self.uname.append(com['member']['uname'])
                    self.sex.append(com['member']['sex'])
                    self.like.append(com['like'])
                    self.comment.append(com['content']['message'])
                    if com["rcount"] != 0:
                        rpid = com['rpid']
                        for i in range(1, com["rcount"] // 20 + 2):
                            time.sleep(2)
                            params_rp = {
                                'oid': self.oid,
                                'root': rpid,
                                'type': 1,
                                'pn': i}
                            res_rp = requests.get(url=self.rp_url, params=params_rp, headers=self.headers).json()
                            comments_rp = res_rp['data']['replies']
                            if comments_rp != []:
                                for com_rp in comments_rp:
                                    self.uname.append(com_rp['member']['uname'])
                                    self.sex.append(com_rp['member']['sex'])
                                    self.like.append(com_rp['like'])
                                    self.comment.append(com_rp['content']['message'])
                            else:
                                break
            else:
                break
            print(f"=================================已存储第{page}页评论=====================================")

    def main(self):  # 主函数，执行爬取流程
        reply_num = self.get_oid()
        self.get_top_comment()
        self.get_comment(reply_num)
        print("存储完毕！！！")
        df = pd.DataFrame({"用户名称": self.uname,
                           "用户性别": self.sex,
                           "获赞": self.like,
                           "评论内容": self.comment})
        print(len(df))
        df = df.to_excel(rf'{self.filename}.xlsx', index=False)


if __name__ == '__main__':
    url = input("请输入视频链接:")
    filename = input("请输入保存文件名:")
    sprider = BilibiliCommentSpider(url, filename)
    sprider.main()
