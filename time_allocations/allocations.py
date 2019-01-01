from __future__ import print_function

import re
import sys

STRING_INPUT_LABEL = "(string)"

class AllocationsConfig( object ):
    """
    """

    def __init__( self, default_year=None, strict_parsing=False, validate_dates=True ):
        """
        """

        self._default_year   = default_year
        self._strict_parsing = strict_parsing
        self._validate_dates = validate_dates

    def defaults():
        """
        """

        return AllocationsConfig()

    def get( self, key ):
        """
        """

        if key == "default_year":
            return self._default_year
        elif key == "strict_parsing":
            return self._strict_parsing
        elif key == "validate_dates":
            return self._validate_dates
        else:
            return KeyError( "Unknown key ({:s})".format( key ) )

    def from_file( file_name ):
        """
        """

    def to_file( self, file_file ):
        """
        """

class Allocations( object ):
    """
    """

    

    # patterns for date-like and allocation-like lines.  used to determine
    # whether the parser should complain about a line that it didn't parse or
    # not.
    #
    # potential dates roughly match "<weekday> <digit>/<digit>" with deletions
    # of each sub-component.  potential allocations *roughly* match
    # "<category>:.*<unit>" while trying taking into account the myriad of ways
    # cut and paste could result in an allocation that should be flagged while
    # ignoring commonly used divider/comment/formatting lines.
    # XXX: handle just <month>/<date>
    potential_date_pattern       = re.compile( r"^("
                                               r"(\w+\s+)?\d+\s*/\s*\d+" + r"|" # optional weekday, with month/date (possibly whitespace padded)
                                               r"\w+\s+(\d+/\s*|\s*/\d+)"       # weekday with month or date, but not both (possibly whitespace padded)
                                               r")$" )
    # XXX: describe these one per line
    potential_allocation_pattern = re.compile( r"^(" +
                                               r"[^:]*:\s*([^:]*((hour|hr)s?)?)?" + r"|" # category/subcategories with duration (possibly invalid) and units
                                               r".*\d+(\.\d*)? (hour|hr)s?"       +      # anything with a duration and units at the end
                                               r")$",
                                               flags=re.IGNORECASE )

    # accept integral and fractional, positive durations.
    valid_duration_pattern   = re.compile( r"^((0?\.0*)?[1-9]\d*|[1-9]+\.\d*)$" )

    def __init__( self, file_like, configuration=None ):
        # XXX: factor this out into a parse routine so additional fragments can
        #      be consumed by the object.
        """
          strict_parsing - Optional flag specifying whether parsing should fail if an invalid
                           line is encountered.  If True, invalid lines cause parsing to fail
                           with an ValueError exception.  Otherwise, invalid lines cause a warning to
                           be logged to standard error and the internal error count incremented.
                           If omitted, defaults to False.

          validate_dates - Optional
          default_year   - Optional
        """

        if configuration is None:
            configuration = AllocationsConfig.defaults()

        self._configuration = configuration

        # XXX
        self._current_year = configuration.get( "default_year" )

        # determines how improperly formatted lines are handled.  exceptions are
        # raised when strictness is requested, warnings on standard error
        # otherwise.
        self._strict_parsing = configuration.get( "strict_parsing" )

        # we start at zero errors during parsing.
        self._number_errors = 0

        if file_like is not None:
            self.parse( file_like )

        # we don't care about the status returned.  either we threw an exception
        # and didn't fully construct an object, or we've complained and the
        # caller can check a non-zero number of errors that have accumulated.

    def _raise_parse_error( self, source_string, line_number, error_string, parsed_line ):
        """
        Raises or logs a parse error depending on whether strict parsing was requested.
        If strict parsing was requested, a ValueError is raised, otherwise the error is
        logged to standard error.  In either case the error message is of the form:

          <allocations source>:<line number> <error message> (<parsed line>)

        Takes 5 arguments:

          self          - Allocations object that encountered an error.
          source_string - String specifying the source of the error encountered.
          line_number   - Line number of source_string where the parse error occurred.
          error_string  - Error message describing the parse error.
          parsed_line   - Input line that generated the parse error.

        Returns nothing.

        """

        formatted_error = "{:s}:{:d} - {:s} (\"{:s}\")".format(
            source_string,
            line_number,
            error_string,
            parsed_line )

        # raise or print depending on how retentive we've been configured.
        if self._strict_parsing is True:
            raise ValueError( formatted_error )
        else:
            print( formatted_error, file=sys.stderr )

    def _is_valid_date( date_string, year=None ):
        """
        Validates a date string is well formed, optionally verifying that it is a real
        date.  The supplied date string must be of the form:

          <weekday> <month>/<date>

        Where <weekday> must be one of "Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", or "Saturday".  Note that <weekday> must be capitalized.

        If the caller wants to verify the date string is valid, then <date> must
        be a valid date for <month> for the supplied year and <weekday> must
        be correct for the supplied <month>/<date> combination.  Otherwise <date>
        must be a valid date for <month> in a leap year and it does not matter if
        <weekday> agrees.

        Takes 2 arguments:

          date_string - String containing a weekday, month, and date to validate for
                        well formedness.
          year        - Optional integer specifying the year to use when validating
                        date_string.  If omitted, defaults to None and date_string
                        is not verified to be consistent with a particular year.

        Returns 2 values:

          status        - Boolean specifying whether date_string is valid or not.
          error_message - A message indicating why date_string is invalid when status
                          is False.  Empty otherwise.

        """

        weekdays = ["Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday"]

        # break the date into weekday and numeric month and day so we can
        # validate each.
        #
        # NOTE: this implicitly ignores repeated whitespace between the weekday
        #       and month/day string.
        #
        try:
            weekday, month_date_string = date_string.split()
        except ValueError:
            return (False, "Date is not well formed")

        # make sure the weekday is known.
        if weekday not in weekdays:
            return (False, "Invalid weekday in date ({:s})".format( weekday ))

        # ensure we have a numeric month and date.
        try:
            month, date = list( map( int, month_date_string.split( "/" ) ) )
        except ValueError:
            return (False,
                    "Date is not well formed".format( date_string ))

        # validate the month/date is valid without knowing the year.
        # we assume that leap dates are okay here.
        if month in [1, 3, 5, 7, 8, 10, 12]:
            if not (1 <= date <= 31):
                return (False, "Date is invalid ({:d}/{:d})".format( month, date ))
        elif month in [4, 6, 9, 11]:
            if not (1 <= date <= 30):
                return (False, "Date is invalid ({:d}/{:d})".format( month, date ))
        elif month == 2:
            if not (1 <= date <= 29):
                return (False, "Date is invalid ({:d}/{:d})".format( month, date ))
        else:
            return (False, "Month is invalid ({:d})".format( month ))

        # verify the weekday matches the date provided for the given year.
        if year is not None:
            return (False, "XXX")

        return (True, "")

    def _looks_like_date( date_string ):
        """
        """

        return Allocations.potential_date_pattern.match( date_string )

    def _is_valid_allocation( allocation_string ):
        """
        Validates an allocation string is well formed.  The supplied allocation must be
        of the form:

          <category>[ (<sub-category>[ (...)])]: <duration> hours

        Where <category> is a free-form string that doesn't contain parentheses.
        <sub-category>'s are optional and may be nested arbitrarily.  <duration>
        is a positive integer or floating point value.

        Takes 1 argument:

          allocation_string - String containing an allocation to validate for
                              well formedness.

        Returns 2 values:

          status        - Boolean specifying whether allocation_string is valid or not.
          error_message - A message indicating why allocation_string is invalid when status
                          is False.  Empty otherwise.

        """

        try:
            # break the allocation at the colon and verify we have a category
            # and a duration.  trim leading and trailing whitespace from each
            # component so we normalize category names.
            #
            # NOTE: we filter out empty strings since a non-default separator
            #       does not automatically do that for us.
            #
            categories_string, duration_string = list( map( lambda x: x.strip(),
                                                            filter( lambda x: len( x ) > 0,
                                                                    allocation_string.split( ":" ) ) ) )

        except ValueError:
            return (False, "Allocation is not well formed")

        try:
            time_string, units_string = duration_string.split()
        except ValueError:
            return (False, "Allocation is missing units")

        # we currently only support time in hours.
        if units_string.lower() not in ["hour", "hours"]:
            return (False, "Allocation has wrong units - expected \"hours\" but received \"{:s}\"".format(
                units_string ))

        # verify we got a positive time.
        if not Allocations.valid_duration_pattern.match( time_string ):
            return (False, "Allocation has invalid duration")

        # our regular expression should pull a subset of floating point values
        # that we're willing to accept.  make sure it hasn't accidentally
        # admitted something that isn't a valid floating point.
        try:
            float( time_string )
        except ValueError:
            return (False, "Allocation has invalid duration")

        # catch an empty category without sub-categories.
        if len( categories_string ) == 0:
            return (False, "Allocation has an empty category")

        # our duration is sensible, now verify that we've only got nested
        # sub-categories.  verify our parentheses are balanced and follow
        # a monotonic increase in opens and then monotonically increase in
        # closes (aka decreases in opens).
        parentheses_count = 0
        maximum_count     = 0
        for character in categories_string:
            if character == "(":
                # an open parenthesis after we've closed at least one pair
                # means that this isn't a nested sub-category, but rather
                # a second sub-category at a particular nesting level.
                if maximum_count > parentheses_count:
                    return (False, "Allocation has multiple sub-categories")

                parentheses_count += 1
                maximum_count     += 1

            elif character == ")":
                parentheses_count -= 1

                if parentheses_count < 0:
                    if maximum_count == 0:
                        return (False, "Allocation has a closing parenthesis without an open")
                    else:
                        return (False, "Allocation has too many closing parentheses")

        # do we have an open parenthesis that was not closed along the way?
        if parentheses_count != 0:
            return (False, "Allocation has an unmatched open parenthesis")

        # do we have well-formed sub-categories and an empty category?
        if maximum_count > 0 and categories_string.find( "(" ) == 0:
            return (False, "Allocation has an empty category")

        # if there were no sub-categories, we're good.
        if maximum_count == 0:
            return (True, "")

        # check that all of the sub-categories are non-empty.  iterate through
        # the first N - 1 nested sub-categories and examine the distance between
        # open parentheses.  then look at the last sub-category and examine
        # the distance between the open and close.  if any of those are adjacent
        # to each other (after ignoring whitespace), then we have an empty
        # sub-category.
        open_index       = categories_string.find( "(" )
        target_character = "("
        for nesting_index in range( maximum_count ):

            # our last iteration looks for a closing parenthesis.
            if nesting_index == (maximum_count - 1):
                target_character = ")"

            # compute the number of characters from this open parenthesis to
            # its successor.  note that we avoid computing the offset as that
            # introduces too many "+ 1"s in the indexing below.
            close_distance = categories_string[open_index+1:].find( target_character ) + 1
            close_index    = open_index + close_distance

            if( close_distance == 1 or
                categories_string[open_index+1:close_index].isspace()):
                return (False, "Allocation has an empty sub-category (nesting level {:d})".format( nesting_index + 1 ) )

            open_index += close_distance

        # all of the sub-categories are non-empty.
        return (True, "")

    def _looks_like_allocation( allocation_string ):
        """
        """

        return Allocations.potential_allocation_pattern.match( allocation_string )

    def _record_allocation( self, date_string, allocation_string ):
        """
        """

        if date_string is None:
            # XXX: we don't know where to record this particular allocation.
            raise ValueError( "" )

        pass

    def clear( self ):
        """
        Clears existing allocations.  All known categories and their allocations are
        wiped out so that the allocations from the next call to parse() are the only
        allocations available.

        Takes no arguments.

        Returns nothing.

        """

        pass

    def get_configuration( self ):
        """
        """

        return self._configuration

    def number_errors( self ):
        """
        """

        return self._number_errors

    def parse( self, file_like, current_year=None, current_configuration=None ):
        """
        Parses a block of allocations and merges them into the existing allocations.
        XXX: raises ValueError or complains depending upon the configuration.

        Takes 3 arguments:

          file_like             -
          current_year          - XXX: Parse with a temporary year.
          current_configuration - XXX: Parse with a temporary configuration.

        Returns 1 value:

          status -

        """

        if current_configuration is None:
            current_configuration = self._configuration

        # XXX: handle the current date being optional
        if current_year is None:
            current_year = self._current_year

        # XXX: shouldn't be part of the instance
        allocations_source  = "(string)"
        current_line_number = 0

        # note the previous number of errors
        previous_error_count = self.number_errors()

        # read in all of the lines if we're working with a file-like object.  we
        # assume this will never be used on truly large data (100's of thousands
        # of lines) so we simply buffer the data and move on.
        if not isinstance( file_like, str ):

            # figure out where these allocations come from.
            try:
                allocations_source = file_like.name
            except:
                allocations_source = "(unknown)"

            allocations_string = ""

            while( file_like ):
                allocations_string += file_like.readline()

            file_like = allocations_string

        # walk through line-by-line and parse the allocations from cleaned up
        # lines.
        for current_line in file_like.split( "\n" ):

            current_line_number += 1

            # strip out empty comments.
            comment_start_index = current_line.find( "#" )
            if comment_start_index > -1:
                current_line = current_line[:comment_start_index]

            # remove leading/trailing whitespace.
            current_line = current_line.strip()

            # ignore empty lines.
            if len( current_line ) == 0:
                continue

            # are we looking at the start of a new day?
            date_status, date_error = Allocations._is_valid_date( current_line,
                                                                  current_year )

            if date_status is True:
                weekday, current_date = current_line.split()
                continue

            allocation_status, allocation_error = Allocations._is_valid_allocation( current_line )

            if allocation_status is True:
                try:
                    self._record_allocation( current_date, current_line )
                except ValueError as e:
                    # XXX: failed to record (likely no date)
                    self._number_errors +=1

                    self._raise_parse_error( allocations_source,
                                             current_line_number,
                                             str( e ),
                                             current_line )
                continue

            # neither the date nor the allocation are valid, so we need to
            # determine if we silently ignore this line because it isn't
            # something we would be expected to parse or if we need to complain
            # and increment our error count.
            if (date_status is not True) and Allocations._looks_like_date( current_line ):
                self._raise_parse_error( allocations_source,
                                         current_line_number,
                                         date_error,
                                         current_line )
            elif (allocation_status is not True) and Allocations._looks_like_allocation( current_line ):
                self._raise_parse_error( allocations_source,
                                         current_line_number,
                                         allocation_error,
                                         current_line )

            # this line didn't look like either a date or an allocation so we
            # assume it wasn't something we should parse.  move on to the next
            # line.
            pass

        # parsing is successful if we didn't have any errors.
        return (self.number_errors() == previous_error_count)

    def set_configuration( self, new_configuration ):
        """
        """

        self._configuration = new_configuration

    def to_df( self, filters=None, filter_type=None, depth_limit=0 ):
        """
        Converts allocations to a Pandas DataFrame.  A subset of allocations can be filtered
        in or out based on regular expression or an explicit list, or allocations can be
        flattened so that a maximum depth is not exceeded.

        Takes 3 arguments:

          filters     -
          filter_type -
          depth_limit -

        Returns 1 value:

          df -

        """

        return None
