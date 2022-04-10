# Data Acquisition and Telemetry Application
Handles all data collection from the sensors on [Georgia Tech Off-Road's](https://gtor.gatech.edu/) car and displays sensor data in real time. 
Exports data directly to MATLAB workspace for mechanical team's use, in addition to CSVs.

Designed with/for [Python 3.6.8](https://www.python.org/downloads/release/python-368/)

[GitHub Repo](https://github.com/Georgia-Tech-Off-Road/GTORDaata/)

## How to Run

1. Install dependencies in `install_dependencies.bat` (by double-clicking on the 
file).
2. Run `daata.py`

This app may be run with fake data (user may select `Fake Data` under `Input`) for 
testing. 

### Google Drive
This app enables a user to download and upload collected data onto our shared Google Drive.
Users must first have access to the 
[GTORDaata's shared Google Drive](https://drive.google.com/drive/u/0/folders/1OaMbG-wAqC6_Ad8u5FiNS9L8z2W7eB2i) 
in order to upload or download testing data. Further, the secret API key 
(`secret_oAuth_key.json`) must be downloaded [here](https://drive.google.com/file/d/117yhiyV2BAZNxityj4la6J50FECaEPJB/view?usp=sharing), 
and put into the top-level directory of this repo, i.e. at the same level as this `README.md`. 

Not acquiring this API key does not impede other aspects of this app's functionality.

## About

_Designed by the [Georgia Tech Off-Road]([GitHub Repo](https://github.com/Georgia-Tech-Off-Road/GTORDaata/)) Data Acquisition and Electrical Engineering (DAQ) subteam_

### Spring 2022 Contributors
1. Andrew Hellrigel (Lead Data Acquisition and IT Engineer)
2. Ryan Chen (Lead Electrical Systems Engineer)
3. Benjamin Boeckman
4. Param Pithadia
5. Faris Durrani
6. Peter
7. Caden Farley
8. Vishnav Deenadayalan
9. Akash Harapanahalli
10. Vincent Fang