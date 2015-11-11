drop table if exists ip_logger;
    create table ip_logger (
    id integer primary key autoincrement,
    ip_address text not null,
    timestamp text not null
);

drop table if exists phone_number_logger;
    create table phone_number_logger(
    id integer primary key autoincrement,
    phone_number text not null,
    timestamp text not null
);

drop table if exists address_logger;
    create table address_logger(
    id integer primary key autoincrement,
    lat text not null,
    long text not null,
    timestamp text not null
);

drop table if exists backpage_logger;
     create table backpage_logger(
     id integer primary key autoincrement,
     text_body text,
     text_headline text,
     link text,
     case_number text,
     timestamp text,
     photos text,
     language text,
     polarity float,
     translated_body text,
     translated_title text,
     subjectivity float,
     posted_at text,
     is_trafficking boolean,
     phone_number text
);

drop table if exists keywords;
     create table keywords(
     id integer primary key autoincrement,
     keyword text not null
);
          
	  
