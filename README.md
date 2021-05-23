# Degrees Of Connection
> A simple "Kevin Bacon" style degrees of connection based on an MySQL database

## What is it?
"Six Degrees of Kevin Bacon" is a game whereby someone is challenged to find a connection between any arbitrary actor and Kevin Bacon, through 6 shared connections (ie, movie appearances). This Python script emulates this with any two actors, given a SQL database of actors, and movies, along with a reference for actors performing in movies. It generates a graph representation, where nodes are actors and edges are movies they have acted in together; this graph is then tranversed, and finds the shortest possible path between the two actors, along with the actors and movies that connect any two arbitrary actors.



