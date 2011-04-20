webpy-mongodb-sessions
===

A SessionStore class that allows you to use web.py sessions with MongoDB.

To setup:

    import web
    from session import MongoStore
    from pymongo import Connection
    #if you want to do user auth stuff add the following line
    import users
 
    #First get a MongoDB database object
    c = Connection()
    db = c.webpy

    #Create a new session object, passing the db and collection name to the MongoStore object
    session = web.session.Session(app, MongoStore(db, 'sessions'))

    #If you want to do user authentication and stuff aswell, add these two lines
    users.session = session
    users.collection = db.users
    users.SALTY_GOODNESS = u'RANDOM_SALT'
 
To use:
   
    You can now use the `session` object as you would do with normal web.py sessions - http://webpy.org/cookbook/sessions.

    To handle user stuff:

    #USER REGISTRATION
    users.register(username=username, password=users.pswd(password), contacts=[]) # Add anything you want to store as kwargs

    #USER LOGIN AND AUTH
    user = users.authenticate(username, pass)
    if user:
        users.login(user)
    else:
        #Handle your login failure
        pass

    #GET LOGGED IN USER
    users.get_user()

    #USER LOGOUT
    users.logout()

    #RESTRICT A URL TO LOGGED IN USERS
    class Hidden:
        @users.login_required
        def GET(self):
            #Do your stuff
            pass
