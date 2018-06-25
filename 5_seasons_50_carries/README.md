# Which running backs have had 50+ carries in each of the last 5 years?
This folder contains a Python 3 program and a Jupyter Notebook notebook that can scrape data from [The Football Database](https://www.footballdb.com/) and places it into a data frame. The notebook uses the `Requests` and `Beautiful Soup 4` modules to gather the web page data. A `Player` class is used to create objects representing a single player. The program loops through the 5 most recent NFL seasons and gathers data for each season. A sample `.csv` output file is included in this repository.

## Requirements
The following Python 3 libraries are needed to run this program: `Requests`, `Beautiful Soup 4`, `NumPy`, and `Pandas`. 

It also requires the `Player` class from `../player.py`.

## Usage
To run `5_seasons_50_carries.py`, make sure the libraries listed above are installed and use the following Terminal command:

`python3 5_seasons_50_carries.py`

If no problems occur, a `.csv` output file should be saved in `5_seasons_50_carries.py`'s current directory. 