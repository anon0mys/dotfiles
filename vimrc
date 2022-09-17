" ========================================
" Config 
" ========================================
set nocompatible "don't be Vi compatible
filetype on "enable filetype detection
filetype plugin on "filetype specific plugins
filetype indent on "filetype specific indents
set expandtab "use spaces instead of tabs
set encoding=UTF-8
set textwidth=119
set undofile " Maintain undo history between sessions
set undodir=~/dotfiles-local/undodir
set splitright

" ========================================
" Language specific config 
" ========================================
" vim-test
let test#python#runner = 'pytest'
let g:test#python#pytest#executable = './manage.py test --settings=api.config.settings.local_test -- -q -s --disable-warnings'

" ========================================
" General vim sanity improvements
" ========================================
command! Q q " Bind :Q to :q
command! W w
command! Qall qall
nnoremap Y y$

" ========================================
" Key Mappings
" ========================================
let mapleader = " "
let g:mapleader = " "

" If you visually select something and hit paste
" that thing gets yanked into your buffer. This
" generally is annoying when you're copying one item
" and repeatedly pasting it. This changes the paste
" command in visual mode so that it doesn't overwrite
" whatever is in your paste buffer.
vnoremap p "_dP

"Global copy/pasting
noremap <leader>y "*p
nnoremap <leader>y "*y
vnoremap <leader>y "*y

" Remap O and o to insert blank lines without entering insert
nnoremap O O<esc>
nnoremap o o<esc>

" Remap save and quit
nnoremap <leader>w :w<CR>
nnoremap <leader>q :qa<CR>

" navigate with arrows
nnoremap <Left> h
nnoremap <Right> l
nnoremap <Up> k
nnoremap <Down> j

" navigate splits with shift-→ , shift-←, shift-↓, shift-↑
nnoremap <S-left> <C-w>h
nnoremap <S-right> <C-w>l
nnoremap <S-up> <C-w>k
nnoremap <S-down> <C-w>j
inoremap <S-left> <C-w>h
inoremap <S-right> <C-w>l
inoremap <S-up> <C-w>k
inoremap <S-down> <C-w>j

" <leader># Surround a word with #{ruby interpolation}
let g:surround_113 = "#{\r}"   " v
let g:surround_35  = "#{\r}"   " #
map <leader># ysiw#
vmap <leader># c#{<C-R>"}<ESC>

" <leader>:symbol Surround a word with that symbol
" The difference is in whether a space is put in
map <leader>" ysiw"
vmap <leader>" c"<C-R>""<ESC>
map <leader>' ysiw'
vmap <leader>' c'<C-R>"'<ESC>
map <leader>( ysiw(
map <leader>) ysiw)
vmap <leader>( c( <C-R>" )<ESC>
vmap <leader>) c(<C-R>")<ESC>
map <leader>] ysiw]
map <leader>[ ysiw[
vmap <leader>[ c[ <C-R>" ]<ESC>
vmap <leader>] c[<C-R>"]<ESC>
map <leader>} ysiw}
map <leader>{ ysiw{
vmap <leader>} c{ <C-R>" }<ESC>
vmap <leader>{ c{<C-R>"}<ESC>

" Clear search highlighting with <esc>
nnoremap <silent> <CR> :nohlsearch<CR><CR>

" Start fuzzy finder with <space>f
map <leader>f :FZF<CR>

"toggle NERDTree w/ <leader>tr
map <leader>tr :NERDTreeToggle<CR>

" ========================================
" VIM Plug
" ========================================

call plug#begin('~/.vim/plugged')

" Sidebars
Plug 'scrooloose/nerdtree'
Plug 'airblade/vim-gitgutter'

" Fuzzy Finder
Plug '/usr/local/opt/fzf'
Plug 'junegunn/fzf.vim'

" Commands
Plug 'terryma/vim-multiple-cursors'

" Color
Plug 'joshdick/onedark.vim'

" File Icons
Plug 'ryanoasis/vim-devicons'

call plug#end()

" ========================================
" Plugin Configs 
" ========================================

" ====== NERDTree Config ======
let NERDTreeIgnore=['\~$', '__pycache__', '*.pyc']
let NERDTreeShowHidden=1

" Make nerdtree look nice
let NERDTreeMinimalUI = 1
let NERDTreeDirArrows = 1
let g:NERDTreeWinSize = 30

" Auto open nerd tree on startup
let g:nerdtree_tabs_open_on_gui_startup = 0

" Focus in the main content window
let g:nerdtree_tabs_focus_on_files = 1

" Using controlP open the file in the default nerdtree window at launch
let g:ctrlp_dont_split = 'NERD_tree_2'

" Open the project tree and expose current file in the nerdtree with Ctrl-\
nnoremap <silent> <C-\> :NERDTreeFind<CR>:vertical res 30<CR>

" ====== MultiCursor Config ======
let g:multi_cursor_exit_from_visual_mode = 0
let g:multi_cursor_exit_from_insert_mode = 0

" ====== Syntastic Config ======
set colorcolumn=0

" ====== Colorscheme Config ======
syntax on
colorscheme onedark

