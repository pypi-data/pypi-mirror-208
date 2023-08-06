
import pyhttpx
from loguru import logger

from .base import BaseCracker

import warnings
warnings.filterwarnings('ignore')


class CloudFlareCracker(BaseCracker):
    
    cracker_name = "cloudflare"
    cracker_version = "universal"    

    """
    cloudflare cracker
    :param href: 触发 cloudfalre 验证的首页地址
    :param user_agent: 请求流程使用 ua, 必须使用 MacOS Firefox User-Agent, 否则可能破解失败
    :param html: 触发 cloudflare 验证的响应源码, 特征: window._cf_chl_opt=.../window["CF$params"]=...
    :param cookies: 触发验证必须的 cookies, 默认 {} 
    :param ja3: 请求客户端使用的 ja3 指纹, 例如: "771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-34-51-43-13-45-28-21,29-23-24-25-256-257,0", 不传则默认使用随机 ja3 指纹, 可通过 https://tls.peet.ws/api/clean 查询你的请求客户端的 tls 指纹, 然后填入返回的 ja3 字段值, 则我们的破解流程将会使用你上传的 ja3 指纹, 从而保持 tls 指纹一致
    调用示例:
    cracker = CloudFlareCracker(
        href=href,
        user_token="xxx",

        # debug=True,
        # check_useful=True,
        # proxy=proxy,
        # ja3="771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-34-51-43-13-45-28-21,29-23-24-25-256-257,0",
        # check_proxy=True,
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href"]
    # 默认可选参数
    option_params = {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0",
        "html": "",
        "headers": {},
        "cookies": {},
        "ja3": "",
    }

    @staticmethod
    def parse_proxy(proxy):
        _auth, _proxy = None, None
        if proxy:
            _proxy = proxy.split("/")[-1]
            if "@" in _proxy:
                _proxy_split = _proxy.split("@")
                _proxy = _proxy_split[1]
                _auth = tuple(_proxy_split[0].split("/")[-1].split(":"))
        return _proxy, _auth

    def tls_session(self, ja3=None):
        if not hasattr(self, "_tls_session"):
            self._tls_session = pyhttpx.HttpSession(ja3=ja3, http2=True)
        return self._tls_session
    
    def _checktls(self, tls={}):
        try: 
            ja3_ret = self.session.get('https://tls.peet.ws/api/clean', headers={
                "User-Agent": self.user_agent
            }, timeout=10).json
            node_ja3_hash = tls.get("ja3_hash")
            py_ja3_hash = ja3_ret.get("ja3_hash")
            node_h2_hash = tls.get("akamai_hash")
            py_h2_hash = ja3_ret.get("akamai_hash")
            
            if not self.randomtls:
                node_ja3_hash = 'cd08e31494f9531f560d64c695473da9'
                node_h2_hash = '46cedabdca2073198a42fa10ca4494d0'
            if node_ja3_hash:
                if node_ja3_hash == py_ja3_hash:
                    if self.debug: 
                        logger.success("ja3 指纹一致: {}".format(py_ja3_hash))
                else:
                    if self.debug: 
                        logger.warning("ja3 指纹不一致, node_ja3_hash: {} | py_ja3_hash: {}".format(node_ja3_hash, py_ja3_hash))
            else:
                if self.debug: 
                    logger.warning("未检查 node tls, py ja3 hash => " + py_ja3_hash)

            if node_h2_hash:
                if node_h2_hash == py_h2_hash:
                    if self.debug: 
                        logger.success("h2 指纹一致: {}".format(py_h2_hash))
                else:
                    if self.debug: 
                        logger.warning("h2 指纹不一致, node_h2_hash: {} | py_h2_hash: {}".format(node_h2_hash, py_h2_hash))
            else:
                if self.debug: 
                    logger.warning("未检查 node tls, py h2 hash => " + py_h2_hash)
        except Exception as e:
            if self.debug: 
                logger.warning("检查 tls 出错: {}".format(e.args))
    
    def _check_proxy(self):
        _proxy = self.session.get("https://icanhazip.com", proxies={
            "https": self._proxy,
            "https": self._proxy
        }, proxy_auth=self._auth).text.strip()
        if _proxy == self._proxy.split(":")[0]:
            if self.debug: 
                logger.success("代理一致")
        else:
            if self.debug: 
                logger.error("代理不一致: {}".format(_proxy))
    
    def response(self, result):
        cookies = result.get("cookies") or {}
        self.cookies.update(cookies)
        if self.debug: 
            logger.debug("cookies: {}".format(self.cookies))
        self.wanda_args["cookies"] = self.cookies
        result.update({
            "cookies": self.cookies,
        })
        return result
    
    def check(self, ret):
        tls = ret.get("tls", {})
        ja3 = tls.get("ja3")
        self.session = self.tls_session(ja3 or self.ja3)
        
        html = ret.get("html")
        if not html:
            return False
        return True
