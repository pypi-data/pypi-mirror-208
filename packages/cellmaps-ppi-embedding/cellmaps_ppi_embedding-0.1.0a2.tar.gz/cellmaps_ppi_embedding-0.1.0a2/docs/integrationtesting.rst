Integration testing
=======================

To support `integration testing <https://en.wikipedia.org/wiki/Integration_testing>`__ the unit tests in **cellmaps_network_embedding**
include a parallel set of tests reside in the existing test framework and
can be activated if ``CELLMAPS_PPI_EMBEDDING_INTEGRATION_TEST`` environment
variable is set to any value:

Example variable:

.. code-block::

    export CELLMAPS_PPI_EMBEDDING_INTEGRATION_TEST="true"
    make test
