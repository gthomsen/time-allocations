" Vim timealloc plugin file
" Language:   TA-Lang
" Maintainer: Polarsky

if exists('g:autoloaded_timealloc')
  finish
endif
let g:autoloaded_timealloc = 1

"===========================================================
" Functions: Formating
"===========================================================
" TimeallocSetCurrLine:
"   in: string to replace line with
function! timealloc#SetCurrLine( str )
  call setline( line( '.' ), a:str )
endfunction

function! timealloc#AppendToCurrentLine( str )
  call append( line('.'), a:str )
  normal! J
endfunction

" Remove a character matching pattern
"   in:  takes in a patter
function! s:EatChar( pat )
  let c = nr2char( getchar( 0 ) )
  return ( c =~ a:pat ) ? '' : c
endfunction

" s:PostPad:
"   in:  string
"   in:  pad length
"   in:  char to pad with
"   Note: PostPad str with pad numer of char's
function! s:PostPad( str, pad, ... )
  if a:0 > 0
    let char = a:1
  else
    let char = ' '
  endif

  return a:str . repeat( char, a:pad - len( a:str ) )
endfunction

" s:PrePad:
"   in:  string
"   in:  pad length
"   in:  char to pad with
"   Note: PrePad str with pad numer of char's
function! s:PrePad( str, pad, ... )
  if a:0 > 0
    let char = a:1
  else
    let char = ' '
  endif
  return repeat( char, a:pad - len( a:str ) ) . a:str
endfunction

"===========================================================
" Functions: Regex Matching
"===========================================================
" s:IsComment:
"   in:  string line
"   out: boolean
"   Note: Checks if string line given is a comment string
function! s:IsComment( str )
  let match = matchstr( a:str , "#.*$" )
  return !empty( match )
endfunction

" s:IsTimeStamp:
"   in:  string word
"   out: boolean
"   Note: Checks if string word given is a time stamp
function! s:IsTimeStamp( str )
  let match = matchstr( a:str , "[0-9][0-9]:[0-9][0-9]" )
  return !empty( match )
endfunction

"===========================================================
" Functions: Time String Parsing
"===========================================================
" timealloc#GetTimeRange:
"   Note: Returns a string of g:s:Granularity invervals
function! timealloc#GetTimeRange()
  let min   = strftime( "%M" )
  let n_min = min
  let hr    = strftime( "%H" )
  let n_hr  = hr
  let granu = g:TimeallocGranularity

  if ( 0 ==# granu )
    let granu = 1
  endif

  if ( granu/2 > min )
    let min = float2nr( floor( min / (granu*1.0) ) ) * granu
  else
    let min = float2nr( ceil( min / (granu*1.0) ) ) * granu
  endif
  let n_min = min

  if ( 60 ==# min )
    let min    = 0
    let n_min  = granu
    let hr    += 1
    let n_hr   = hr
  else
    let n_min += granu
    if ( 60 ==# n_min )
      n_min = 0'
      n_hr += 1
    endif
  endif

  let str_t1 = s:PrePad( hr, 2, '0' )   . ':' . s:PrePad( min, 2, '0' )
  let str_t2 = s:PrePad( n_hr, 2, '0' ) . ':' . s:PrePad( n_min, 2, '0' )

  return str_t1 . '-' . str_t2
endfunction

" s:GetTimeStampRanges:
"   in:  a line string
"   out: a string of time stamp ranges found in that line string
"   Note: returns string of all time stamp ranges in line
"   XXX: Does not remove repeated time stamp ranges
function! s:GetTimeStampRanges( str )
  let stamp_ranges = ''

  if ( !s:IsComment( a:str ) )
    let line_arr = split( a:str )
    for word in line_arr
      if ( s:IsTimeStamp( word ) )
        let stamp_ranges = stamp_ranges . word . ' '
      endif
    endfor
  endif

  return stamp_ranges
endfunction

" s:GetTimeStamps:
"   in:  a line string
"   out: a string of time stamps found in that line string
"   Note: empty string returned for comment lines
"   XXX: Does not remove repeated time stamp ranges
function! s:GetTimeStamps( str )
  let stamps = ''

  if ( !s:IsComment( a:str ) )
    let line_arr = split( a:str )
    for word in line_arr
      let word_arr = split( word, '-' )
      for sword in word_arr
        if ( s:IsTimeStamp( sword ) )
          let stamps = stamps . sword . ' '
        endif
      endfor
    endfor
  endif

  return stamps
endfunction

" s:SumOfTimeStamps:
"   in:  string of time stamps like so:
"        00:00-00:00 00:00-00:00
"   out: string of the float of total hours found in time stamps
"   Note: Adds time stamp ranges
"   XXX: Function does not check for invalid timestamps
function! s:SumOfTimeStamps( time_stamps )
  let time_stamps_arr = split( a:time_stamps )
  let hrs_sum         = 0

  for time in time_stamps_arr
    let time    = split( time, ':' )
    let hr      = time[0]*1.0 + time[1]/60.0
    let hrs_sum = abs( hr - hrs_sum )
  endfor

  let hrs_sum_inte = float2nr(hrs_sum)
  let hrs_sum_frac = float2nr( (hrs_sum - hrs_sum_inte*1.0) * 100 )

  if ( 0 ==# hrs_sum_frac )
    return hrs_sum_inte
  else
    return hrs_sum_inte . '.' . hrs_sum_frac
  endif
endfunction

" timealloc#UpdateTimeStampLine:
"   in:  gets current line at cursor
"   out: appends to end of current line at cursor total hours
"   Note: current line at cursor must not be a comment line
"         or line not containing solely timestamps
function! timealloc#UpdateTimeStampLine()
  let curr_line = getline( '.' )
  if ( s:IsComment( curr_line ) )
    echom 'timealloc:Error: Line is a comment cannot update time'
    return curr_line
  endif

  let stamps = s:GetTimeStamps( curr_line )
  if ( empty( stamps ) )
    echom 'timealloc:Error: Line contains no time stamps'
    return curr_line
  endif

  let hrs = s:SumOfTimeStamps( stamps )
  if ( empty( hrs ) )
    let hrs = '0'
  endif

  let stamp_ranges = s:GetTimeStampRanges( curr_line )
  normal! 0D
  return stamp_ranges . '(' . hrs . ' hours)'
endfunction
