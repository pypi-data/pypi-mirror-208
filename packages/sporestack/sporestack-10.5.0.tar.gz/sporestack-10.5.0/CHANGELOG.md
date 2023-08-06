# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Deprecated features that will be removed in the next major version.

- `burn_rate` from `TokenInfo` is deprecated. Use `burn_rate_cents` or `burn_rate_usd` instead.
- `--no-local` will become the default for `sporestack server list`.
- If you want the CLI features, you will have to `pip install sporestack[cli]` instead of just `pip install sporestack`.

## [Unreleased]

- Nothing yet.

## [10.5.0 - 2023-05-12]

## Changed

- Use fancy table output for `sporestack server list`.

## Added

- `sporestack token invoices` command.

## [10.4.0 - 2023-05-12]

## Changed

- `pip install sporestack[cli]` recommended if you wish to use CLI features. This will be required in version 11.
- Implement [Rich](https://github.com/Textualize/rich) for much prettier output on `token info`, `server regions`, `server flavors`, and `server operating-systems`. Other commands to follow.

## [10.3.0 - 2023-05-12]

## Added

- `regions` to `APIClient` and `Client`.
- `sporestack server regions` command.

## [10.2.0 - 2023-05-03]

## Changed

- Updated client to support new `forgotten_at` field and `deleted_by`.

## [10.1.2 - 2023-04-14]

## Fixed

- HTTP 4XX errors now raise a `SporeStackUserError` instead of `SporeStackServerError`.

## [10.1.1 - 2023-04-14]

## Added

- `burn_rate_cents` to `TokenInfo` to replace `burn_rate`.
- `burn_rate_usd` to `TokenInfo`.

## Changed

- `sporestack token info` will now show burn rate in dollar amount ($0.00) instead of cents.

## Fixed

- `sporestack server operating-systems` was updated to the new API behavior. (Unfortunately, was a breaking change.)

## [10.1.0 - 2023-04-14]

## Added

- `token_info()` to `APIClient`.
- `info()` to `Client.token`.
- `changelog()` to `APIClient`.
- `changelog()` to `Client`.
- `sporestack token info` command.

## Improved

- Improved some docstrings and help messages.

## [10.0.1 - 2023-04-13]

## Fixed

- Fixed critical issue on Python versions earlier than 3.10.

## [10.0.0 - 2023-04-12]

## Changed

- No more `retry` options in `api_client`. Use try/except for `SporeStackServerError`, instead, to retry on 500s.
- Exception messages may be improved.

## [9.1.1 - 2023-04-12]

### Changed

- Bug fix with `default_factory` issue.

## [9.1.0 - 2023-03-28]

### Added

- Token messages support.
- `deleted_at` field in Server Info respones.

### Changed

- Fixes to be compatible with API updates.

## [9.0.0 - 2023-02-08]

### Added

- `Client` added to `client`
- `/server/quote` support
- `--no-wait` option for `sporestack server launch` to not wait for an IP address to be assigned.

### Changed

- Now uses `httpx` instead of `requests`

## [8.0.0 - 2023-02-07]

### Changed

- `api_client` now exposes methods under APIClient()
- `client` added with Server and Token.
- CLI reworked some. `sporestack server info` now returns plain text info. `sporestack server json` returns info in JSON format.

## [7.3.0 - 2022-11-28]

### Fixed

- Fixed broken `sporestack server topup` after API changes.

## [7.2.1 - 2022-11-01]

### Changed

- Fixed on Python 3.7 and 3.8.

## [7.2.0 - 2022-11-01]

### Changed

- Use new format for new tokens.

## [7.1.2 - 2022-11-01]

### Changed

- Fixed launch output with recent API changes.

## [7.1.1 - 2022-09-29]

### Changed

- Fixed hostname related bug when launching a server.

## [7.1.0 - 2022-09-27]

### Added

- `sporestack server autorenew-enable/disable`

### Changed

- Show autorenew status and associated token in `sporestack server list` (not in all cases, however)

## [7.0.0 - 2022-09-07]

### Added

- `sporestack server list` now accepts `--local` or `--no-local`.
- `sporestack server operating-systems`

### Changed

- `sporestack server` subcommands take `--hostname` or `--machine-id`.
- `sporestack server flavors` output is slightly more readable.

### Removed

- `sporestack server delete` (in favor of: `sporestack server destroy`)
- `sporestack server get-attribute`

## [6.2.0 - 2022-09-07]

### Added

- Allow for new *beta* `--autorenew` feature with `sporestack server launch`.

### Changed

- No longer save server JSON to disk for new servers.

## [6.1.0 - 2022-06-14]

### Changed

- Use servers launched by token endpoint in `sporestack server list`.
- Send server hostname to SporeStack API at launch time.

## [6.0.3 - 2022-04-22]

### Changed

- Bug fixes.

## [6.0.2 - 2022-04-22]

### Changed

- Replace setuptools with flit.

## [6.0.1 - 2022-04-22]

### Changed

- Use `requests` session for improved performance, in particular for `sporestack server list`.

## [6.0.0 - 2022-04-14]

### Fixed

- Use specified API endpoint for `sporestack server list` command.

## [6.0.0a3 - 2022-04-05]

### Removed

- Get rid of deprecated TokenEnable usage.

## [6.0.0a2 - 2022-04-01]

### Added

- `--quote` / `--no-quote` to launch/topup. Prompt by default if price to draw from token is acceptable.

### Removed

- affiliate_amount

### Fixed

- Protect files in ~/.sporestack with aggressive `umask`.

## [6.0.0a1 - 2022-03-31]

Remember to backup your ~/.sporestack folder as any tokens you generate will be stored there!

### Changed

- Now token-centric. You can only use `sporestack` to launch or topup servers from a token.
- `sporestack launch/info/topup`, etc, moved to `sporestack server launch/info/topup`, etc.
- `--token` argument takes the name of the token, and not the key. Defaults to `primary`.
- `--ssh-key-file` now defaults to `~/.ssh/id_rsa.pub`.
- Import generated tokens from the key with: `sporestack token import (token reference name, default is primary) --key (the token key in hex format)`

### Added

- New token commands: `sporestack token create/list`

## [5.2.3 - 2022-03-30]

### Added

- Use `~/.sporestack/servers` instead of `~/.sporestack`. Will migrate existing servers automatically.

## [5.2.2 - 2022-02-24]

### Added

- Better `sporestack list` expired server handling.

## [5.2.1 - 2022-02-10]

### Added

- New, 32 character machine ID format. (Old, 64 hex character format still supported.)
- CHANGELOG.md in Keep a Changelog format.

## [5.2.0 - 2022-01-31]

### Added

- `sporestack rebuild` command.

## [5.1.2 - 2021-10-18]

### Added

- Send `sporestack-python/version` in Use-Agent header.
