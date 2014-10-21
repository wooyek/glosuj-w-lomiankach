# coding=utf-8
# Copyright 2013 Janusz Skonieczny
import os

from flask_script import Manager, Command


class InitDatabase(Command):
    """Initialize database"""
    def run(self):
        from flask import current_app
        datafile = current_app.config.get("SQLALCHEMY_DATABASE_URI")[10:]
        if os.path.exists(datafile):
            os.remove(datafile)
        from website.database import db
        db.create_all()

def setup_manager():

    import main
    app = main.create_app(**main.OPTIONS)

    manager = Manager(app)
    manager.add_command('resetdb', InitDatabase())

    from flask_security import script
    manager.add_command('create-user', script.CreateUserCommand())
    manager.add_command('create-role', script.CreateRoleCommand())
    manager.add_command('add-role', script.AddRoleCommand())
    manager.add_command('remove-role', script.RemoveRoleCommand())
    manager.add_command('activate-user', script.ActivateUserCommand())
    manager.add_command('deactivate-user', script.DeactivateUserCommand())

    from flask_migrate import MigrateCommand
    manager.add_command('db', MigrateCommand)

    from flask_script.commands import ShowUrls
    manager.add_command('rules', ShowUrls)


    from flask_assets import ManageAssets
    manager.add_command("assets", ManageAssets())
    return manager

if __name__ == "__main__":
    manager = setup_manager()
    manager.run()
