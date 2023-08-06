
# Changelog
All notable changes to rattail-corepos will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.1.19] - 2023-05-17
### Changed
- Replace `setup.py` contents with `setup.cfg`.

## [0.1.18] - 2023-05-11
### Changed
- Add behavior options for CORE member importer.

## [0.1.17] - 2023-05-09
### Changed
- Add support for `member_type_id` in CORE `MemberInfoImporter`.

## [0.1.16] - 2023-05-08
### Changed
- Avoid deprecated import for `OrderedDict`.
- Move logic for CORE importing to "more precise" module path.
- Move CORE DB import handler to more general location.

## [0.1.15] - 2023-05-01
### Changed
- Show all deprecation warnings occurring within `corepos` pkg.

## [0.1.14] - 2023-02-12
### Changed
- Refactor `Query.get()` => `Session.get()` per SQLAlchemy 1.4.

## [0.1.13] - 2023-01-03
### Changed
- Define default handler for `corepos_member` batch type.

## [0.1.12] - 2023-01-02
### Changed
- Configure DB connections for CORE trans archive on app startup.
- Fix datasync bug for CORE API -> Rattail.
- Update usage of `short_session()` per upstream changes.

## [0.1.11] - 2022-03-15
### Changed
- Add "raw" card number value to CORE Member Import batch.

## [0.1.10] - 2022-03-01
### Changed
- Some tweaks to expose CORE <-> Rattail import handlers in web app.
- Overhaul import handler config etc.
- Refactor CORE API hack to use `custdata` instead of `Customers` table.
- Avoid error if CORE product data is missing some fields.
- Refactor some importer method calls to avoid deprecation warnings.

## [0.1.9] - 2021-11-05
### Changed
- Add support for 2nd "member type" file in CORE member batch.

## [0.1.8] - 2021-11-04
### Changed
- Add `custdata` importer for CORE Office -> Lane.
- Add batch to update CORE member records directly via SQL.

## [0.1.7] - 2021-08-31
### Changed
- Add CORE Office -> Lane op importer for Department.

## [0.1.6] - 2021-08-02
### Changed
- Add email setting for CORE Office -> CORE Lane export.

## [0.1.5] - 2021-07-21
### Changed
- Add basic support for CORE Office -> CORE Lane export.

## [0.1.4] - 2021-06-11
### Changed
- Several more updates...mostly a "save point" release.

## [0.1.3] - 2020-09-19
### Changed
- Add some common email profiles, for importer diff warnings.

## [0.1.2] - 2020-09-16
### Changed
- Fix manifest to include alembic migrations.

## [0.1.1] - 2020-09-16
### Changed
- A ton of updates, mostly a "save point" release.

## [0.1.0] - 2020-02-27
### Added
- Initial version of the package; defines some basic importer/datasync logic.
