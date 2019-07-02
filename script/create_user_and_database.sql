/*  Create user/role "oc-pizza" 
    for access database oc-pizza only.
    can not create database, can login, 
    is not superuser, can nopt create role,
    please, do create password as soon as possible.*/
CREATE USER "oc-pizza" WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION;
COMMENT ON ROLE "oc-pizza" IS 'Accès privilégié à la base de données oc-pizza';
/*  Create database "oc-pizza"  for user "oc-pizza" 
    and fr UTF-8 chars encoding */
CREATE DATABASE "oc-pizza"
    WITH 
    OWNER = 'oc-pizza'
    ENCODING = 'UTF8'
    LC_CTYPE = 'fr_FR.UTF-8'
    CONNECTION LIMIT = -1;
COMMENT ON DATABASE "oc-pizza"
    IS 'OpenClassRooms
Path Python
projet 6: -- OC-Pizza --';
