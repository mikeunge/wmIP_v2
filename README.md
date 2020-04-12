# wmIP_v2

Script that gets your public ip 🌎.
This little script gets your puplic ip and stores it (and all the changes) in a storage file.

Feel free to give it a try.


## But why?

Because I need the public ip from mine and/or some other unix boxes to do some stuff (like a ssh or vpn connection).

The script is fast and it just works as I want it to.


## Todo

- [ ] Dump the current ip to a different file
- [x] Read and write the IP (& changes) to an .json file
  - [x] Everytime the public IP changes, a new entry to the json file is made
  - [x] Keep track of the datetime
- [x] Add logging function
- [x] Fix the 'first time' issues
  - [x] Create storage.json automatically (if not exists)
  - [x] Create first entry if not exists
