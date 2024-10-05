# wireguard-config-manager
My wireguard config manager. Support Wireguard and Vless.

The main direction of traditional VPN is to be fast or easy to distribute and manage, without considering how to hide the traffic. At the same time, many schools or businesses use firewalls to block most VPN connections. But - we may just want to connect to the NAS at home through Wireguard to synchronize our school homework files. Under the premise that we are clear about what we are doing and can bear the consequences, we can try to use a proxy with obfuscation - such as Vless development by v2fly. Through this agent, you almost never need to modify the Wireguard configuration, and this project can manage the configuration more conveniently.

**<font color="red">Warning, the project is still under development and no actual functionality has been completed yet.</font>**

## Install

**TODO**

## Guide

Call `python -m wg_config_manager` to start GUI.

Then config file is at `${home}/.config/wg_config_manager/config.ini`.

### Load a plugin

Open the config file at `${home}/.config/wg_config_manager/config.ini`. If file not exist, run `python -m wg_config_manager` and close it to generate it.

In config.ini file, you can find `plugins = "v2ray"` in `[Extension]` part. Add your new plugin after that keyword, by using a comma (`,`) and using quotes around the plugin name, like `, "YOUR PLUGIN"`.

Optional, you can set the plugin path by adding a key `plugin_dir-{YOUR PLUGIN}` , and the default paths `{CONFIG_DIR}/{PLUGIN NAME}`. Note that the value of `plugin dir` should be a dictionary, app will load `{plugin_dir}/{PLUGIN NAME}.py`.

For example, you download a plugin named `plg`, and the plugin file `plg.py` is located at `~/.loacl/share/wgm/plg.py`, the path value be: `~/.loacl/share/wgm`.

```ini
[Extension]
plugin_dir-v2ray = {APP_DIR}/v2ray
plugin_dir-plg = ~/.loacl/share/wgm
plugins = "v2ray", "plg"
```

## Develop an Extension

### Overview

The extension (or plugin?) works by keywords. A `keyword` is a variable with the specified name.

There are two kinds of keywords: constant and function set. `VERSION` is a constant, so a callable object is not necessary. The other type is *function set*, a function set is a `dict` with function name  as key and function, function-parameters list as value.

Examples for different keywords here:

```python
VERSION_REQ = ">=0.0.1"
```

Example 1: a constant keyword

```python
FunctionParameter(name="fwrite", default="hello world", before_pass=str.encode)
```

Example 2: parameter declare for a function

### Keywords:

| name                  | type   | usage                                                |
| --------------------- | ------ | ---------------------------------------------------- |
| `VERSION_REQ`         | `str`  | Version requirements.                                |
| `ENCRYPT_TYPE_{NAME}` | `dict` | Add an encryption method. See "Declare an Encrypt Type" |
| `VPN_TYPE_{NAME}`     |        | Add an type of VPN. See "Declare a VPN type". |
|`BACKGROUND_SERVICE_{NAME}`|`dict`|Add a background service. See "Declare a Background Service".|
### Declare Version Requirements

Plugins use `VERSION_REQ` to set version requirement.

Use `>=`,`<=`, `!=`, or`==` before target version to describe version requirement logic, and use commas (with optional spaces) to connect other expressions.

For example, `VERSION_REQ = ">0.0.1, !=0.1.0-alpha"` means the version should lager than `0.0.1` and shouldn't be `0.1.0-alpha`.

You can use `load_plugin.check_version_format` to check the format is correct or not.

### Declare an Encrypt Type

The encrypt type is statement by `ENCRYPT_TYPE_{NAME}`. This variable should point to a list containing encryption, decryption methods and required keywords.

Here are the steps to add a new encrypt type:

1. Define the functions to encryption and decryption:

   ```python
   def xor_callback(target: bytes, xor_keyword: bytes):
       return xor_bytes(target, xor_keyword)
   ```
   
2. Declare the parameters for encryption and decryption by `load_plugin.FunctionParameter`.

   Note that the type for all the passed value is `str`. To pass another type value to function, set `befor_pass` as a function.

   ```python
   from wg_config_manager.load_plugin import FunctionParameter, AcquireValue
   
   parameters = [
       FunctionParameter(name="target",
                         default=AcquireValue("TARGET DATA"),
                         docs="path to data file",
                         user_accessible=False),
       FunctionParameter(name="xor_keyword",
                         default="password", 
                         before_pass=str.encode)]
   ```

   `AcquireValue` is the key data to get values from mapping. In this case, `TARGET DATA` means the byte to be encrypt or decrypt.

   In addition, the value of `default` will be auto format by `str.format_map`.

