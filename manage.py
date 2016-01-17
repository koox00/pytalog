from pytalog import app, db
from flask.ext.script import Manager, prompt_bool
from pytalog.seed_db import seed
manager = Manager(app)


@manager.command
def initdb():
    db.create_all()
    print 'Initialized the database'

@manager.command
def seeddb():
    seed()
    print 'Initialized the database'


@manager.command
def dropdb():
    if prompt_bool("Are you sure?"):
        db.drop_all()
        print 'Database dropped'


if __name__ == '__main__':
    manager.run()
