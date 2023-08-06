from output.database.database_base import engine

if __name__ == '__main__':
    engine.execute('alter table User add column change_pwd Boolean')
