This is a simple Python library that enables simple authentication.
For each authentication, the server generates a new and different number with the function authrand().
The server sends the new number to the client to check if the client is for real.
The client calls authenticate_self() with the arguments the secret key and the number it recieved(the key is a number too),
and sends the result back to the server.
To check if the client is authentic, the server calls verify() with the number it sent to the client, the secret key,
and what it recieved from the client.
verify() returns True if the client is authentic, and false if the client is lying.