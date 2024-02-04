# wireguard-config-manager
My wireguard config manager. Provide GUI to generate configurations for different devices. Support Wireguard and Vless.

**<font color="red">Warning, the project is still under development and no actual functionality has been completed yet.</font>**

## Install

**TODO**

## Guide

Call `python -m wg_config_manager` to start GUI.

Then config file is at `${home}/.config/wg_config_manager/config.ini`.

## Develop an Extension

### Keywords:

| name                  | type   | usage                                                |
| --------------------- | ------ | ---------------------------------------------------- |
| `VERSION`             | `str`  | Version requirements.                                |
| `ENCRYPT_TYPE_{NAME}` | `dict` | Add an encryption method.                            |
| `VPN_TYPE_{NAME}`     |        | Add an type of VPN. See "How to add a new VPN type". |

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

  the text can be display in UI and console.

- 

### Declare a VPN Type

TODO

### Format Mapping for Plugin

| key           | usage                                         |
| ------------- | --------------------------------------------- |
| `APP_DIR`     | The path where module installation location.  |
| `CONFIG_DIR`  | The path where the configuration is located.  |
| `CONFIG_FILE` | The path to configuration file `config.ini` . |
| `DATA_FILE`   | The path to current data storage file.        |

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
```