3. Set a variable named like `ENCRYPT_TPYE_{NAME}`. For example: `ENCRYPT_TYPE_XOR`, so app will add a new encrypt `XOR` after load it.

   ```python
   ENCRYPT_TYPE_XOR = {"encrypt": [xor_callback, parameters.copy()],
                       "decrypt": [xor_callback, parameters.copy()]}
   ```


Advantage:

- To disable the type extension by set bool key `disable`,like:

  ```python
  ENCRYPT_TYPE_XXX = {"encrypt": ...,
                      "disable": True}
  ```

  then plugin loader will skip the extension.

- To add help text or document, set key `helper`:

  ```python
  ENCRYPT_TYPE_XXX = {"encrypt": ...,
                      "helper": "<text>"}
  ```

  the text can be display in UI and console. **<font color="red">TODO</font>**

- Use `logger.Logger` to set logs.

### Declare a VPN Type

TODO

### Declare a Background Service

Background service is a good way to keep a  subprocess alive, because the object constructed from `new` will be kept by loader. Here is the steps to declare a background service.

1. Define the functions or class of the service.

   ```python
   class V2rayService:
       def __init__(self, config_path):
           self.process = Popen("v2ray", "-c", config_path)
       def down(self):
           if self.process.poll() is None:
               self.process.kill()
           self.process = None
   ```

2. Declare the parameters for the background service. Module loader will find the dictionary by name starts with `BACKGROUND_SERVICE_`, in the following example, `v2ray` is the name of service.

   ```python
   from wg_config_manager.load_plugin import FunctionParameter, ServiceSelfObject
   
   parameter_config_path = FunctionParameter(name="config_path",
                                             default="{APP_DIR}/config.json",
                                             docs="path to the v2ray configuration")
   
   BACKGROUND_SERVICE_v2ray = {"new": [V2rayService, [ServiceSelfObject, parameter_config_path]],
                               "teardown": [V2rayService.down, [ServiceSelfObject]]}
   ```

   Special parameter `self` should be declare manually by `load_plugin.ServiceNewObject`.

   There are two special key-name: `new` and `teardown`. `new` for the constructor, `teardown` for the destruction. That means, the value with key `new` will be called automatically when this service started by `load_plugin.LoadPluginModule.run_service`, then the function return value will be storage as `ServiceSelfObject`. Like the constructor function, `teardown` will be called automatically when `load_plugin.LoadPluginModule.stop_service` is called.

### Format Mapping for Plugin

| key           | usage                                         |
| ------------- | --------------------------------------------- |
| `APP_DIR`     | The path where module installation location.  |
| `CONFIG_DIR`  | The path where the configuration is located.  |
| `CONFIG_FILE` | The path to configuration file `config.ini` . |
| `DATA_FILE`   | The path to current data storage file.        |

Note: You can check (even change) the values at `wg_config_manager.storage.PathMap`.

## Document

### load_plugin(Part 1): Plugin Development Utility

#### `FunctionParameters`:

It's a class decorated by `dataclasses.dataclass`.

Parameters:

| name              | type                                    | describe                                                     |
| ----------------- | --------------------------------------- | ------------------------------------------------------------ |
| `name`            | `str`                                   | the name of the parameter                                    |
| `default`         | `Any`, default is `None`                | The default value shown and set in UI or console.            |
| `helper`          | `str`, default is empty: `""`           | The helper text in UI or console.                            |
| `before_pass`     | `Callable`, optional, default is `None` | Function for processing character values before passing in.  |
| `user_accessible` | `bool`, default is `True`               | Whether the user can modify this value through the UI or console. |

Note of `default`:

- If `default` is text, it will be mapping format by build-in `str.format_map` with `storage.PathMap` and the values in the configuration which following key name equal to plugin name and special keyword `TARGET DATA` with the bytes to encrypt or decrypt. 
- If  `default` is instance `AcquireValue`, the value of `default` will be replaced with `format_mappning[default.keyword]`. It's very useful to acquire none-text data, like `TARGET DATA`.

#### `MINIMUM_PLUGIN_VARIABLES`:

The type is `set`, which holds the parameters that must be included to implement a plugin. Used to check plugin integrity.

### load_plugin(Part 2): Utilities to load plugins

#### `LoadPluginModule`:

TODO

### version

Get the version string by `version.VERSION`.

The version is following [Semantic Versioning  2.0.0](https://semver.org/spec/v2.0.0.html).

### wireguard_core

This module provides functions for wireguard options.

A config for is like:

```ini
[pc-1]
private key=
public key =
persistent keep alive=
public key is auto generated = False
pre-shared key[pc-2] =
address = 
listen port =
post up =
post down =
MTU =
```

### logger



### command_line_interface

**TODO**

### graphic_interface

#### `Window`

*Window* Object provides tree key frames.

1. `Menu` on top, belongs to its master parameter.
2. `Frame` on left to switch action items.
3. `Frame` on right to display different action items.
