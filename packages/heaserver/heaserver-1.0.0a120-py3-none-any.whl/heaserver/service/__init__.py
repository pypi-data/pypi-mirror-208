"""
HEA Server Framework is a framework library for creating HEA microservices.

Types of microservices

The registry microservice manages a listing of all microservices that the
current instance of HEA knows about.

Trash microservices serve items that have been marked for permanent deletion but
have not been permanently deleted yet. The registry service may have at most
one trash microservice registered for a given desktop object type, file system
type, and file system name combination. Desktop object types with no registered
trash microservice are assumed not to have a trash and are deleted permanently.

"""
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
