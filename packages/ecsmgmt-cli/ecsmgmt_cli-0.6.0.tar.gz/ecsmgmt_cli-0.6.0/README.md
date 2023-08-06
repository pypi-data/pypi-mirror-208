# ecsmgmt-cli

Small CLI tool for interacting with the ECS Management API. ECS is Dell EMC's Object Storage (S3) Solution.

## usage

### config file
**Warning: It's not recommended to store your credentials in an plaintext file. If you decide nevertheless to do so, please be sure to limit the access to the config file, for example with `chmod 600 $configfilepath`.**

The config file is expected to be in the common config directories for the following platforms:
* unix: `~/.config/ecsmgmt-cli/config.yml`
* macOS: `~/Library/Application Support/ecsmgmt-cli/config.yml`
* Windows: `C:\Users\<user>\AppData\Local\ecsmgmt-cli\config.yml`

