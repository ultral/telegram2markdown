# telegram2markdown
exports telegram posts as markdown files


## Prepare virtualenv

There are some dependencies for python for running ansible. We install those dependencies into [virtualenv](https://virtualenv.pypa.io/en/latest/).

```shell
[[ -d .venv ]] &&  rm -rf .venv
python3 -m venv .venv --system-site-packages
. .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```
