" Vim timealloc plugin file
" Language:   TA-Lang
" Maintainer: Polarsky

if exists('g:loaded_timealloc')
  finish
endif
let g:loaded_timealloc = 1

"===========================================================
" Global(s)
"===========================================================
" Global for time granularity
let g:TimeallocGranularity = 15

"===========================================================
" Functions: Drawing
"===========================================================
" Print functions:
"   Day
function! TimeallocDay()
  let str = strftime( "%A %-m/%-d" )
  call timealloc#AppendToCurrentLine( str )
endfunction

"   Time
function! TimeallocTime()
  let str = timealloc#GetTimeRange()
  call timealloc#AppendToCurrentLine( str )
endfunction

"   New (category entry)
function! TimeallocNew()
  call timealloc#AppendToCurrentLine( 'XXX (XXX (XXX)): XXX hours' )
endfunction

"   Update Hours (Update to time stamp line)
function! TimeallocUpdate()
  let str = timealloc#UpdateTimeStampLine()
  call timealloc#SetCurrLine( str )
endfunction

"===========================================================
" Commands
"===========================================================
" NOTE: User may use these to map commands to key bindings
command! TADay    call TimeallocDay()
command! TATime   call TimeallocTime()
command! TANew    call TimeallocNew()
command! TAUpdate call TimeallocUpdate()

"===========================================================
" Bindings
"===========================================================
" Timealloc filetype specific commands
augroup timealloc
  autocmd!
  autocmd Filetype timealloc nnoremap <buffer> o o<esc>0Di
augroup END
