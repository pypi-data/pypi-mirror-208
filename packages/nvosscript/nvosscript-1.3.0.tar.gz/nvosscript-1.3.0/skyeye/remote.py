import requests
import os
import logging
import json
from start import commonUtil


daemon_network = "https://nvos-toolchain.nioint.com"

daemon_network_mapping = {
    "prod": "https://nvos-toolchain.nioint.com",
    "stg": "https://nvos-toolchain-stg.nioint.com",
    "dev": "https://nvos-toolchain-dev.nioint.com"
}

daemon_network_front_mapping = {
    "prod": "https://ndtc.nioint.com/#/nvosTool/spaceList",
    "stg": "https://ndtc-stg.nioint.com/#/nvosTool/spaceList",
    "dev": " https://soa-tools-dev.nioint.com/#/nvosTool/spaceList"
}

# 导入全局日志记录器
logger = logging.getLogger(__name__)

def upload_file():
    print("upload_file")

def get_current_env():
    global daemon_network
    result = {}
    if os.path.exists(os.path.expanduser(os.path.join('~', '.ndtcrc', 'skyeye_env'))):
        with open(os.path.expanduser(os.path.join('~', '.ndtcrc', 'skyeye_env')), 'r')as f:
            result = json.loads(f.readline().strip())
            daemon_network = result["cloud"]
            tip = result["tip"]
            env = result["env"]
            logger.info(f"current env:{env} this cloud linked:{tip} daemon_network:{daemon_network}")
    if result == {}:
        result["cloud"] = daemon_network_mapping.get('prod')
        result['env'] = 'prod'
        result['tip'] = daemon_network_front_mapping.get('prod')
    return result


def switch_env(env):
    val = daemon_network_mapping.get(env)
    if len(val) == 0:
        return
    tip = daemon_network_front_mapping.get(env)
    result = {"cloud":val,"tip":tip,"env":env}
    commonUtil.check_local_workspace()
    with open(os.path.expanduser(os.path.join('~','.ndtcrc' ,'skyeye_env')), 'w') as f:
        f.writelines(json.dumps(result))
    print(f"this script current env:{env} and cloud linked:{tip}")
