# ipfs (interplanetary filesystem) kvs (key value store)

![](https://img.shields.io/readthedocs/ipfs-kvs?label=readthedocs)
![](https://img.shields.io/github/actions/workflow/status/nanoswap/ipfskvs/test.yml?label=tests)
![](https://img.shields.io/snyk/vulnerabilities/github/nanoswap/ipfskvs)
![](https://img.shields.io/pypi/pyversions/ipfskvs)

- [Installation](#installation)
- [Documentation](#documentation)
  * [Build docs locally](#build-docs-locally)
- [Tests](#tests)
  * [Before running tests:](#before-running-tests-)
    + [Regenerate pb2.py files](#regenerate-pb2py-files)
    + [Ipfs setup](#ipfs-setup)
    + [Run the ipfs daemon](#run-the-ipfs-daemon)
- [IPFS troubleshooting](#ipfs-troubleshooting)

## Installation

```
pip install ipfskvs
```

## Documentation

https://ipfs-kvs.readthedocs.io/

### Build docs locally
`mkdocs serve`

## Tests
To only run tests: `pytest --cov=ipfskvs --log-cli-level=debug`  
To run all checks: `nox`

### Before running tests:

#### Regenerate pb2.py files 
```
cd protobuf;
protoc --python_out=../proto --proto_path=protobuf protobuf/sample.proto
```

#### Ipfs setup
https://docs.ipfs.tech/install/  

#### Run the ipfs daemon
```
ipfs daemon --api /ip4/0.0.0.0/tcp/5001
```
Check the status of your node at:
  - http://localhost:5001/webui
  - https://webui.ipfs.io/#/status


## IPFS troubleshooting

Set the log level, send the logs to a file, and search the file for relevant messages
```
export IPFS_LOGGING=<debug|info|error>
ipfs daemon --debug 2>&1 | tee ipfs.log
cat ipfs.log | grep test_directory
```

If you find something important, you can show the first few lines around that message
```
grep -C 10 '2023-04-13T17:31:49.712-0400' ipfs.log
```

Here is an example of an error message in these logs:
```
2023-04-13T17:31:49.712-0400	DEBUG	cmds/http	http/handler.go:90	incoming API request: /files/mkdir?arg=test_directory
2023-04-13T17:31:49.712-0400	DEBUG	cmds	go-ipfs-cmds@v0.8.2/command.go:161	error occured in call, closing with error: paths must start with a leading slash
```
