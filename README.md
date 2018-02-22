# pyLyRT

### Installation

* Requirements:
  * python3
  * python3-pip

* Installing on Ubuntu 16.04

```
$ sudo apt install python3 python3-pip python3-venv
$ python3 -m venv myvenv
$ source myvenv/bin/activate
(myvenv)$
```

### Testing

```
(myvenv)$ nosetests tests/

alternatively:
(myvenv)$ nosetests tests/ --with-coverage
```

### Runtime update example

In one terminal:
```
(myenv)$ python3 main.py
```

In another terminal:
```
cp runtime_lib/new_developer.py runtime_lib/newBob.py
```
