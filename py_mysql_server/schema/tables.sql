create table `mysql_users`(
  user_id int not null AUTO_INCREMENT COMMENT '用户id',
  user_name varchar(30) not null COMMENT '用户名称',
  user_password varchar(20) not null COMMENT '用户密码',
  upt_time datetime not null default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  primary key(user_id),
  unique key(user_name)
)engine=innodb, COMMENT 'user表';

create table `mysql_servers`(
  server_id int not null AUTO_INCREMENT COMMENT 'server id',
  server_host varchar(15) not null,
  server_port int not null DEFAULT 3306,
  server_user varchar(30) not null,
  server_password varchar(20) not null,
  server_charset varchar(20) not null,
  upt_time datetime not null default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  primary key(server_id),
  unique key(server_host,server_port,server_user)
)engine=innodb, COMMENT 'server表';