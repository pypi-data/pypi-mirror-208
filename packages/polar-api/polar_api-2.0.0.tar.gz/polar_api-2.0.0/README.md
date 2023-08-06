# Polar API

### Overview
This repository contains code to extract data from Polar Team Pro API.

### Usage
### Installation

Username and password
```
pip install git+https://github.com/FC-Nordsjaelland/polar-api.git
```

SSH key
```
pip install git+ssh://git@github.com/FC-Nordsjaelland/polar-api.git
```

### Documentation
Documentation can be found [here](https://www.polar.com/teampro-api/?python#teampro-api)

### Repository structure
```
Polar API repository
|
|── get_player_session_trimmed.py
|── get_session_raw_gps.py
|
|── polar_api
|   |── polar_api.py
|   └── cleaning.py
|
|── scripts
|   |── download_raw_data.py
|   |── get_player_session_trimmed.py
|   |── get_session_raw_gps.py
|   |── gps_data_project.py
|   └── session_viz.py
|
|── utils
|   |── metadata.py
|   |── polar_api_old.py
|   └── polar_IO.py
```
