import unittest
import functools
import time
from liepin_job.crawl_job_info import CrawlJobs
import os
import csv
import json


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


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    @func_test_log
    def test_get_job_infos(self):
        url = 'https://www.liepin.com/job/1926508809.shtml'
        data = CrawlJobs.get_job_infos(url)
        self.assertEqual(data['id'], '1926508809')

    # @func_test_log
    # def test_crawl_one_page(self, page_count=1):
    #     crawl = CrawlJobs(key='python')
    #     log_file = crawl.log_file
    #     if os.path.exists(log_file):
    #         os.remove(log_file)
    #     info_count = crawl.get_one_page_links(curPage=page_count)
    #     f = open(log_file, 'r', encoding='gbk')
    #     res = f.readlines()
    #     f.close()
    #     self.assertEqual(info_count, len(res))
    #
    # @func_test_log
    # def test_save_job_infos(self):
    #     csv_file = os.path.join(os.getcwd(), 'job_links.csv')
    #     save_path = 'test_job_infos.json'
    #     crawl = CrawlJobs(key='python', save_path=save_path)
    #     if os.path.exists(save_path):
    #         os.remove(save_path)
    #     f = open(csv_file, 'r', encoding='gbk')
    #     links = f.readlines()
    #     f.close()
    #     for info in links:
    #         url = info.split(',')[-1].strip()
    #         new_data = crawl.get_job_infos(job_url=url)
    #         crawl.save_to_json(new_data, save_path)
    #     fp = open(save_path, 'r', encoding='utf-8')
    #     json_data = json.load(fp, encoding='utf-8')
    #     data = json_data['data']
    #     fp.close()
    #     self.assertEqual(len(data), len(links))


if __name__ == '__main__':
    unittest.main()
