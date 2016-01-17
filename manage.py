from pytalog import app, db
from flask.ext.script import Manager, Server, prompt_bool
from pytalog.seed_db import seed

manager = Manager(app)
server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


@manager.command
def initdb():
    db.create_all()
    print 'Initialized the database'


@manager.command
def seeddb():
    seed()
    print 'Seed the database with data'


@manager.command
def dropdb():
    if prompt_bool("Are you sure?"):
        db.drop_all()
        print 'Database dropped'


if __name__ == '__main__':
    manager.run()
