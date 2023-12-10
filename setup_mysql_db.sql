-- Create a user with a password

CREATE USER chatapp WITH PASSWORD 'noor';
CREATE DATABASE chatapp WITH OWNER = chatapp;
GRANT ALL PRIVILEGES ON DATABASE chatapp TO chatapp;
