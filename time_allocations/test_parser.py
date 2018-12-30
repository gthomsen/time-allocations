#!/usr/bin/env python

import unittest

import allocations as allocations_module
import re

class TestAllocationValidAllocations( unittest.TestCase ):
    """
    """

    VALID_DATE_STRING    = "Monday 1/1\n"
    FIRST_VA_LINE_NUMBER = 2

    def test_valid_date_month_day( self ):
        """
        Verifies the form and content of date lines.  Iterates through each
        combination of <weekday> and <month>/<date> and verifies that both
        un- and zero-padded combinations of <month>/<date> are accepted.
        """

        weekdays = ["Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday"]

        months_with_30_days = [4, 6, 9, 11]
        months_with_31_days = [1, 3, 5, 7, 8, 10, 12]

        # iterate through all the possibilities of weekday and month/date.
        for weekday in weekdays:
            # handle February since there is only one month with 28 or 29 days.
            for day_number in range( 1, 30 ):
                date_string          = "{:s} 2/{:d}\n".format( weekday, day_number )
                padded_date_1_string = "{:s} 2/{:02d}\n".format( weekday, day_number )
                padded_date_2_string = "{:s} 02/{:02d}\n".format( weekday, day_number )

                allocation = allocations_module.Allocations( date_string,
                                                             strict_parsing=True )
                allocation = allocations_module.Allocations( padded_date_1_string,
                                                             strict_parsing=True )
                allocation = allocations_module.Allocations( padded_date_2_string,
                                                             strict_parsing=True )

            # handle the months with 30 days in them.
            for month_number in months_with_30_days:
                for day_number in range( 1, 31 ):
                    date_string          = "{:s} {:d}/{:d}\n".format( weekday,
                                                                      month_number,
                                                                      day_number )
                    padded_date_1_string = "{:s} {:d}/{:02d}\n".format( weekday,
                                                                        month_number,
                                                                        day_number )
                    padded_date_2_string = "{:s} {:02d}/{:02d}\n".format( weekday,
                                                                          month_number,
                                                                          day_number )

                    allocation = allocations_module.Allocations( date_string,
                                                                 strict_parsing=True )
                    allocation = allocations_module.Allocations( padded_date_1_string,
                                                                 strict_parsing=True )
                    allocation = allocations_module.Allocations( padded_date_2_string,
                                                                 strict_parsing=True )

            # handle the months with 31 days in them.
            for month_number in months_with_31_days:
                for day_number in range( 1, 32 ):
                    date_string          = "{:s} {:d}/{:d}\n".format( weekday,
                                                                      month_number,
                                                                      day_number )
                    padded_date_1_string = "{:s} {:d}/{:02d}\n".format( weekday,
                                                                        month_number,
                                                                        day_number )
                    padded_date_2_string = "{:s} {:02d}/{:02d}\n".format( weekday,
                                                                          month_number,
                                                                          day_number )

                    allocation = allocations_module.Allocations( date_string,
                                                                 strict_parsing=True )
                    allocation = allocations_module.Allocations( padded_date_1_string,
                                                                 strict_parsing=True )
                    allocation = allocations_module.Allocations( padded_date_2_string,
                                                                 strict_parsing=True )


        # XXX: validate with year

    def test_valid_allocation_form( self ):
        """
        Verifies parsing of allocations with the forms:

          <category>: <duration>
          <category> (<subcategory>): <duration>
          <category> (<subcategory> (<subsubcategory>)): <duration>
        """

        single_category_string = "category: 0.5 hours\n"
        subcategory_string     = "category (sub-category): 1 hour\n"
        subsubcategory_string  = "category (sub-category (sub-category)): 2 hours\n"

        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + single_category_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + subcategory_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + subsubcategory_string,
                                                     strict_parsing=True )

    def test_valid_allocation_duration( self ):
        """
        Verifies allocations have valid duration.  Tests integral and fractional
        hours.
        """

        integral_duration_string     = "category: 1 hour\n"
        fractional_duration_1_string = "category: 0.5 hours\n"
        fractional_duration_2_string = "category: 0.25 hours\n"
        fractional_duration_3_string = "category: 1.5 hours\n"
        fractional_duration_4_string = "category: 1.0 hours\n"
        fractional_duration_5_string = "category: 1. hour\n"

        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + integral_duration_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + fractional_duration_1_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + fractional_duration_2_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + fractional_duration_3_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + fractional_duration_4_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + fractional_duration_5_string,
                                                     strict_parsing=True )

    def test_valid_allocation_categories( self ):
        """
        Verifies allocations can have nested sub-categories.
        """

        # number of nesting levels to test.  this should be significantly larger
        # than any sane person would use.
        nesting_depth = 20

        # walk through nesting levels and construct an allocation that has
        # nesting_level-many sub-categories.
        subcategory_prefix = "sub"
        subcategory_string = ""
        for nesting_index in range( nesting_depth ):
            test_string = "category{:s}{:s}: {:d} hour{:s}\n".format( subcategory_string,
                                                                      ")" * nesting_index,
                                                                      nesting_index + 1,
                                                                      "" if nesting_index == 0 else "s" )
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + test_string,
                                                         strict_parsing=True )

            # nest another subcategory for the next iteration.
            subcategory_string = "{:s} ({:s}category".format( subcategory_string,
                                                              subcategory_prefix )

            subcategory_prefix += "sub"

    def test_valid_allocation_multiline( self ):
        """
        Verifies that multi-line allocations are parsed properly.
        """

        example_1_string = ("category1 (subcategoryA): 1 hour\n" +
                            "category2: 3 hours\n"
                            "category1 (subcategoryA): .75 hours\n" +
                            "category2 (subcategoryB): 1.0 hour\n")

        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + example_1_string,
                                                     strict_parsing=True )

        # XXX more here

    def test_valid_allocation_ignored_lines( self ):
        """
        Verifies allocations with non-recognized lines do not trigger errors.
        """

        empty_line_string                   = "\n"
        commented_invalid_allocation_string = "# category () ( (): XYZ hours\n"
        divider_string                      = "############ divider #############\n"
        duration_notes_1_string             = "07:00-08:00\n"
        duration_notes_2_string             = "07:00-08:00 (1 hour)\n"
        duration_notes_3_string             = "09:15-19:00 20:15-23:00 (12.5 hours)\n"
        duration_notes_4_string             = "07:00-12:00 13:00-\n"

        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_line_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + commented_invalid_allocation_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + divider_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + duration_notes_1_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + duration_notes_2_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + duration_notes_3_string,
                                                     strict_parsing=True )
        allocation = allocations_module.Allocations( self.VALID_DATE_STRING + duration_notes_4_string,
                                                     strict_parsing=True )

