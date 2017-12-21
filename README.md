This is the source code for the project Flight Rout



To use this sorce code put all the files in the same folder (including the logo file)

You will need to create also 4 folders:

delay_raw
fares_raw
delay_clean
fares_clean


Put the raw data in the raw folders and run the command:

$ python  clean_build_data.py


Start Docker with GrapheneDB using the commands:

$ sudo sh docker_load_images.sh
$ sudo sh docker_start_graphDB.sh


Start the Best Route software using the command:

$ python  best_route.py


When done, close the Best Route GUI and shotdown Docker with the command:

$ sudo sh docker_stop_graphDB.sh



Created by Guy Farkash
