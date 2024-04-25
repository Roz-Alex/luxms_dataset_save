# luxms_dataset_save

Использование

```commandline

usage: ds_save.py [-h] [-m [{save,restore}]] [-u [USER]] [-H [HOST]] [-p [PORT]] [-P [PATH]] [ds_name]

Luxms BI Dataset saver. Saves specified dataset with all info from specified stand

positional arguments:
  ds_name               name of dataset to dump. Is required

optional arguments:
  -h, --help            show this help message and exit
  -m [{save,restore}], --mode [{save,restore}]
                        optional argument that sets basic program usage. Can be save (default) or restore If save - program makes a dump of specified dataset with
                        additional meta info If restore - program restores dataset from dump
  -u [USER], --user [USER]
                        optional argument that specifies username for ssh connection. is required if host and port are used
  -H [HOST], --host [HOST]
                        optional argument that specifies host for ssh connection. is required if user or port are used
  -p [PORT], --port [PORT]
                        optional argument that specifies port for ssh connection. is required if user or host are used
  -P [PATH], --path [PATH]
                        optional argument that specifies local path where files will be saved is required if user or host are used

Developed by Alex_R

```

Пока это все описание.

Тудушки стоят прямо в коде