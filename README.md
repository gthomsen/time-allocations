# Overview

Python module to parse and analyze time allocations recorded in a (mostly
free-form) text-based file format.  This provides basic functionality for
reporting time spent on projects while exporting to Pandas DataFrames to
allow more in depth analysis of trends.

The format was borne out of necessity when working on aging RHEL 5 systems that
could not be updated with external software.  Its simplicity and minimal
overhead resulted in more than a decade's worth of allocations to be recorded
across a variety of projects.  This implementation in Python replaced the
original Perl-based implementation that has been since long lost.
