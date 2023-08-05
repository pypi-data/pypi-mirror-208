# DotStat_IO: 
A generic python package which could be integrated with other end-user applications and Gitlab runner to perform basic io with .Stat Suite. 
Its role is to mask the complexities of authentication to connect to .Stat Suite.
The user needs to provide a set of parameters and the package exposes a couple of methods which will download or upload data from/to .Stat Suite.

## This package contains two modules:
- ADFS-authentication module
- Download-upload module

## In ADFS-authentication module, four methods are available:
### 1. To initialise the module for interactive use:
```python 
interactive(client_id: str, sdmx_resource_id: str, scopes: list[str], authority_url: str, redirect_port: int)
```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite PP
* `scopes:` Scopes requested to access a protected API (a resource defined by sdmx_resource_id)
* `authority_url:` URL that identifies a token authority
* `redirect_port:` The port of the address to return to upon receiving a response from the authority

### 2. To initialise the module for non-interactive use using a secret: 
```python
nointeractive_with_secret(client_id: str, sdmx_resource_id: str, scopes: list[str], authority_url: str, client_secret: str)
```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite PP
* `scopes:` Scopes requested to access a protected API (a resource defined by sdmx_resource_id)
* `authority_url:` URL that identifies a token authority
* `client_secret:` The application secret that you created during app registration in ADFS

### 3. To initialise the module for non-interactive use using windows client authentication:
```python
nointeractive_with_adfs(client_id: str, sdmx_resource_id: str, token_url: str)
```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite PP
* `token_url:` URL of the authentication service

### 4. To get a token after initialisation: 
```python
get_token()
```

## In Download-upload module, three methods are available:
### 1. To download a file from .Stat:
```python
download_file(self, dotstat_url: str, content_format: str, file_path: Path)
```
* `dotstat_url:` URL of data to be downloaded from .Stat Suite
* `content_format:` Format of the downloaded content
* `file_path:` The full path where the file will downloaded

### 2. To download streamed content from .Stat:
```python
download_stream(self, dotstat_url: str, content_format: str)
```
* `dotstat_url:` URL of data to be downloaded from .Stat Suite
* `content_format:` Format of the downloaded content

### 3. To upload a file to .Stat:
```python
upload_file(self, transfer_url: str, file_path: Path, space: str)
```
* `transfer_url:` URL of the transfer service
* `file_path:` The full path of the SDMX-CSV file, which will be uploaded to .Stat Suite
* `space:` Data space where the file will be uploaded

## For more information about how to use this package, all test cases can be accessed from this [`link`](https://gitlab.algobank.oecd.org/sdd-legacy/dotstat_io/-/blob/main/tests/test_cases.py)
