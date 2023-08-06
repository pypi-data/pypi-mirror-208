Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Nomenclature
------------


Updates and Changes
===================

<!--
## [X.Y.Z] - < !-- YYYY-MM-DD or -- > [UNRELEASED]
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Internal
### Security
### TODO
-->


## [0.1.0] - 2023-05-13
### Added
- Initial PyPi release
- `Example-02` - demonstrates the use of a *validator*
- Parameter: `validate_on_set` -- this allows disabling of validation checks
  on set for code running in a "release" mode. This will turn off all validation
  checks AND data transformations on assignment. It undermines the whole point
  of a "strongly typed" property but can increase performance alot if a property
  is assigned a lot. I'm on the fence of whether or not I should hang onto this.
  - UPDATE: This is parked on a holding branch for now. It's not clear if giving
    a trivial way to disable strong type checking is advisable since someone using
    this class would likely use that as the default mode... in which case why
    not just use a more vanilla DataClass? It's still an open issue and I'll
    track this on Gitlab in the Issues.
- `Example-03` - Demonstrates a `TypeError` that is thrown at _definition time_
  of a property if the `validator` is not callable.
### Changed
- Changed up Example-01 to show more simple cases.
### Internal
- Moved validation of the `validator` callback function to the property
  definition stage of a `StronglyTypedProperty`. This takes the check
  out of the `@setter` because we shouldn't need to be checking that the
  validator is callable every time we write a value to the property.
- Documentation now publishes the coverage data link into the docs and this
  also gets included+linked into the gitlab pages docs.
- License boilerplate updated - AFAIK this is the proper way to show the original
  Sandia National Laboratories copyright + my own additions / takeover when I pulled
  this from `ConfigParserEnhanced`. I consulted with the Licensing and Copyright
  department folks on this issue and they instructed me that this is the way.
### TODO
- [X] Get documentation into a 'releasable' state.
- [X] PyPi integration documentation + links back to Gitlab
- [X] Fix code banner for copyright notices.


## [0.0.1] - 2022-12-05
### Added
- Initial checkin
- Example-01: `examples/StronglyTypedProperty-Example-01.py`


