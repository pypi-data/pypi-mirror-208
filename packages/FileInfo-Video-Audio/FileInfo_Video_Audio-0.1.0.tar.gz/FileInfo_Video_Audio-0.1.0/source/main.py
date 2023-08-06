#! /usr/bin/python
import os
import json
import sys
from .lib.Argument import Argument
Argument=Argument(sys.argv)

def help():
    print("<FileInfo> [Options].. ")

def main():
    if Argument.hasOptionValue('-file'):
        if Argument.getoptionvalue('--type') and Argument.getoptionvalue('--option'):
            file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
            try:
                if file_content["media"]["track"]:
                    for track in file_content["media"]["track"]:
                        if(track['@type'] == Argument.getoptionvalue('--type')):
                            d = json.dumps(track, indent=4)
                            option = Argument.getoptionvalue('--option')
                            for i in track.keys():
                                if option == i:
                                    print(f"{option} ==> {track[i]}")
                else:
                    raise Exception("Unable to fetch the Tracks of your Source file")
            except ValueError as e:
                print(e)
                
        # elif Argument.getoptionvalue('--type') and (Argument.hasOption(['--list_All_keys']) or Argument.hasOption(['-l'])):
        #     file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
        #     try:
        #         if file_content["media"]["track"]:
        #             for track in file_content["media"]["track"]:
        #                 if(track['@type'] == Argument.getoptionvalue('--type')):
        #                     for i in track.items():
        #                         print(f"{i[0]}    ==> {i[1]}")
        #         else:
        #             raise Exception("Unable to fetch the Tracks of your Source file")
        #     except ValueError as e:
        #         print(e)
                            
        # elif Argument.hasOption(['--type']) and (Argument.hasOption(['--help']) or Argument.hasOption(['-h'])):
        #     file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
        #     try:
        #         if file_content["media"]["track"]:
        #             for track in file_content["media"]["track"]:
        #                 tracks = track['@type']
        #                 if tracks =="General":
        #                     print(f"{tracks}  ==> Show's the Files General properties" )
        #                 if tracks =="Video":
        #                     print(f"{tracks}    ==> Show's the Files Video properties" )
        #                 if tracks =="Audio":
        #                     print(f"{tracks}    ==> Show's the Files Audio properties" )
        #         else:
        #             raise Exception("Unable to fetch the Tracks of your Source file")
        #     except ValueError as e:
        #         print(e)
                    
                    
        # elif Argument.getoptionvalue('--type') and  Argument.hasOption(['--options']):
        #     file_content = json.loads(os.popen('mediainfo --Output=JSON '+Argument.getoptionvalue('-file')).read())
        #     try:
        #         if file_content["media"]["track"]:
        #             for track in file_content["media"]["track"]:
        #                 if(track['@type'] == Argument.getoptionvalue('--type')):
        #                     type = Argument.getoptionvalue('--type')
        #                     for i in track:
        #                         print(f"{i}  ==> {i} of the Source File")
        #         else:
        #             raise Exception("Unable to fetch the Tracks of your Source file")
        #     except ValueError as e:
        #         print(e)
      
    else:
        help()
        
if __name__ == "__main__":
    main()

        

                            

            
                    
                


            


