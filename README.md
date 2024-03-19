# CSC 480 - Doom Project

Cal Poly Winter 2024 - Professor Rodrigo Canaan

Team Members:

* Zhi He
* Gordon Luu
* Andre Mapili
* Dennis Phun
* Sean Phun

This repo is a combination of three repos:

* [VDAIC2017](https://github.com/mihahauke/VDAIC2017)
  * f1
  * **host** (don't need to care about the others)
  * intelact
  * no_host
  * random
  * RandomTeam_track1n2
* [Arnold](https://github.com/glample/Arnold) - (renamed as 480Arnold)
* [sample-factory](https://github.com/alex-petrenko/sample-factory)

It's in a bit of a state of disarray, but everything should work properly. You shouldn't have to edit any of the code except for in `sample-factory/sf_examples/vizdoom/doom/multiplayer/doom_multiagent.py` to switch between the multiplayer and self-evaluation modes.

## Usage
This repo has two use cases: self-eval and multiplayer.

Regardless of the style of play, there are two virtual environments to be aware of.  

One should be used for all `VDAIC2017` and `Arnold` related things, the dependencies should be easily gathered from a the `requirements.txt` file found here.  

The other virtual environment should deal with the `sample-factory` directory. I believe `pip install sample-factory`, `pip install sample-factory[vizdoom]`, and `pip install vizdoom` should gather all the things required to run.

### Self-eval
To run the Arnold bot's self-eval you simply need to:
```bash
-- Activate virtual environment for arnold/host
cd 480Arnold
./run.sh sf
```  
If you want visualization, run `sf2` instead of `sf`.  
Edits to the evaluation time can be done in `./480Arnold/src/doom/scenarios/deathmatch.py` on line 69.

The Sample Factory self-eval is a little more complex. Basically, Sample Factory will treat every game like it is a multiplayer game, so you have to make sure you are just hosting the server itself.

In `sample-factory/sf_examples/vizdoom/doom/multiplayer/doom_multiagent.py`, make sure lines 150-154 are commented **out** and lines 96-148 are **not**. Then, you should be able to simply:
```bash
cd sample-factory
-- Activate virtual environment for sample-factory
python -m sf_examples.vizdoom.enjoy_vizdoom --env=doom_deathmatch_bots --experiment=doom_deathmatch_bots --train_dir=./train_dir --no_render
```
You can add `--device=cpu` to run it if you don't have a CUDA graphics card. If you want visualization, remove the `--no_render` argument.

### Multiplayer
Try to run these commands in quick succession because they do have timeout times.  

Start up the host:
```bash
python host/host.py -p 2 -b 8 -m 1 -w
```
`-p 2` says there will be 2 players.
`-b 8` will spawn 8 bots.
`-m 1` makes sure we're playing on map id 1
`-w` enables spectator mode, I never got the camera to be able to move on WSL but maybe you'll have som luck...?

Start up Arnold:
```bash
cd 480Arnold
./run.sh sf3
```

Start up Sample Factory:  
In `sample-factory/sf_examples/vizdoom/doom/multiplayer/doom_multiagent.py`, make sure lines 196-148 are
commented **out** and lines 150-154 are **not**. Then:
```bash
cd sample-factory
python -m sf_examples.vizdoom.enjoy_vizdoom --env=doom_deathmatch_bots --experiment=doom_deathmatch_bots --train_dir=./train_dir
```

## Results
You can run the self-eval commands, the Arnold one 10 times and the Sample Factory one for 10 episodes and gather up the statistics yourself. Keep in mind the environments are not identical (notably Arnold getting a lot of time wasted on the silly spawn bug).

Alternatively here's a list:  
Arnold (25.5±8.031)
[28, 23, 30, 24, 22, 14, 38, 15, 24, 37]

Sample Factory (67±5.578)
[62, 74, 68, 56, 72, 70, 63, 70, 64, 71]

You can also run the multiplayer as shown above which will print out a summary at the end of the match:
|   Player |   Frags |
|----------|---------|
|     2(SF)|     105 |
| 3(Arnold)|      17 |

Some videos are included in this directory showing off the bots.
