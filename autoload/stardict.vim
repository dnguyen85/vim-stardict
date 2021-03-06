"=============================================================================
" FILE: autoload/stardict.vim
" AUTHOR: Phong V. Cao <phongvcao@phongvcao.com>
" License: MIT license {{{
" Permission is hereby granted, free of charge, to any person obtaining
" a copy of this software and associated documentation files (the
" "Software"), to deal in the Software without restriction, including
" without limitation the rights to use, copy, modify, merge, publish,
" distribute, sublicense, and/or sell copies of the Software, and to
" permit persons to whom the Software is furnished to do so, subject to
" the following conditions:
"
" The above copyright notice and this permission notice shall be included
" in all copies or substantial portions of the Software.
"
" THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
" OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
" MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
" IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
" CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
" TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
" SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
" }}}
"=============================================================================


" This is for setting up PYTHONPATH
let s:script_folder_path = escape(expand('<sfile>:p:h'), '\')
let s:stardict_buf_count = 0


function! s:SetPythonPath() abort
    if has('python3')
        python3 import sys
        python3 import vim
        execute 'python3 sys.path.insert(0, "' . s:script_folder_path . '/../python")'
    elseif has('python')
        python import sys
        python import vim
        execute 'python sys.path.insert(0, "' . s:script_folder_path . '/../python")'
    endif

    return 1
endfunction


function! stardict#StarDict(...)
    let l:expl=stardict#GetDefinition(a:000)

    if (&filetype != 'stardict')
        let l:cur_winnr = winnr()
        execute "normal! \<C-W>b"
        if (winnr() > 1)
            exe "normal! " . l:cur_winnr . "\<C-W>w"
            while 1
                if (&filetype == 'stardict')
                    break
                endif
                exe "normal! \<C-W>w"
                if (l:cur_winnr ==# winnr())
                    break
                endif
            endwhile
        endif
        if &filetype != 'stardict'
            if (g:stardict_split_horizontal ==# 1)
                silent! execute g:stardict_split_size . 'sp vim-stardict' . s:stardict_buf_count
            else
                silent! execute g:stardict_split_size . 'vsp vim-stardict' . s:stardict_buf_count
            endif
        endif
    endif

    silent exec "1,$d"
    setlocal buftype=nofile bufhidden=hide noswapfile readonly filetype=stardict
    setlocal number relativenumber nobuflisted
    silent! 1s/^/\=l:expl/
    1
endfunction


function! stardict#GetDefinition(...)
    if s:SetPythonPath() != 1
        return "Cannot set ${PATH} variable!"
    endif

    let l:argsStr = join(a:000, '\\ ')

    if has('python3')
        python3 definition = GetDefinitionInner(vim.eval('a:000'))
        let l:definition = py3eval('definition')
    elseif has('python')
        python definition = GetDefinitionInner(vim.eval('a:000'))
        let l:definition = pyeval('definition')
    endif

    return l:definition
endfunction

if has('python3')
python3 << EOF
def GetDefinitionInner(argsStr):
    import stardict

    return stardict.getDefinition(argsStr)
EOF
elseif has('python')
python << EOF
def GetDefinitionInner(argsStr):
    import stardict

    return stardict.getDefinition(argsStr)
EOF
else
    echom 'vim-stardict requires your Vim to be compiled with +python or +python3 option!'
endif
