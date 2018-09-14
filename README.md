# DNS_Tester

## Introduction
An small script that would help testing dns servers (which ones are fasted, which ones can find the sites you cared, etc.)

This script will read input files to know the dns servers and the sites you cared. It will invoke system `ping` command to approximate the access delay between your computer and the dns servers within the dns list. Meanwhile, it will also invoke `nslookup` command to identify whether the sites you cared could be looked up from the dns servers (in other words, the tool will test whether the dns server will return you with a result of your sites, but the returning results are not guaranteed to be correct, see [DNS spoofing](https://en.wikipedia.org/wiki/DNS_spoofing))

## Usage
The script has two inputs, `dns servers` and `sites` you cared.

```shell
$ python3 dns_tester.py {dns} {sites}
```

For example,
```shell
$ python3 dns_tester.py dns.txt sites.txt
```

`dns.txt` contains dns servers. Empty lines and lines start with '#' will be ignored.
`sites.txt` contains website domains you cared. Empty lines and lines start with '#' will be ignored.
