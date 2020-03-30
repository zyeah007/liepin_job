#!/usr/bin/env python
# coding=utf-8


import requests
from lxml import etree
import time
import os
import json
import codecs
import random
import functools

BASE_URL = 'https://www.liepin.com/zhaopin/'
HEADS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/80.0.3987.132 Safari/537.36'
}
COOKIES = '__uuid=1584362896230.08; abtest=0; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1584362905; access_system=C; fe_se=-1584366268132; user_roles=0; user_photo=5822947562f0ac1627d841bf05a.jpg; user_name=%E9%83%91%E4%B8%9A; need_bind_tel=false; new_user=false; c_flag=3c5d1d41a4531892e25e4179855a6002; gr_user_id=ea67d51d-b6bf-4e84-8ed4-6757df0ee5e4; bad1b2d9162fab1f80dde1897f7a2972_gr_last_sent_cs1=2737aeb1674e1e891a667e00ad0d9493; grwng_uid=db39f0cd-1e16-49c2-b0c1-e29d58072945; fe_im_openchatwin=0_0; fe_im_opencontactlist=0_0; JSESSIONID=1762103C810932B6216EB574E029004B; __tlog=1584362896240.71%7C00000000%7CR000000058%7C00000000%7C00000000; fe_im_socketSequence_0=2_0_2; bad1b2d9162fab1f80dde1897f7a2972_gr_session_id=e0fe9e6a-cdd8-4e93-97f5-95c761f8668c; UniqueKey=2737aeb1674e1e891a667e00ad0d9493; lt_auth=7%2BdcOHYHyl2s7HWM22pc4adK3tOgBmTI9n4MjR4F0Na7XaXr4P3mQQKOqLgGxAMhx050csULNLj6MeH%2FyHNC40MVwGmnkoCzueW40XYeRt11HuyflMX8k87XQqUkrXg6yUpynw%3D%3D; bad1b2d9162fab1f80dde1897f7a2972_gr_last_sent_sid_with_cs1=e0fe9e6a-cdd8-4e93-97f5-95c761f8668c; imClientId=19e71675eed5ab87c7385431eb0b985d; imId=19e71675eed5ab87478d7731ddfe6f52; imClientId_0=19e71675eed5ab87c7385431eb0b985d; imId_0=19e71675eed5ab87478d7731ddfe6f52; bad1b2d9162fab1f80dde1897f7a2972_gr_session_id_e0fe9e6a-cdd8-4e93-97f5-95c761f8668c=true; bad1b2d9162fab1f80dde1897f7a2972_gr_cs1=2737aeb1674e1e891a667e00ad0d9493; __session_seq=27; __uv_seq=7; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1584491121'


def func_test_log(test_func):
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        print('*-' * 10)
        print("当前正在测试:%s" % test_func.__name__)
        start = time.time()
        test_func(*args, **kwargs)
        end = time.time()
        print("本次测试用时%.4f秒" % (end - start))
        print("函数%s测试完成!" % test_func.__name__)
        print('+-' * 10)
        print('\n\n')

    return wrapper


def get_cookie(cookie_str: str):
    cookies = {}
    for line in cookie_str.split(';'):
        key, value = line.split('=', 1)
        cookies[key] = value
    return cookies


