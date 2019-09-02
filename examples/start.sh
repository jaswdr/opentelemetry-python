#!/bin/sh

cd "$(dirname -- "${BASH_SOURCE[0]}")"
cd ..

# Set up a Python virtual environment in order not to break laptop
virtualenv venv
source venv/bin/activate

pip install requests
pip install lightstep

# Install API
echo '##########'
cd opentelemetry-api
python setup.py install
cd ..

# Install SDK
echo '##########'
cd opentelemetry-sdk
python setup.py install
cd ..

# Install bridge
echo '##########'
cd bridge/opentracing
python setup.py build
python setup.py install
cd ../..

echo '##########'

#python3 examples/hello.py
python3 examples/ot-example.py
