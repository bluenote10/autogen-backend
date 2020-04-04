from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
import simplejson

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

import logging

logger = logging.getLogger(__name__)

"""
Resources:
- Core Tutorial: https://docs.sqlalchemy.org/en/13/core/tutorial.html

About whether using flask_sqlachemy is really useful:
- https://pypi.org/project/flask-sqlalchemy-core/
- https://stackoverflow.com/questions/22156897/pattern-for-a-flask-app-using-only-sqlalchemy-core
"""


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        logger.debug("Enabling foreign key support for SQLite3Connection")
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def json_response(data, status=200):
    response = make_response(simplejson.dumps(data, ignore_nan=True), status)
    response.mimetype = "application/json"
    return response


def create_get_view_func(db, table):

    def view_func(*args, **kwargs):
        logger.info("Request {} args: {} kwargs: {}".format(request.method, args, kwargs))

        if request.method == 'GET':
            result = db.session.execute(table.select())
            result_columns = result.keys()
            # Build return data
            data = []
            for row in result:
                record = {
                    result_columns[i]: row[i]
                    for i in range(len(row))
                }
                data.append(record)

            return json_response(data)
        else:
            body = request.get_json(force=True)
            logger.info("Request body: {}".format(body))

            # TODO: add body validation based on schema

            # https://stackoverflow.com/a/22084672/1804173
            ins = table.insert().values(**body)
            try:
                result = db.session.execute(ins)
                db.session.commit()
                inserted_id = result.inserted_primary_key[0]
                return json_response({
                    "id": inserted_id
                })
            except Exception as e:
                return json_response({
                    "msg": str(e)
                }, 400)

    return view_func


def app_builder(metadata, tables):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
    # app.config['SQLALCHEMY_ECHO'] = True

    db = SQLAlchemy(app, metadata=metadata)
    db.create_all()

    for table in tables:
        route = "/{}".format(table.name)
        logger.info("Adding route: {}".format(route))

        # https://stackoverflow.com/a/13734321/1804173
        app.add_url_rule(
            route,
            endpoint=table.name,
            view_func=create_get_view_func(db, table),
            methods=['GET', 'POST'],
        )

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    return app


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S',
    )
    logging.getLogger('sqlalchemy').setLevel(logging.INFO)

    from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

    metadata = MetaData()

    users = Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String),
        Column('fullname', String),
    )

    addresses = Table(
        'addresses',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', None, ForeignKey('users.id')),
        Column('email_address', String, nullable=False)
    )

    app = app_builder(metadata, [users, addresses])
    app.run()