class CrawlJobs(object):
    def __init__(self, key=None, save_path=None):
        self.key = key
        self.save_path = os.path.join(os.getcwd(), save_path)
        self.error_log_file = os.path.join(os.getcwd(), 'error.txt')
        self.log_file = os.path.join(os.getcwd(), 'fa__job_links0315.txt')

    def get_one_page_links(self, curPage):

        params = {
            'pubTime': 30,
            'key': self.key,
            'init': -1,
            'searchType': 1,
            'headckid': 'a3a5e7bc87599733',
            'fromSearchBtn': 2,
            'sortFlag': 15,
            'ckid': '5ce650b85cedd497',
            'degradeFlag': 0,
            'jobKind': 2,
            'siTag': 'I-7rQ0e90mv8a37po7dV3Q~UoKQA1_uiNxxEb8RglVcHg',
            'd_sfrom': 'search_fp_bar',
            'd_ckId': '326ae63369b609a6304b8b57ed423d73',
            'd_curPage': curPage,
            'd_pageSize': 40,
            'd_headId': '354cdc300b49eb693f681d861f12b49',
            'curPage': curPage + 1
        }
        info_count = 0
        try:
            session = requests.Session()
            cookies = get_cookie(COOKIES)
            r = session.get(url=BASE_URL, headers=HEADS, cookies=cookies, params=params)
            r.raise_for_status()
            html = r.text
            html = etree.HTML(html)
            job_list = html.xpath("//ul[@class='sojob-list']/li")
            for li in job_list:
                job_url = li.xpath('.//h3/a/@href')[0].strip()
                job_title = li.xpath('.//h3/a/text()')[0].strip()
                company_name = li.xpath(".//p[@class='company-name']/a/text()")[0].strip()
                info = [
                    str(company_name),
                    str(job_title),
                    str(job_url)
                ]
                with codecs.open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(','.join(info))
                    f.write('\n')
                    # writer = csv.writer(f)
                    # writer.writerow(info)
                    info_count += 1
            print('成功取得第%d页%d条数据' % (curPage + 1, info_count))
            time.sleep(5)

        except:
            print('第%d页链接失败！' % (curPage + 1))
            time.sleep(5)
            self.get_one_page_links(curPage)
        return info_count

    @func_test_log
    def save_all_links(self, page_limit=10):
        """
        保存所有url
        :param page_limit:
        :return:
        """
        for i in range(93, page_limit):
            self.get_one_page_links(i)
            print('\r完成进度:%.3f%%' % ((i + 1) * 100 / page_limit), end='')

    @staticmethod
    def get_job_infos(job_url):
        """
        从具体招聘信息页获取招聘信息
        :param job_url:
        :return: 需要的所有字段
        """
        try:
            session = requests.Session()
            cookies = get_cookie(COOKIES)
            r = session.get(job_url, headers=HEADS, cookies=cookies, timeout=5)
            r.raise_for_status()
            html = r.text
            html = etree.HTML(html)
            title = html.xpath('//h1/text()')[0].strip()
            company_name = html.xpath("//div[@class='title-info']/h3/a/text()")[0].strip()
            salary = html.xpath("//p[@class='job-item-title']/text()")[0].strip()
            city = html.xpath("//p[@class='basic-infor']/span/a/text()")[0].strip()
            job_quals = html.xpath("//div[@class='job-qualifications']//span/text()")
            education = job_quals[0].strip()
            experience = job_quals[1].strip()
            language = job_quals[2].strip()
            age = job_quals[3].strip()
            description = html.xpath(
                "//div[@class='job-item main-message job-description']//div[@class='content content-word']//text()")
            job_desc = ','.join(description)
            industry = html.xpath("//ul[@class='new-compintro']/li/a/@title")
            base_url = os.path.basename(job_url)
            job_id = base_url.split('.')[0]
            data = {
                'id': job_id,
                'company': company_name,
                'title': title,
                'salary': salary,
                'city': city,
                'industry': industry,
                'education': education,
                'experience': experience,
                'language': language,
                'age': age,
                'description': job_desc
            }
            time.sleep(random.randint(2, 6))
            return data
        except:
            print('链接失败：%s' % job_url)
            with open('failed_url.txt', 'a') as f:
                f.write(job_url + '\n')
                time.sleep(5)
            return None

    def save_to_json(self, new_data: json, save_path: str):
        """

        :param new_data: json文件
        :param save_path: 文件保存路径
        :return:
        """
        if not os.path.exists(save_path):
            with open(save_path, 'w', encoding='utf-8') as f1:
                res = {'data': [new_data]}
                json.dump(res, f1, indent=4, ensure_ascii=False)
        else:
            with open(save_path, 'r', encoding='utf-8') as f2:
                res = json.load(f2)
                current_data = res['data']
                id_list = self.get_ids(current_data)
            if new_data['id'] not in id_list:
                res['data'].append(new_data)
                with open(save_path, 'w', encoding='utf-8') as f3:
                    json.dump(res, f3, indent=4, ensure_ascii=False)

    @staticmethod
    def get_ids(data_list: list):
        return [data['id'] for data in data_list]

    def crawl_all_infos(self, urls):
        """

        :param urls:
        :return:
        """
        get_count = 0
        total_count = len(urls)
        for url in urls:
            new_data = self.get_job_infos(url)
            if new_data is not None:
                self.save_to_json(new_data, save_path=self.save_path)
                get_count += 1
            print('\r爬取进度:%.4f%%' % (get_count * 100 / total_count), end='')

    def read_urls(self):
        with open(self.log_file, 'r', encoding='utf-8') as f:
            res = f.readlines()
        return [info.split(',')[-1].strip() for info in res]


def main():
    job_crawl = CrawlJobs(key='财务分析', save_path='财务分析2.json')
    # job_crawl.save_all_links(page_limit=100)
    urls = job_crawl.read_urls()
    print('共读取%d条数据。' % len(urls))
    job_crawl.crawl_all_infos(urls)


if __name__ == "__main__":
    main()
