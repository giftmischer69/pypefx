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

- code
    - [X] add youtube url support as input
    - [X] Shell full step support
    - Memento Pattern  
    - Gui 
      - node-based gui internals
    - add tests
    - add folder as input
- infrastructure
    - [X] add setup.py
    - [X] add building exe
    - add asciicinema gif in readme
    - add pybuilder  
