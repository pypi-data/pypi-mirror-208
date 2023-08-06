# certbot-acme-dns

ACME DNS Authenticator plugin for Certbot.

This plugin automates the process of completing a `dns-01` challenge with the
help of an [acme-dns] proxy server.

## Warning

Your ACME CA must properly implement [RFC 8657], namely the `accounturi`
issuance parameter. This plugin contains a list of compliant ACME CAs
and will abort if the chosen CA is not on that list.

The RFC does not require CAs to fail validation when they don't understand an
issuance parameter, meaning that unless a particular ACME CA explicitly
documents supporting and honoring the `accounturi` issuance parameter, it
will be **silently ignored**. Typos in the parameter names are allowed to be
ignored, too (eg. `accounturl` will render your deployment insecure even when
the CA fully implements the RFC). See the [RFC complaint forum post] for
discussion.

You can force this plugin to proceed anyway using the
`--acme-dns-is-trusted=yes` option. However, this is **INSECURE** and
**DANGEROUS**, unless you self-host the [acme-dns] proxy server **and** fully
trust it. The proxy server will be able to issue certificates for the
"delegated" domain without your (certbot's) consent.

## Installation

```
pip install certbot-acme-dns
```

## Usage

To start using the plugin, pass the `--authenticator=acme-dns` (or just
`-a acme-dns` for short) option to certbot's command line.

Custom ACME DNS proxy server URL can be specified using the
`--acme-dns-url https://acme-dns.example.com` option, default is
`https://auth.acme-dns.io`.

## Development

### Run tests

```
tox
```

### Auto-fix code formatting

```
tox -e reformat
```

### Run Certbot with the certbot-acme-dns plugin

```
tox -e run -- certonly -a acme-dns -d example.com
```

Certbot logs & config (accounts, hooks, certificates, etc.) are stored under `./.certbot/`.

### Build

#### sdist

```
tox -e build
```

#### wheel

```
tox -e build -- --wheel
```

### Generate documentation

```
tox -e docs
```

[acme-dns]: https://github.com/joohoi/acme-dns
[RFC 8657]: https://tools.ietf.org/html/rfc8657
[RFC complaint forum post]: https://community.letsencrypt.org/t/boulder-ignores-rfc-8657-accounturi/123336
