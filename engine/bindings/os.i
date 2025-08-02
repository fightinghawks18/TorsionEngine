%module os

%{
#include "os/window.h"
%}

%include "std_string.i"

%ignore SDL_Window;
%ignore SDL_WINDOWPOS_CENTERED;

%include "os/window.h"