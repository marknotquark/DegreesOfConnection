#!/usr/bin/python3
import sqlite3,sys
import itertools

# -- Helpers

def getAdjacentActors(actor):
    '''
    Returns a list of adjacent actors given an actor's name.
    Returns list, potentially empty.
    '''

    query = f"""
        SELECT a3.actor_id 
        FROM movie m
            JOIN acting a1 on m.id = a1.movie_id
            JOIN actor a2 on a1.actor_id = a2.id and a2.id = {actor}
            JOIN acting a3 on a3.movie_id = m.id and a3.actor_id <>  a2.id
        GROUP BY a3.actor_id;
    """
    cur.execute(query)
    results = cur.fetchall()

    # Get a list of adjacent actors, excluding the original actor.
    return [adjActor[0] for adjActor in results if (adjActor[0] != actor)]

def createGraph(actor, target_actor):
    '''
    Transverse the graph, finding the next point, creating a graph.
    Returns new prediction
    '''

    q = "SELECT count(*) FROM actor;"
    cur.execute(q)
    
    actCount = cur.fetchone()[0]
    
    dis = [float("inf") for _ in range(0, actCount + 1)]
    pred = [[] for _ in range(0, actCount)]
    visited = set([actor])
    updated = set()
    dis[actor] = 0

    ## -- Referenced from CodeForGeeks
    while (True):
        adjacentActors = getAdjacentActors(actor)
        for act in adjacentActors:
            if dis[act] > dis[actor] + 1:
                dis[act] = dis[actor] + 1
                pred[act] = [actor]
            elif dis[act] == dis[actor] + 1:
                pred[act].append(actor)
            updated.add(act)
        visited.add(actor)

        # -- Calculate what point to visit next

        # Closest is set to infinite for first additional bound comparions
        closest = float("inf")
        closestActor = None

        # If the actor is closer, set the closest actor to the newest closest.
        for actor in updated:
            if actor not in visited and dis[actor] < closest:
                closestActor = actor
                closest = dis[actor]

        if closest > 5 or closest > dis[target_actor]:
            return pred
        
        visited.add(closestActor)
        actor = closestActor

def calculatePath(start, end):
    '''
    Calculates a path from start to end
    Calls createGraph to create a graph

    Returns a path from start to end. (list)
    '''

    predicted = createGraph(start, end)


    ''' 
    Interior recurisve find function to make predictions
    Calls itself to find next step
    '''
    def recursiveFind(start, end):
        if start in predicted[end]:
            return [[start, end]]

        paths = []

        for predictedActor in predicted[end]:
            newPath = recursiveFind(start, predictedActor)
            
            for i in range(0, len(newPath)):
                newPath[i].append(end)
     
            paths.extend(newPath)
        
        return paths

    return recursiveFind(start, end)

def createOutput(arrOfLine):
    '''
    Output manager given lines; joins lines and adds new formatting based on the ASCII-sort.

    Returns string.
    '''

    arrOfLine.sort()

    for i in range(0, len(arrOfLine)):
        arrOfLine[i] = f"{i + 1}. " + arrOfLine[i]
    return "\n".join(arrOfLine)

# -- Main

# Check arguments
if len(sys.argv) != 3:
    print(sys.argv[0] + ": [First Actor] [Second Actor]")
    sys.exit(1)

# Attempt connection to databse
try:
    con = sqlite3.connect('a2.db')
except:
    print("Could not connect to database")
    sys.exit(1)

cur = con.cursor()

# Ensure actors exist
cur.execute(f"select r.name from actor r where r.name LIKE '{sys.argv[1]}';")
startRes = cur.fetchone() 

cur.execute(f"select r.name from actor r where r.name LIKE '{sys.argv[2]}';")
endRes = cur.fetchone() 

if startRes != None and endRes != None:
    startActor = startRes[0]
    targetActor = endRes[0]
else:
    print("One or more actors could not be found in database.")
    sys.exit(0)


# Retrieve ID of the two actors
sql = "SELECT id FROM actor WHERE lower(name) = lower(?)"
cur.execute(sql, (startActor,))
startID = cur.fetchone()[0]
cur.execute(sql, (targetActor,))
endID = cur.fetchone()[0]

paths = calculatePath(startID, endID)
string_list = []
lines = []

for path in paths:

    relatedMovies=[]

    #  Build a name list to all the id in path
    startActors = []
    for startID in path:
        q = f"SELECT name FROM actor WHERE id = {startID};" 
        cur.execute(q)
        startActors.append(cur.fetchone()[0])
    
    for i in range(0, len(path) - 1):
        
        firstName, secondName = (startActors[i], startActors[i+1])
        
        # Query for movie details
        q = """
        SELECT title, year 
        FROM (
            SELECT m.title, m.year, group_concat(a2.name) AS actor_name FROM movie m
            JOIN acting a ON m.id = a.movie_id
            JOIN actor a2 ON a.actor_id = a2.id
            GROUP BY m.title)
        WHERE actor_name like ? and actor_name like ?;
        """
        cur.execute(q, [f"%{firstName}%", f"%{secondName}%"])

        moviesPath = [(m[0], m[1]) for m in cur.fetchall()]
        relatedMovies.append(moviesPath)

    relations = list(itertools.product(*relatedMovies))

    # -- Create output
    for r in relations:
        strList = []
        for i in range(0, len(r)):
            appendStr = f"{startActors[i]} was in {r[i][0]} "
            if r[i][1] != None:
                appendStr += f"({r[i][1]}) with {startActors[i+1]}"
            else:
                appendStr += f"with {startActors[i+1]}"

            strList.append(appendStr)
        lines.append("; ".join(strList))

print(createOutput(lines))

con.close()
