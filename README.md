# pypefx

apply an effects pipeline to a song.

## Usage:

````shell
# cli usage: 
python -m pypefx

python -m pypefx ++mode=cli +input="song.mp3" +profile=profile_name 

# shell usage:
python -m pypefx ++mode=shell  

python -m pypefx +input="song.mp3" ++output="output.wav"

# gui usage:
python -m pypefx ++mode=gui

# enabling debug logging:
python -m pypefx hydra.verbose=True
````

<hr>

## How it works:

````text
┌─────┐                                             
│input│                                             
└┬────┘                                             
┌▽─────────────────────┐                            
│optional_input_effects│                            
└┬─────────────────────┘                            
┌▽─────────────────────────────┐                    
│spleeter                      │                    
└┬────────┬────────┬──────────┬┘                    
┌▽──────┐┌▽──────┐┌▽────────┐┌▽──────────┐          
│track_4││track_2││track_3  ││track_1    │          
└┬──────┘└────┬──┘└────────┬┘└──────────┬┘          
┌▽──────────┐┌▽──────────┐┌▽──────────┐┌▽──────────┐
│effect_4...││effect_2...││effect_3...││effect_1...│
└┬──────────┘└┬──────────┘└┬──────────┘└┬──────────┘
┌▽────────────▽────────────▽────────────▽┐          
│combiner                                │          
└┬───────────────────────────────────────┘          
┌▽──────────────────────┐                           
│optional_output_effects│                           
└┬──────────────────────┘                           
┌▽─────┐                                            
│output│                                            
└──────┘    
````

[diagram source](https://arthursonzogni.com/Diagon/#GraphDAG)

## VST Effects Source

http://vstplanet.com/Effects/Effects.htm

## TODOs

- code
    - add youtube url support as input
    - node-based gui internals
    - add tests
- infrastructure
    - add setup.py
    - add building exe
    - add pybuilder  
