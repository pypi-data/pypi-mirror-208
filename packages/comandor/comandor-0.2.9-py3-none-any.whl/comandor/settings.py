from pydantic import ValidationError

from comandor.models import Setting
from comandor.log import log

import json
import os


# load setting form file and return setting
# default use ./.comandor
def loadSetting(file: str = ".comandor") -> Setting:
    if not os.path.exists(file):
        raise Exception("Config file not found!")

    setting: Setting
    with open(file, "r") as f:
        try:
            op = json.load(f)
            setting = Setting(**op)

        except ValidationError as e:
            log.error(e)
            raise e

        except json.JSONDecodeError as e:
            log.error(e)
            raise e

    return setting
