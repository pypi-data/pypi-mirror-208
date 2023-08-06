"""
The HEAObject project implements classes representing all the data managed by HEA microservices that are maintained by
RISR. It also provides base classes for third parties to use in creating their own microservices.

Generally speaking, there is a one-to-one correspondence between module and microservice. Each module's docstring, and
the docstrings for the classes contained within, describe any special requirements for microservices that use those
classes. For HEA microservice authors, it is important to understand those requirements so that your microservices
function properly. For example, the heaobject.folder module describes requirements for microservices that implement
management of folders.
"""
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
