import os
import time
import traceback

import jinja2
from loguru import logger

from .analyze import analyze_command
from .data_source import (hikari_config, set_config, set_render_params,
                          template_path)
from .Html_Render import html_to_pic
from .model import Hikari, Input, Output, Ship, UserInfo
from .utils import startup

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)
env.globals.update(
    time=time,
    abs=abs,
    enumerate=enumerate,
)


async def init_hikari(
    platform: str,
    PlatformId: str,
    command_text: str = None,
    auto_rendering: bool = True,
    auto_image: bool = True,
    use_broswer: str = "chromium"
) -> Hikari:
    """Hikari初始化，如果进行过set_config，则会覆盖这边的对应配置

    Args:
        platform (str): 平台类型
        PlatformId (str): 平台ID
        command_text (str): 传入指令，不带wws
        auto_rendering (bool): 自动填充模板，默认启用
        auto_image (bool): 是否自动渲染，默认启用，若auto_rending未启用则该项配置无效
        use_broswer (str): chromium/firefox，默认chromium，性能大约为firefox三倍

    Returns:
        Hikari: 可通过Hikari.Output.Data内数据判断是否输出
    """
    try:
        userinfo = UserInfo(Platform=platform, PlatformId=PlatformId)
        ship = Ship()
        input = Input(Command_Text=command_text, ShipInfo=ship)
        output = Output()
        hikari = Hikari(UserInfo=userinfo,
                        Input=input, Output=output)
        hikari = await analyze_command(hikari)
        if not hikari.Status == "error" and hikari.Function:
            hikari: Hikari = await hikari.Function(hikari)
            if hikari.Output.Data_Type == '''<class 'str'>''':
                logger.info(hikari.Output.Data)
                return hikari
            else:
                if auto_rendering:
                    template = env.get_template(hikari.Output.Template)
                    template_data = await set_render_params(hikari.Output.Data)
                    content = await template.render_async(template_data)
                    if auto_image:
                        hikari.success(
                            await html_to_pic(content, wait=0, viewport={"width": hikari.Output.Width, "height": hikari.Output.Height}, use_browser=use_broswer))
                logger.info(hikari.Output.Data_Type)
        if hikari.Output.Data_Type == '''<class 'str'>''':
            logger.info(hikari.Output.Data)
        return hikari
    except Exception:
        logger.error(traceback.format_exc())
        return hikari.error("解析指令时发生错误，请确认输入参数无误")


mtime = os.path.getmtime(template_path/"wws-info.html")
if time.time()-mtime > 86400:
    startup()

logger.add(
    "hikari-core-logs/error.log",
    rotation="00:00",
    retention="1 week",
    diagnose=False,
    level="ERROR",
    encoding="utf-8",
)
logger.add(
    "hikari-core-logs/info.log",
    rotation="00:00",
    retention="1 week",
    diagnose=False,
    level="INFO",
    encoding="utf-8",
)
logger.add(
    "hikari-core-logs/warning.log",
    rotation="00:00",
    retention="1 week",
    diagnose=False,
    level="WARNING",
    encoding="utf-8",
)
