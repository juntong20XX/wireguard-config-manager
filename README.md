# wireguard-config-manager
My wireguard config manager. Provide GUI to generate configurations for different devices. Support Wireguard and Vless.

**<font color="red">Warning, the project is still under development and no actual functionality has been completed yet.</font>**

## Install

**TODO**

## Guide

Call `python -m wg_config_manager` to start GUI.

Then config file is at `${home}/.config/wg_config_manager/config.ini`.

## About Extension

### Keywords:

| name                  | usage                                                |
| --------------------- | ---------------------------------------------------- |
| `ENCRYPT_TYPE_{NAME}` | Add an encryption method.                            |
| `VPN_TYPE_{NAME}`     | Add an type of VPN. See "How to add a new VPN type". |

### How to add a new encrypt type

The encrypt type is statement by `ENCRYPT_TYPE_*`. This variable should point to a list containing encryption, decryption methods and required keywords.

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

### How to add a new VPN type

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
