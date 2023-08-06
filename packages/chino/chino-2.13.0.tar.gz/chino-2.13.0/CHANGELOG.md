# Changelog

Note: remember to update version in README.md.

## [2.13.0] 2023-05-15
- Added support for blocked user API

## [2.12.0] 2022-06-13
- Added support for the /users/bulk_get endpoint

## [2.11.0] 2022-05-23
- Added support for the /documents/bulk_get endpoint 

## [2.10.0] 2022-03-31
- Added support for check_reuse flag on users update and partial_update 
- Added support for endpoint which adds all users in schema to group

## [2.9.0] 2021-11-22
- Added support for urlparam uid_type in token introspection call

## [2.8.0] 2021-07-21
- Added support for OAuth token introspection

## [2.7.0] 2021-05-24
- Added support for Dump UserSchema

## [2.6.1] 2021-05-17
- Fix the return message in case JSON is not in the correct format (e.g. Server problem)

## [2.6.0] 2021-05-12
- Added support for document list metadata filtering and ordering

## [2.5.1] 2021-04-21
- Fixed dump schema test to reflect the latest server bug fixes.

## [2.5.0] 2021-04-09
- Added support for datatype conversion and dump schema

## [2.4.0] 2021-03-18
- Deprecated old Search API in favor of the new one. Added ad hoc methods to
  search over docs and users
- Deprecated old Consent Management API in favor of the new 
  [Consenta API](https://docs.chino.io/consent/consentame/docs/v1).

## [2.3.0] 2020-10-26 
- Added support for the 'default' attribute in Schema and UserSchema fields
  definition

## [2.2.0] 2020-09-24 
- Added url/token for blob

## [2.1.0] 2020-09-04
- Added support for Documents PATCH (partial update)
- Repositories LIST: added support for search filter 'descr' (URL query param)
- Schemas LIST: added support for search filter 'descr' (URL query param)
- UserSchemas LIST: added support for search filter 'descr' (URL query param)
- Groups LIST: added support for search filter 'name' (URL query param)
- Collections LIST: added support for filtering by 'document_id' (list only the
  collections which keeps that document)
