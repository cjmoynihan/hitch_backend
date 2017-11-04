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
    src_lat float not null,
    src_long float not null,
    dest_lat float not null,
    dest_long float not null,
    depart_time long not null,
    arrive_time long not null,
    total_seats int not null,
    cost float not null
);
CREATE INDEX sorted_slat ON rides(src_lat);
CREATE INDEX sorted_slong ON rides(src_long);
CREATE INDEX sorted_dlat ON rides(dest_lat);
CREATE INDEX sorted_dlong ON rides(dest_long);
CREATE INDEX depart_time ON rides(depart_time);
drop table if exists passengers;
create table passengers (
    id integer unique primary key autoincrement,
    ride_id integer not null,
    passenger_id integer not null,
    unique(ride_id, passenger_id)
);