class TestAllocationAllocationNormalizations( unittest.TestCase ):
    """
    """

    # "category : 1 hour" is equivalent to "category: 1 hour"  (and variations on subcategories)

class TestAllocationAllocationMisc( unittest.TestCase ):
    """
    """

    # XXX: back to back dates, some with empty whitespace, others on successive lines

class TestAllocationInvalidAllocations( unittest.TestCase ):
    """
    """

    VALID_DATE_STRING         = "Monday 1/1\n"
    FIRST_INVALID_LINE_NUMBER = 2

    def test_invalid_date_form( self ):
        """
        Verifies that date lines with invalid formatting are not accepted.
        Non-capitalized and abbreviated weekdays are verified as rejected, as
        well as <month>/<date> combinations that are either missing a component
        or have extraneous whitespace in them.
        """

        valid_weekdays   = ["Sunday",
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday"]
        invalid_weekdays = ["Sun", "Mon", "Tues", "Weds", "Thurs", "Fri", "Sat"]

        valid_month_day_string = "1/1\n"

        invalid_date_1_string = "Monday 1 /1\n"
        invalid_date_2_string = "Monday 1/ 1\n"
        invalid_date_3_string = "Monday /1\n"
        invalid_date_4_string = "Monday 1/\n"

        # verify that non-capitalized weekdays with a valid date are invalid.
        for weekday in valid_weekdays:
            lowercase_date_string = "{:s} {:s}\n".format( weekday.lower(),
                                                          valid_month_day_string )
            uppercase_date_string = "{:s} {:s}\n".format( weekday.upper(),
                                                          valid_month_day_string )

            # lowercase weekday.
            with self.assertRaisesRegex( ValueError,
                                         re.escape( "{:s}:1 - Invalid weekday in date ({:s})".format(
                                             allocations_module.STRING_INPUT_LABEL,
                                             weekday.lower() ) ) ):
                allocation = allocations_module.Allocations( lowercase_date_string,
                                                             strict_parsing=True )

            # uppercase weekday.
            with self.assertRaisesRegex( ValueError,
                                         re.escape( "{:s}:1 - Invalid weekday in date ({:s})".format(
                                             allocations_module.STRING_INPUT_LABEL,
                                             weekday.upper() ) ) ):
                allocation = allocations_module.Allocations( uppercase_date_string,
                                               strict_parsing=True )

        # verify that abbreviated weekdays (capitalized, lowercase, and
        # uppercase) are invalid.
        for weekday in invalid_weekdays:
            date_string           = "{:s} {:s}\n".format( weekday,
                                                          valid_month_day_string )
            lowercase_date_string = "{:s} {:s}\n".format( weekday.lower(),
                                                          valid_month_day_string )
            uppercase_date_string = "{:s} {:s}\n".format( weekday.upper(),
                                                          valid_month_day_string )

            # abbreviated weekday.
            with self.assertRaisesRegex( ValueError,
                                         re.escape( "{:s}:1 - Invalid weekday in date ({:s})".format(
                                             allocations_module.STRING_INPUT_LABEL,
                                             weekday ) ) ):
                allocation = allocations_module.Allocations( date_string,
                                                             strict_parsing=True )

            # lowercase abbreviated weekday.
            with self.assertRaisesRegex( ValueError,
                                         re.escape( "{:s}:1 - Invalid weekday in date ({:s})".format(
                                             allocations_module.STRING_INPUT_LABEL,
                                             weekday.lower() ) ) ):
                allocation = allocations_module.Allocations( lowercase_date_string,
                                                             strict_parsing=True )

            # uppercase abbreviated weekday.
            with self.assertRaisesRegex( ValueError,
                                         re.escape( "{:s}:1 - Invalid weekday in date ({:s})".format(
                                             allocations_module.STRING_INPUT_LABEL,
                                             weekday.upper() ) ) ):
                allocation = allocations_module.Allocations( uppercase_date_string,
                                                             strict_parsing=True )

        # verify invalid <month>/<date> forms aren't accepted.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:1 - Date is not well formed".format(
                                         allocations_module.STRING_INPUT_LABEL ) ) ):
            allocation = allocations_module.Allocations( invalid_date_1_string,
                                                         strict_parsing=True )
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:1 - Date is not well formed".format(
                                         allocations_module.STRING_INPUT_LABEL ) ) ):
            allocation = allocations_module.Allocations( invalid_date_2_string,
                                                         strict_parsing=True )
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:1 - Date is not well formed".format(
                                         allocations_module.STRING_INPUT_LABEL ) ) ):
            allocation = allocations_module.Allocations( invalid_date_3_string,
                                                         strict_parsing=True )
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:1 - Date is not well formed".format(
                                         allocations_module.STRING_INPUT_LABEL ) ) ):
            allocation = allocations_module.Allocations( invalid_date_4_string,
                                                         strict_parsing=True )


    def test_invalid_date_month_day( self ):
        """
        Verifies that date lines do not accept invalid <month>/<day>
        combinations.
        """

        # segment our months by the number of days.  February is handled
        # separately below.
        months_with_30_days = [4, 6, 9, 11]
        months_with_31_days = [1, 3, 5, 7, 8, 10, 12]

        # range of invalid months and days to test.  invalid months are tested
        # with all combinations of their valid days and valid months are tested
        # with invalid days tailored to the month in question.
        invalid_standard_months = [0] + list( range( 13, 100 ) )
        invalid_standard_days   = [0] + list( range( 32, 100 ) )

        valid_standard_days     = range( 1, 32 )
        valid_months            = range( 1, 13 )

        # verify we don't accept invalid months (0, 12+) with all of the valid
        # "standard" days (1-31).
        for month_number in invalid_standard_months:
            for day_number in valid_standard_days:
                date_string = "Monday {:d}/{:d}".format( month_number,
                                                         day_number )

                with self.assertRaisesRegex( ValueError,
                                             re.escape( "{:s}:1 - Month is invalid ({:d})".format(
                                                 allocations_module.STRING_INPUT_LABEL,
                                                 month_number ) ) ):
                    allocation = allocations_module.Allocations( date_string,
                                                                 strict_parsing=True )

        # verify we don't accept invalid days (0, 31ish+) for valid months
        # (1-12), handling each month's duration properly.
        for month_number in valid_months:
            if month_number in months_with_30_days:
                invalid_days = [31] + invalid_standard_days
            elif month_number in months_with_31_days:
                invalid_days = invalid_standard_days
            elif month_number == 2:
                invalid_days = [30, 31] + invalid_standard_days

            for day_number in invalid_days:
                date_string = "Monday {:d}/{:d}".format( month_number,
                                                         day_number )
                with self.assertRaisesRegex( ValueError,
                                             re.escape( "{:s}:1 - Date is invalid ({:d}/{:d})".format(
                                                 allocations_module.STRING_INPUT_LABEL,
                                                 month_number,
                                                 day_number ) ) ):
                    allocation = allocations_module.Allocations( date_string,
                                                                 strict_parsing=True )

        # XXX: add support for years here

    def test_invalid_allocation_form( self ):
        """
        Verifies parsing fails if the allocation is not of the form:

          <categories>: <duration>
        """

        category_only_string       = "invalid:\n"
