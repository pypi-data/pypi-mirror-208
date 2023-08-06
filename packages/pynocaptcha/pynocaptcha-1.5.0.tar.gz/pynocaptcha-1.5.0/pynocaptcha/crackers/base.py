
import requests
from loguru import logger
from typing import Any


class BaseCracker:
    
    # 破解器
    cracker_name = "base"
    
    # 破解版本
    cracker_version = "universal"
    
    # 必须参数列表
    must_check_params = []
    
    # 可选参数
    option_params = {}
    
    # 需要删除的多余参数
    delete_params = []
    
    def __init__(
        self,    
        user_token: str = None,
        developer_id: str = None,   
        user_agent: str = None,
        proxy: str = None, 
        timeout: int = 30,
        debug: bool = False,
        check_useful: bool = False,
        max_retry_times: int = 3,
        internal=True,
        internal_api=True,
        show_ad=True,
        **kwargs
    ) -> None:
        """
        :param user_token: nocaptcha.io 用户 token
        :param developer_id: nocaptcha.io 用户上级代理 token
        :param user_agent: 请求流程使用 ua
        :param proxy: 请求流程代理, 不传默认使用系统代理, 某些强制要求代理一致或者特定区域的站点请传代理, 支持协议 http/https/socks5, 代理格式: {protocol}://{ip}:{port}（如有账号验证：{protocol}://{user}:{password}@{ip}:{port}）
        :param timeout: 破解接口超时时间(秒)
        :param debug: 是否开启 debug 模式
        :param check_useful: 检查破解是否成功
        :param max_retry_times: 最大重试次数
        :param internal: 是否使用国内代理
        """
        if show_ad:
            logger.debug("感谢选择 nocaptcha, 我们只做别人做不到的(手动狗头)~")
            logger.debug("欢迎推荐注册, 官网地址: https://www.nocaptcha.io/")
        self.user_token = user_token
        if not self.user_token:
            raise Exception("缺少用户凭证")
        self.developer_id = developer_id
        self.user_agent = user_agent
        self.proxy = proxy
        self.timeout = timeout
        self.debug = debug
        self.check_useful = check_useful
        self.max_retry_times = max_retry_times

        self.internal_api = internal_api
        self.wanda_args = {
            "internal": internal
        }
        for k in self.must_check_params:
            _v = kwargs.get(k)
            if not hasattr(self, k) or getattr(self, k) is None:
                setattr(self, k, _v)
            self.wanda_args.update({ k: _v })
        for k, v in self.option_params.items():
            _v = kwargs.get(k, v)
            if not hasattr(self, k) or getattr(self, k) is None:
                setattr(self, k, _v)
            self.wanda_args.update({ k: _v })
        
        for k in self.delete_params:
            if k in self.wanda_args:
                del self.wanda_args[k]

        if any(getattr(self, k) is None for k in self.must_check_params):
           raise AttributeError("缺少参数, 请检查")

    def response(self, result: Any):
        return result
        
    def check(self, ret):
        return True
    
    def crack(self):
        headers = {
            "User-Token": self.user_token
        }
        if self.developer_id:
            headers["Developer-Id"] = self.developer_id
        
        if self.user_agent:
            self.wanda_args["user_agent"] = self.user_agent
        if self.proxy:
            self.wanda_args["proxy"] = self.proxy

        retry_times = 0        
        resp = {}
        while retry_times < self.max_retry_times:
            try:
                resp = requests.post(
                    f"http://{'xn--fjqs46frol.com' if self.internal_api else 'api.nocaptcha.io' }/api/wanda/{self.cracker_name}/{self.cracker_version}", 
                    headers=headers, json=self.wanda_args, timeout=self.timeout
                ).json()
                if self.debug:
                    logger.info(resp)
                break
            except Exception as e:
                if self.debug:
                    logger.error(e)
                retry_times += 1
        wanda_ret = resp.get("data")
        if not wanda_ret:
            if self.debug:
                logger.error(resp.get("msg"))
            return
        ret = self.response(wanda_ret)
        if self.check_useful:
            if self.check(wanda_ret):
                if self.debug:
                    logger.success("crack success")
            else:
                retry_times += 1
                if retry_times < self.max_retry_times:
                    return self.crack()
                else:
                    logger.error("crack fail")
        return ret
