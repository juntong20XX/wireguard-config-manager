"""
测试插件加载功能
"""
from wg_config_manager.storage import PathMap
from wg_config_manager.load_plugin import load_plugin_module

model = load_plugin_module("{APP_DIR}/v2ray", "v2ray")

model.hello()
