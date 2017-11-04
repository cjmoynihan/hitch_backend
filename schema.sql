drop table if exists users;
create table users (
    user_id integer unique primary key autoincrement,
    email text unique not null,
    firstname text not null,
    lastname text not null
);
drop table if exists rides;
create table rides (
    ride_id integer unique primary key autoincrement,
    user_id integer not null,
    source_lat float not null,
    source_long float not null,
    dest_lat float not null,
    dest_long float not null,
    depart_time long not null,
    total_seats int not null,
    cost float not null
);
drop table if exists passengers;
create table passengers (
    id integer unique primary key autoincrement,
    ride_id integer not null,
    passenger_id integer not null,
    unique(ride_id, passenger_id)
);