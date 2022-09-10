create database cardb; 

create table dim_customer (
id integer primary key,
name varchar (255) , 
phone_number varchar (20)
);

create table dim_salesperson (
id integer primary key,
name varchar (255) , 
joindate date
);

create table dim_car (	
id integer primary key,
manufacturer varchar(255),
model_name varchar(255), 
serial_number varchar(255), 
weight float, 
price float
);

create table transaction (
id integer primary key,
customerid integer,
salespersonid integer, 
carid integer,
transaction_date date,
);



