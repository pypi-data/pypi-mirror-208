<!-- GitLab Badges -->


StronglyTypedProperty
=====================

Sometimes we need to enforce that a property meets certain type and/or value restrictions
because the consumers of that property have made assumptions regarding the data that is
stored.

The permissiveness of Python to allow anything to be assigned to a property gives us
tremendous flexibility but it can also complicate debugging when things go wrong,
especially when the wrong data is written into a property. When this happens we will
either have an application that runs to completion without failing but gives an incorrect
result or we may get an exception thrown at a point-of-use. Either one of these cases can
be time consuming to debug depending on the complexity of the application as we need to
find *where*, *why*, and *when* the bad data was written to the variable.

While it can be costly to do this checking at each assignment, there are times
when we really wish to lock down a property and restrict what can be assigned
to it so that any errors will manifest at assignment rather than a use point.
In applications that we need to identify exactly where things go wrong quickly
(i.e., fail-fast systems) the value of this may well outweigh the hit on
performance that we take.

*StronglyTypedProperty* provides a [Data Class][1] like interface with an additional
ability to perform strong type checking as well as value checking on the property
created.
Type checking operations are performed when values are assigned to the property.
The following capabilities are provided:

* Restrict assigned data to a list of allowable types.
* Specify the internal sotrage type of the property.
* Set default values (for read before write situations).
* Provide optional *value* checking on assignment in addition to type checking.

Documentation and User Guide
============================
See the [User Guide][4] for detailed documentation on the package. This includes
the API docs, user guide, and examples.

History
=======
*StronglyTypedProperty* is pulled from [*ConfigParserEnhanced*][3] into its own module
because it is an interesting and useful class. Splitting these up was the intent from
the beginning when it was originally developed.

Updates
=======
See [CHANGELOG][2] for information on changes.


[1]: https://docs.python.org/3/library/dataclasses.html
[2]: https://gitlab.com/semantik-software/code/python/StronglyTypedProperty/-/blob/main/CHANGELOG.md
[3]: https://github.com/sandialabs/ConfigParserEnhanced
[4]: https://semantik-software.gitlab.io/code/python/StronglyTypedProperty/

