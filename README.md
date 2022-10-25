# AWS - (Python 3.9): Amazon Linux Server run on a EC2 instance
![1024px-Amazon_Web_Services_Logo svg (1)](https://user-images.githubusercontent.com/46793138/197844527-8bba5ee7-bd19-4c5f-b0bc-471f07bbf490.png)
AWS | EC2 | DynamoDB | AWS Lambda
## AWS Features:
- AWS DynamoDB (Non relational database) to store all user names

- AWS Lambda Cloud functions to manipulate the database as needed

- EC2 instance to keep the server running in its own session, even when I'm away from my computer (though, I can also turn it on and off when needed)

## Matchmaking
- 2 players per match

- When one player requests matchmaking, they are put into a waiting room. Once a second client joins, a match is made and they get put into a game session

- When a 3rd client joins, the step above repeats itself, they are put into a different game session

- If a client leaves in an active match, the other client gets kicked back to the matchmaking menu
## User Authentication
- Every player has to sign in or create an account in order to play

- If the player created a new account, it gets added as a new item on the database

- If the player is logging in with an existing account, they're status gets set to "active" on the database

- No player can login more than once (ie: If a player is logged in and actively playing, no one else can login with that account)

- Checks for user taken, wrong user and wrong password
## Real Time
- Networked Player Movement - replicated on each client

- Networked Projectiles - replicated on each client
 
- Networked Asteroids - replicated on each client
## Server Threading (Not controllable by anyone except for me)
- Server messages are listening on a seperate thread from the main thread

- Daemon Thread to run run the server, once the main thread stops, the server thread stops also

- Once the server thread stops, all clients logged in get kicked back to the "Connect to Host" menu. Their status gets set to "offline"

- Press any key to stop the server thread
