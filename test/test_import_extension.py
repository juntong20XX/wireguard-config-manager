"""
测试插件加载功能
"""
from wg_config_manager.storage import PathMap
from wg_config_manager.load_plugin import load_plugin

model = load_plugin("{APP_DIR}", "v2ray")

model.hello()
