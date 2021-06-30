# pypefx

apply an effects pipeline to a song.

(held together by elmer's glue)

## Usage:

````shell
# every command can be run with 
# either: python -m pypefx [args]
# or:     pypefx [args]

# cli usage: 
pypefx

pypefx --help

pypefx --version

pypefx -i song.mp3 -p profile_name -o output.wav 

# shell usage:
pypefx -m SHELL  

# gui usage:
pypefx -m GUI

# enabling debug logging:
pypefx -d [args]
pypefx --debug [args]
````

<hr>

## How it works:

````text
┌──────────┐             
│input_file│             
└┬─────────┘             
┌▽───────┐               
│effect_1│               
└┬───────┘               
┌▽───────┐               
│effect_2│               
└┬───────┘               
┌▽──┐                    
│...│                    
└┬──┘                    
┌▽───────┐               
│effect_N│               
└┬───────┘               
┌▽──────────────────────┐
│ExportStep(output_file)│
└───────────────────────┘
````
[diagram source](https://arthursonzogni.com/Diagon/#GraphDAG)

## VST Effects Source

http://vstplanet.com/Effects/Effects.htm

## TODOs

- make it possible
  - [X] core functionality
  - [X] add youtube url support as input
  - [X] Shell full step support
  - [X] Memento Pattern  
  - [X] add setup.py
  - [X] add building exe
  - add pybuilder
  - add asciicinema gif in readme
  - make Gui possible 
    - node-based gui internals
  - add tests
  - add support for a folder as input
- make it beautiful
  - rewrite (some) class structure
  - add readthedocs documentation
  - document avialable steps in readme
  - maybe add python fire cli for pypefx --steps bass +3 gain -3 vst "plugins/test.dll" "plugins/test.fxp"  
  - pylint, pybuilder, etc...
- make it fast
  - performance (multithreading, etc.)
  - cython
- make a full release (1.0.0)   
- linux support 
  - test linux wine support (ubuntu/pop_os)
