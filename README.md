[![](http://jenkins.tribler.org/job/pers/job/test_ipv8_qstokkink/badge/icon)](https://jenkins.tribler.org/job/pers/job/test_ipv8_qstokkink/)

This Python 2 package contains IPv8: an amalgamation of peer-to-peer communication functionality from [Dispersy](https://github.com/Tribler/dispersy) and [Tribler](https://github.com/Tribler/tribler), developed over the last 13 years by students and employees of the Delft University of Technology.
The IPv8 library allows you to interface with the existing Dispersy network to build your own applications.

Functionality included by IPv8 at this point is:
 - *Cryptographically signed messaging*
 - *Tor-like anonymous messaging*
 - *Public service discovery*
 - *Hidden service discovery*
 - *TrustChain self-sovereign blockchain* 
 - *Peer discovery using random walks and (sybil resistant) edge walks*
 - *Peer keep-alive mechanisms*
 
Implementations on the horizon of this library are *stream-based messaging* (instead of packet-based), *scalable TrustChain concensus*, *hidden attribute attestation* and *mixnet functionality*.

### Dependencies
The dependencies for IPv8 are collected in the `requirements.txt` file and can be installed using `pip`:

```
pip install -r requirements.txt
```

The libsodium library will have to be installed manually.
Please follow the instructions for your platform below:

**Debian/Ubuntu**
``sudo apt-get install libsodium18``

**Mac**
``sudo port -N install libsodium`` or ``brew install libsodium``

**Windows**
Download [an MSVC binary release from the libsodium website](https://download.libsodium.org/libsodium/releases/).
Open the archive and browse to the version applicable to your OS (x32 or x64).
Extract the files in the `dynamic` folder to a location on your `PATH` (the folder containing `python.exe` for example).

### Tests
The test suite can run without any external packages, but the `nosetests` package is recommended.
The test suite will automatically detect your back-end when running the tests.
Running tests can be done (**on UNIX**) by running:

```
bash run_all_tests_unix.sh
```

Running code coverage requires the `coverage` package (`pip install coverage`).
A coverage report can be generated by running:

```
python2 create_test_coverage_report.py
```

### Getting started
An example file to load IPv8 has been provided [here](ipv8/ipv8.py).
This file will load the bare minimum IPv8 stack for *signed messaging*, *anonymous messaging*, *public service discovery*, *peer discovery* and *peer keep-alive*.
You can play around with it to get to know IPv8 better.
