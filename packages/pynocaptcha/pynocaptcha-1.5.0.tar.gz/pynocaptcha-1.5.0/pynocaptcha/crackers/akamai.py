
from .base import BaseCracker


class AkamaiV2Cracker(BaseCracker):
    
    cracker_name = "akamai"
    cracker_version = "v2"    

    """
    recaptcha universal cracker
    :param href: 触发验证的页面地址
    :param api: akamai 提交 sensor_data 的地址
    :param telemetry: 是否 headers 中的 telemetry 参数验证形式, 默认 false
    :param _abck: 请求 href 首页返回的 cookie _abck 值, 传了 api 参数必须传该值
    :param bm_sz: 请求 href 首页返回的 cookie bm_sz 值, 传了 api 参数必须传该值
    调用示例:
    cracker = AkamaiV2Cracker(
        user_token="xxx",
        href="xxx",
        api="xxx",
        
        # debug=True,
        # proxy=proxy,
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href"]
    # 默认可选参数
    option_params = {
        "api": "",
        "telemetry": False,
        "_abck": None,
        "bm_sz": None
    }