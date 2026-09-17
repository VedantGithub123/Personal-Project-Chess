# Project Overview

The goal of this project is to develop a chess interface to support human-human, human-computer, and computer-computer play. The bots use a minimax algorithm. This was my final project for the Grade 11 ICS3U0 Introduction to Computer Programming.

## Getting Started

Ensure Git is installed and setup to work with he repository

Clone the project repository to your local machine and navigate into the directory:
```
git clone https://github.com/VedantGithub123/Personal-Project-Chess.git
cd Personal-Project-Chess
```

Ensure Python, PyGame, and NumPy are installed and set up

## Repository Structure

The `main` branch is the organized working branch. Below is an overview of the folder structure for the `main` branch of this repository
```
Personal-Project-Chess/
├── media/
├── src/
│   ├── images/
│   ├── chess.py
│   └── dataStorageAlgo.txt
└── README.md
```

### Folder Descriptions

`media/`: Contains photos of the project

`src/`: Contains code, assets, and data storage files

&emsp;&emsp;`images/`: Stores image assets

&emsp;&emsp;`chess.py`: Python file to run the program

&emsp;&emsp;`dataStorageAlgo/`: Text file containing precomputer moves

`README.md`: Project repository documentation

## Code Overview

The first component to decide was how to store the chessboard as data. The most clear way is a 2D array, which is what I ended up using. Then I needed a way to identify the possible moves given a selected piece. To do this, I identified which piece it was. Based on that, it checked the possible squares the piece could go to to create a list of possible moves, stored as a chessboard state. I also had to consider special moves, such as en passant and castling.

Once the entire framework was done, I needed to make an interface using PyGame. There isn't much to say about it. For the chess bot algorithms, I apply a minimax algorithm. Changing the depth changes the difficulties.