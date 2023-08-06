# Bing Wallpaper download script

Downloads the nice daily wallpaper from Bing and prints the file
location on the command line (e.g., to pass to `feh`).

## Installing
This script is available on pypi.org. Simply use
```sh
pip install bingwallpaper
```

## Running
The script is called `bingwallpaper`; when run without options,
it will simply output the filename of the downloaded image,
which will be `~/Downloads/bingwallpaper.png` if `~/Downloads`
exists and is accessible, or `/tmp/bingwallpaper.png` else.

## Building
Simplest way is using `poetry`:

```sh
poetry build
```

This will create a `dist` dir in the root directory containing
a `.whl` and a `.tar.gz`. You can install the `.whl` by using
`pip`:

```sh
pip install dist/*.whl
```

