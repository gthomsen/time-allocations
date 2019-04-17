" Vim Timealloc syntax file
" Language:   TA-Lang
" Maintainer: Polarsky

if exists("b:current_syntax")
  finish
endif

" Timealloc Keywords for special emphasis
syn keyword TimeallocTodo    TODO FIXME XXX EPS 000 contained
syn keyword TimeallocFill    TODO FIXME XXX EPS 000
syn keyword TimeallocDays    Sunday Monday Tuesday Wednesday Thursday Friday Saturday
syn keyword TimeallocDays    Sun    Mon    Tues    Wed       Thurs    Fri    Sat
syn keyword TimeallocHours   HOURS Hours Hrs hours hrs

" Comments
syn match   TimeallocComment "#.*$"  display contains=TimeallocTodo,@Spell

" Numericals
syn match   TimeallocNumber  "\<\d\>"                                 display
syn match   TimeallocNumber  "\<[0-9]\d\+\>"                          display
syn match   TimeallocNumber  "\<\d\+[jJ]\>"                           display
syn match   TimeallocFloat   "\.\d\+\%([eE][+-]\=\d\+\)\=[jJ]\=\>"    display
syn match   TimeallocFloat   "\<\d\+[eE][+-]\=\d\+[jJ]\=\>"           display
syn match   TimeallocFloat   "\<\d\+\.\d*\%([eE][+-]\=\d\+\)\=[jJ]\=" display

" Identifiers
syn match   TimeallocParen   "[(|)|):]"                   display
syn match   TimeallocDate    "\s*[0-9]*[0-9]/[0-9]*[0-9]" display
syn match   TimeallocStamp   "[0-9][0-9]:[0-9][0-9]"      display

if version >= 508 || !exists("did_timealloc_syn_inits")
  if version <= 508
    let did_timealloc_syn_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif

  " link matches to native vim highlight groups
  HiLink TimeallocTodo    Todo
  HiLink TimeallocFill    Todo
  HiLink TimeallocDays    VisualNOS
  HiLink TimeallocHours   Statement
  HiLink TimeallocComment Comment
  HiLink TimeallocFloat   Float
  HiLink TimeallocNumber  Number
  HiLink TimeallocParen   Define
  HiLink TimeallocDate    VisualNOS
  HiLink TimeallocStamp   Type
endif

let b:current_syntax = "timealloc"
