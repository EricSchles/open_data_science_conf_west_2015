drop table if exists investigation_logger;
    create table investigation_logger(
    id integer primary key autoincrement,
    investigation_id text not null,
    timestamp text not null
);

          
	  
