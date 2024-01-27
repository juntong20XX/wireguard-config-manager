# wireguard-config-manager
My wireguard config manager. Provide GUI to generate configurations for different devices. Support Wireguard and Vless.

**<font color="red">Warning, the project is still under development and no actual functionality has been completed yet.</font>**

## Install

**TODO**

## Guide

Call `python -m wg_config_manager` to start GUI.

Then config file is at `${home}/.config/wg_config_manager/config.ini`.

## Document

### version

Get the version string by `version.VERSION`.

The version is following [Semantic Versioning  2.0.0](https://semver.org/spec/v2.0.0.html).

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
   def xor_file(file_path: str, xor_keyword: bytes):
       with open(file_path, "rb") as fp:
   	    return xor_bytes(f.read(), xor_keyword)
   ```

2. Declare the parameters for encryption and decryption by `load_plugin.FunctionParamater`.

   Note that the type for all the passed value is `str`. To pass another type value to function, set `befor_pass` as a function.

   ```python
   from wg_config_manager.load_plugin import FunctionParamater
   
   paramaters = [
       FunctionParamaters(name="file_path",
                          default="{DATA_FILE}",
                          docs="path to data file"),
       FunctionParamaters(name="xor_keyword",
                          default="{DATA_FILE}", 
                          before_pass=str.encode)]
   ```

3. Set a variable named like `ENCRYPT_TPYE_{NAME}`. For example: `ENCRYPT_TYPE_XOR`, so app will add a new encrypt `XOR` after load it.

   ```python
   ENCRYPT_TYPE_XOR = {"encrypt": [xor_file, paramaters.copy()],
                       "decrypt": [xor_file, paramaters.copy()]}
   ```

### Declare a VPN Type

### Format Mapping for Plugin

| key           | usage                                         |
| ------------- | --------------------------------------------- |
| `APP_DIR`     | The path where module installation location.  |
| `CONFIG_DIR`  | The path where the configuration is located.  |
| `CONFIG_FILE` | The path to configuration file `config.ini` . |
| `DATA_FILE`   | The path to current data storage file.        |

## Usage

### MODEL: storage

### MODEL: load_plugin
