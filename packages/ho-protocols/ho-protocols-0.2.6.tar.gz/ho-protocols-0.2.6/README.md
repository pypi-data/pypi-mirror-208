# HO protocols

ProtoBuf definitions used in various HO components.

Project is structured as recommended by [Google](https://github.com/protocolbuffers/protobuf/issues/1491#issuecomment-263772124) for Python projects.


# Python 3+ components

## Installation

``` bash
pip install ho-protocols
```

## Use

``` python
import ho_protocols.example_pb2 as pb

req = pb.ExampleRequest()    
req.type = pb.ExampleRequest.Two
req.param = 42

print('Request:')
print(req)
print(req.SerializeToString())

res = pb.ExampleResponse()
res.valueA = 'Lorem'
res.valueB = 3.1415

print('\nResponse:')
print(res)
print(res.SerializeToString())
```


## Build and distribute

Generate Python source files (including mypy stub files for better code completion)
``` bash
protoc --python_out=./src --mypy_out=./src --proto_path=./src $(find ./src -name "*.proto")
```

Build distribution package

```bash
python3 -m build
```

Publish to PyPi
```bash
twine upload dist/*
```

