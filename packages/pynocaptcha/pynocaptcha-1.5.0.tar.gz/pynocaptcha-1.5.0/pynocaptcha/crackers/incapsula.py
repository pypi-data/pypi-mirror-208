
import requests
from .base import BaseCracker


class IncapsulaReese84Cracker(BaseCracker):
    
    cracker_name = "incapsula"
    cracker_version = "reese84"    

    """
    incapsula cracker
    :param href: 触发 incapsula 盾验证的首页地址
    :param user_agent: 请求流程使用 ua, 必须使用 MacOS Firefox User-Agent, 否则可能破解失败
    :param submit: 是否提交验证接口, 不提交则返回计算参数
    调用示例:
    cracker = IncapsulaCracker(
        href=href,
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',

        user_token="xxx",

        # debug=True,
        # check_useful=True,
        # proxy=proxy,
        # submit=False
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href", "user_agent"]
    # 默认可选参数
    option_params = {
        "script": "",
        "submit": True,
    }
    
    def check(self, cookies):
        headers = {
            'upgrade-insecure-requests': '1',
            'user-agent': self.user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        resp = requests.get("/".join(self.href.split("/")[:3])+ "/", headers=headers, cookies=cookies)
        return 'ROBOTS' not in resp.text


class IncapsulaUtmvcCracker(BaseCracker):
    
    cracker_name = "incapsula"
    cracker_version = "utmvc"    

    """
    incapsula cracker
    :param script: Incapsula js 脚本字符串
    :param cookies: 携带 incap_sess_xxx 的 cookies, {"incap_ses_xxx": "xaxa"}
    调用示例:
    cracker = IncapsulaUtmvcCracker(
        script=script,
        cookies={},
        
        user_token="xxx",

        # debug=True,
        # check_useful=True,
        # proxy=proxy,
        # submit=False
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["script", "cookies"]
