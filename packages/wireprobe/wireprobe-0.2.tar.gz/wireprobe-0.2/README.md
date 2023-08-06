# wireprobe
A Wireguard Probe

## Installation

### Pypi

```shell
$ python3 -m pip install wireprobe
```

and upgrading

```shell
$ python3 -m pip install wireprobe -U
```

### Debian

```shell
$ sudo apt install python3-urllib3 python3-requests python3-decorator python3-fabric python3-invoke python3-pyyaml-env-tag
```

### Python pip
```shell
python3 -m pip install -r requiremments
```

## Usage

```shell
$ mv wireprobe/settings.yml.example wireprobe/settings.yml
```

Set your configrations in `app/settings.yml`

```shell
$ cd wireprobe
$ fab run
```

For INFO logs

```shell
$ cd wireprobe
$ fab run -l 20
```

You can also set a different path for settings.yml

```shell
$ cd wireprobe
$ fab run -s /path/to/settings.yml
```

## Help

```shell
$ fab --help run
```