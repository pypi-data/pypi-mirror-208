Changelog
=========

1.4.5
-----
 - updated access and update modes management

1.4.4
-----
 - updated Colander API schemas for better OpenAPI specifications
 - added enums for workflow states

1.4.3
-----
 - updated translations

1.4.2
-----
 - updated workflow delete view

1.4.1
-----
 - updated generation evolve

1.4.0
-----
 - added multiple synchronizer configurations
 - added synchronizer access to REST API

1.3.4
-----
 - updated synchronizer call result to return enums values instead of enums, which can't be
   converted to JSON

1.3.3
-----
 - removed permission check for CORS OPTIONS request on document data

1.3.2
-----
 - added new PyAMS_security CORS validators to REST services

1.3.1
-----
 - updated CORS support in REST API
 - added support for Python 3.10

1.3.0
-----
 - added support for CORS preflight OPTIONS verb used by REST services
 - updated support for search params in URL
 - updated Gitlab-CI configuration
 - small ZMI updates

1.2.1
-----
 - added enumeration to handle synchronizer status
 - PyAMS_security interfaces refactoring

1.2.0
-----
 - added workflow label
 - added "NOT_FOUND" status to documents synchronizer if given OID doesn't match an existing
   document
 - added "NO_DATA" status to documents synchronizer if a POSError occurs when reading
   document data

1.1.0
-----
 - add index on properties to make them searchable

1.0.6
-----
 - updated document properties widget template

1.0.5
-----
 - added option to display menu to access documents container from ZMI home page

1.0.4
-----
 - added missing "context" argument to permission check

1.0.3
-----
 - added title to applications vocabulary terms

1.0.2
-----
 - updated application manager permissions

1.0.1
-----
 - updated context of permissions checks in REST and GraphQL APIs

1.0.0
-----
 - initial release
