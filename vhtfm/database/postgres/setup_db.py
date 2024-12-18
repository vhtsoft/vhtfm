import os
import re

import vhtfm
from vhtfm.database.db_manager import DbManager
from vhtfm.utils import cint


def setup_database():
	root_conn = get_root_connection()
	root_conn.commit()
	root_conn.sql("end")
	root_conn.sql(f'DROP DATABASE IF EXISTS "{vhtfm.conf.db_name}"')

	# If user exists, just update password
	if root_conn.sql(f"SELECT 1 FROM pg_roles WHERE rolname='{vhtfm.conf.db_user}'"):
		root_conn.sql(f"ALTER USER \"{vhtfm.conf.db_user}\" WITH PASSWORD '{vhtfm.conf.db_password}'")
	else:
		root_conn.sql(f"CREATE USER \"{vhtfm.conf.db_user}\" WITH PASSWORD '{vhtfm.conf.db_password}'")
	root_conn.sql(f'CREATE DATABASE "{vhtfm.conf.db_name}"')
	root_conn.sql(f'GRANT ALL PRIVILEGES ON DATABASE "{vhtfm.conf.db_name}" TO "{vhtfm.conf.db_user}"')
	if psql_version := root_conn.sql("SHOW server_version_num", as_dict=True):
		semver_version_num = psql_version[0].get("server_version_num") or "140000"
		if cint(semver_version_num) > 150000:
			root_conn.sql(f'ALTER DATABASE "{vhtfm.conf.db_name}" OWNER TO "{vhtfm.conf.db_user}"')
	root_conn.close()


def bootstrap_database(verbose, source_sql=None):
	vhtfm.connect()
	import_db_from_sql(source_sql, verbose)

	vhtfm.connect()
	if "tabDefaultValue" not in vhtfm.db.get_tables():
		import sys

		from click import secho

		secho(
			"Table 'tabDefaultValue' missing in the restored site. "
			"This happens when the backup fails to restore. Please check that the file is valid\n"
			"Do go through the above output to check the exact error message from MariaDB",
			fg="red",
		)
		sys.exit(1)


def import_db_from_sql(source_sql=None, verbose=False):
	if verbose:
		print("Starting database import...")
	db_name = vhtfm.conf.db_name
	if not source_sql:
		source_sql = os.path.join(os.path.dirname(__file__), "framework_postgres.sql")
	DbManager(vhtfm.local.db).restore_database(
		verbose, db_name, source_sql, vhtfm.conf.db_user, vhtfm.conf.db_password
	)
	if verbose:
		print("Imported from database {}".format(source_sql))


def get_root_connection():
	if not vhtfm.local.flags.root_connection:
		import sys
		from getpass import getpass

		if not vhtfm.flags.root_login:
			vhtfm.flags.root_login = (
				vhtfm.conf.get("postgres_root_login")
				or vhtfm.conf.get("root_login")
				or (sys.__stdin__.isatty() and input("Enter postgres super user [postgres]: "))
				or "postgres"
			)

		if not vhtfm.flags.root_password:
			vhtfm.flags.root_password = (
				vhtfm.conf.get("postgres_root_password")
				or vhtfm.conf.get("root_password")
				or getpass("Postgres super user password: ")
			)

		vhtfm.local.flags.root_connection = vhtfm.database.get_db(
			socket=vhtfm.conf.db_socket,
			host=vhtfm.conf.db_host,
			port=vhtfm.conf.db_port,
			user=vhtfm.flags.root_login,
			password=vhtfm.flags.root_password,
			cur_db_name=vhtfm.flags.root_login,
		)

	return vhtfm.local.flags.root_connection


def drop_user_and_database(db_name, db_user):
	root_conn = get_root_connection()
	root_conn.commit()
	root_conn.sql(
		"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = %s",
		(db_name,),
	)
	root_conn.sql("end")
	root_conn.sql(f"DROP DATABASE IF EXISTS {db_name}")
	root_conn.sql(f"DROP USER IF EXISTS {db_user}")
