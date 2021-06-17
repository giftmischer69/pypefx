# pypefx

apply an effects pipeline to a song.

## Cli Usage:

````shell
python -m pypefx

python -m pypefx +input="song.mp3" 

python -m pypefx +input="song.mp3" ++output="output.wav"
````

## Gui Usage:

````shell
python -m pypefx ++mode=gui
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