#        multiple_separators_string = "invalid: 0.5: hours\n"
        no_separator_string        = "invalid 0.5 hours\n"
        duration_only_string       = ": 0.5 hours\n"
        separator_only_string      = ":\n"

        # category only, no duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation is not well formed (\"{:s}\")".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER,
                                         category_only_string.strip() ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + category_only_string,
                                                         strict_parsing=True )

        # multiple separators.
        # with self.assertRaisesRegex( ValueError,
        #                              re.escape( "{:s}:{:d} - Allocation is not well formed (\"{:s}\")".format(
        #                                  allocations_module.STRING_INPUT_LABEL,
        #                                  self.FIRST_INVALID_LINE_NUMBER,
        #                                  multiple_separators_string.strip() ) ) ):
        #     allocation = allocations_module.Allocations( self.VALID_DATE_STRING + multiple_separators_string,
        #                                                  strict_parsing=True )

        # no separator string between category and duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation is not well formed (\"{:s}\")".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER,
                                         no_separator_string.strip() ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + no_separator_string,
                                                         strict_parsing=True )

        # duration only, no category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation is not well formed (\"{:s}\")".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER,
                                         duration_only_string.strip() ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + duration_only_string,
                                                         strict_parsing=True )

        # separator only, no duration or category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation is not well formed (\"{:s}\")".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER,
                                         separator_only_string.strip() ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + separator_only_string,
                                                         strict_parsing=True )

    def test_invalid_allocation_missing_unit( self ):
        """
        Verifies parsing fails if the allocation's duration does not have its units
        specified.
        """

        input_string = "invalid (no unit): .5\n"

        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation is missing units (\"{:s}\")".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER,
                                         input_string.strip() ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + input_string,
                                                         strict_parsing=True )

    def test_invalid_allocation_invalid_unit( self ):
        """
        Verifies parsing fails if the allocation's duration has invalid units.
        """

        h_string       = "invalid (incorrect units): 1 h"
        hr_string      = "invalid (incorrect units): 2 hr"
        hrs_string     = "invalid (incorrect units): 2 hrs"
        seconds_string = "invalid (incorrect units): 3600 seconds"

        # "h" or "H" instead of hours.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"h\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + h_string,
                                                         strict_parsing=True )
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"H\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + h_string.upper(),
                                                         strict_parsing=True )

        # "hr" or "HR" instead of hours.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"hr\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + hr_string,
                                                         strict_parsing=True )
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"HR\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + hr_string.upper(),
                                                         strict_parsing=True )

        # "hrs" or "HRS" instead of hours.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"hrs\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + hrs_string,
                                                         strict_parsing=True )
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"HRS\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + hrs_string.upper(),
                                                         strict_parsing=True )

        # "seconds" or "SECONDS" instead of hours.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"seconds\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + seconds_string,
                                                         strict_parsing=True )
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has wrong units - expected \"hours\" but received \"SECONDS\"".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + seconds_string.upper(),
                                                         strict_parsing=True )

    def test_invalid_allocation_invalid_duration( self ):
        """
        Verifies parsing fails if the allocation's duration is invalid.
        """

        negative_integer_string = "invalid (negative duration): -1 hours"
        negative_float_string   = "invalid (negative duration): -1.0 hours"

        zero_integer_string     = "invalid (zero duration): 0 hours"
        zero_float_1_string     = "invalid (zero duration): 0.0 hours"
        zero_float_2_string     = "invalid (zero duration): 0.00000 hours"
        zero_float_3_string     = "invalid (zero duration): .0 hours"
        zero_float_4_string     = "invalid (zero duration): -.0 hours"

        invalid_time_1_string   = "invalid (zero duration): 1e0 hours"
        invalid_time_2_string   = "invalid (zero duration): 1a2b3c hours"
        invalid_time_3_string   = "invalid (zero duration): XXX hours"

        # negative integer duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + negative_integer_string,
                                                         strict_parsing=True )

        # negative floating point duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + negative_float_string,
                                                         strict_parsing=True )

        # zero integer duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + zero_integer_string,
                                                         strict_parsing=True )

        # zero floating point duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + zero_float_1_string,
                                                         strict_parsing=True )

        # zero floating point duration (with extra zeros).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + zero_float_2_string,
                                                         strict_parsing=True )

        # zero floating point duration (no leading zero).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + zero_float_3_string,
                                                         strict_parsing=True )

        # zero floating point duration (no leading zero, with a negative sign).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + zero_float_4_string,
                                                         strict_parsing=True )

        # scientific notation duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + invalid_time_1_string,
                                                         strict_parsing=True )

        # hexadecimal notation duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + invalid_time_2_string,
                                                         strict_parsing=True )

        # non-numeric duration.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has invalid duration".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + invalid_time_3_string,
                                                         strict_parsing=True )

    def test_invalid_allocation_invalid_categories( self ):
        """
        Verifies parsing fails if the allocation's categories are invalid.
        """

        # empty categories.
        empty_category_1_string = ": 1 hour"
        empty_category_2_string = " : 1 hour"
        empty_category_3_string = "(empty category): 1 hour"
        empty_category_4_string = " (empty category): 1 hour"

        # empty sub-categories.
        empty_subcategory_1_string = "invalid (): 1 hour"
        empty_subcategory_2_string = "invalid ( ): 1 hour"
        empty_subcategory_3_string = "(): 1 hour"
        empty_subcategory_4_string = " (): 1 hour"

        # empty sub-sub-categories.
        empty_subsubcategory_1_string = "invalid (subcategory ()): 1 hour"
        empty_subsubcategory_2_string = "invalid (subcategory ( )): 1 hour"

        # unbalanced sub-categories.
        unbalanced_subcategory_1_string = "invalid (: 1 hour"
        unbalanced_subcategory_2_string = "invalid ): 1 hour"
        unbalanced_subcategory_3_string = "invalid )unbalanced): 1 hour"
        unbalanced_subcategory_4_string = "invalid (unbalanced (a): 1 hour"

        # sub-categories that aren't nested.
        unnested_subcategory_1_string = "invalid (correct) (unnested): 1 hour"
        unnested_subcategory_2_string = "invalid (sub-category (correct) (unnested)): 1 hour"

        # empty category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation is not well formed".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_category_1_string,
                                                         strict_parsing=True )

        # empty category, after normalization.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation is not well formed".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_category_2_string,
                                                         strict_parsing=True )

        # empty category, with sub-categories.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty category".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_category_3_string,
                                                         strict_parsing=True )

        # empty category, with sub-categories.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty category".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_category_4_string,
                                                         strict_parsing=True )

        # category with an empty sub-category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty sub-category (nesting level 1)".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_subcategory_1_string,
                                                         strict_parsing=True )

        # category with an empty sub-category (after whitespace normalization).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty sub-category (nesting level 1)".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_subcategory_2_string,
                                                         strict_parsing=True )


        # empty category with an empty sub-category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty category".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_subcategory_3_string,
                                                         strict_parsing=True )

        # empty category (after whitespace normalization) with an empty sub-category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty category".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_subcategory_4_string,
                                                         strict_parsing=True )

        # category and sub-category with an empty sub-sub-category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty sub-category (nesting level 2)".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_subsubcategory_1_string,
                                                         strict_parsing=True )

        # category and sub-category with an empty sub-sub-category (after
        # whitespace normalization).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an empty sub-category (nesting level 2)".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + empty_subsubcategory_2_string,
                                                         strict_parsing=True )


        # unbalanced sub-category parentheses (open-only).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an unmatched open parenthesis".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + unbalanced_subcategory_1_string,
                                                         strict_parsing=True )

        # unbalanced sub-category parentheses (close-only).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has a closing parenthesis without an open".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + unbalanced_subcategory_2_string,
                                                         strict_parsing=True )

        # unbalanced sub-category parentheses (typo, close when an open was
        # needed).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has a closing parenthesis without an open".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + unbalanced_subcategory_3_string,
                                                         strict_parsing=True )

        # unbalanced sub-category parentheses (missing close parenthesis for
        # sub-category after sub-sub-category).
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has an unmatched open parenthesis".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + unbalanced_subcategory_4_string,
                                                         strict_parsing=True )

        # two sub-categories for the category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has multiple sub-categories".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + unnested_subcategory_1_string,
                                                         strict_parsing=True )

        # two sub-categories for the category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has multiple sub-categories".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + unnested_subcategory_1_string,
                                                         strict_parsing=True )

        # two sub-sub-categories for the sub-category.
        with self.assertRaisesRegex( ValueError,
                                     re.escape( "{:s}:{:d} - Allocation has multiple sub-categories".format(
                                         allocations_module.STRING_INPUT_LABEL,
                                         self.FIRST_INVALID_LINE_NUMBER ) ) ):
            allocation = allocations_module.Allocations( self.VALID_DATE_STRING + unnested_subcategory_2_string,
                                                         strict_parsing=True )

if __name__ == "__main__":
    unittest.main()
