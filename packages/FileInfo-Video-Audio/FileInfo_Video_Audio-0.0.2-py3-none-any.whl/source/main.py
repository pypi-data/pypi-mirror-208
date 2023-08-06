#! /usr/bin/python
import os
import json
import sys
from source.lib.Argument import Argument
Argument=Argument(sys.argv)


def help():
    print("<FileInfo> [Options].. ")

if Argument.hasOptionValue('-file'):
    if Argument.getoptionvalue('--type') and Argument.getoptionvalue('--option'):
        file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
        for track in file_content["media"]["track"]:
            if(track['@type'] == Argument.getoptionvalue('--type')):
                d = json.dumps(track, indent=4)
                option = Argument.getoptionvalue('--option')
                for i in track.keys():
                    if option == i:
                        print(f"{option} ==> {track[i]}")
                        
    elif Argument.hasOption(['--type']) and (Argument.hasCommands(['--help']) or Argument.hasOption(['-h'])):
        file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
        for track in file_content["media"]["track"]:
            tracks = track['@type']
            if tracks =="General":
                print(f"{tracks}  ==> Show's the Files General properties" )
            if tracks =="Video":
                print(f"{tracks}    ==> Show's the Files Video properties" )
            if tracks =="Audio":
                print(f"{tracks}    ==> Show's the Files Audio properties" )
                
    elif Argument.getoptionvalue('--type') and  Argument.hasOption(['--options']):
        file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
        for track in file_content["media"]["track"]:
            if(track['@type'] == Argument.getoptionvalue('--type')):
                type = Argument.getoptionvalue('--type')
                for i in track:
                    print(f"{i}  ==> {i} of the Source File")
                     
    elif (Argument.hasOption(['--help']) or Argument.hasOption(['--help'])) and Argument.hasOptionValue('-file'):
        file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
        for track in file_content["media"]["track"]:
            print(f"Your Tracks are ==> {track['@type']}")
        
else:
    help()
    

                        

        
                
            


        


