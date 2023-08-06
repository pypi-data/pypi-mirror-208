# python-package-backend-template
To create local package and remote package layers (not to create GraphQL and REST-API layers)

#database scripts
Please place <table-name>.py in /db 
No need for seperate file for _ml table
  
# Create the files to create the database schema, tables, view and populate Meta Data and Test Date
/db/<table-name>.py - CREATE SCHEMA ... CREATE TABLE ... CREATE VIEW ...<br>
/db/<table-name>_insert.py to create records

# Update the setup.py (i.e.name, version)
