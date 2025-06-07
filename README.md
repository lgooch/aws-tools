# aws-tools
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)

## Description
Provides a tool to delete the default VPC in a given AWS account.

## Installation
From source
```
git clone https://github.com/lgooch/aws-tools
cd aws-tools
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 setup.py install
```
You will also need the AWS CLI to be installed. More information can be found at https://aws.amazon.com/cli/

## Usage
To run the script against the default profile configured for the AWS CLI you can run
```
delete_default_vpc.py
```
To use a different profile you can use
```
delete_default_vpc.py --profile foo
```
If you would like to automatically accept the deleting of the VPC's you can run
```
delete_default_vpc.py --profile foo --auto-accept
```

## Contributing
Please feel free to raise a PR for any improvements that can be made.

## License
MIT: see LICENSE
