/*
 Navicat Premium Data Transfer

 Source Server         : hhsrc_v3
 Source Server Type    : MySQL
 Source Server Version : 80021
 Source Host           : localhost:3306
 Source Schema         : hhsrc

 Target Server Type    : MySQL
 Target Server Version : 80021
 File Encoding         : 65001

 Date: 04/02/2021 12:55:33
*/
SET GLOBAL sort_buffer_size = 1024*1024;

USE mysql;
UPDATE user SET plugin='mysql_native_password' WHERE User='root';
update mysql.user set authentication_string=password('root') where user='root' and Host = 'localhost';
flush privileges;

CREATE DATABASE hhsrc;
USE hhsrc;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for hhsrc_blacklist
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_blacklist`;
CREATE TABLE `hhsrc_blacklist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `black_name` varchar(128) DEFAULT NULL,
  `black_time` varchar(128) DEFAULT NULL,
  `black_target` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `black_name` (`black_name`),
  UNIQUE KEY `black_name_2` (`black_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_blacklist
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_commonconfig
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_commonconfig`;
CREATE TABLE `hhsrc_commonconfig` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_server` varchar(128) DEFAULT NULL,
  `config_count` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_commonconfig
-- ----------------------------
BEGIN;
INSERT INTO `hhsrc_commonconfig` VALUES (1, 'None', 1);
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_cornjob
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_cornjob`;
CREATE TABLE `hhsrc_cornjob` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cornjob_name` varchar(20) DEFAULT NULL,
  `cornjob_time` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_cornjob
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_dirb
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_dirb`;
CREATE TABLE `hhsrc_dirb` (
  `id` int NOT NULL AUTO_INCREMENT,
  `dir_base` varchar(128) DEFAULT NULL,
  `dir_path` varchar(128) DEFAULT NULL,
  `dir_status` varchar(128) DEFAULT NULL,
  `dir_length` varchar(128) DEFAULT NULL,
  `dir_title` varchar(128) DEFAULT NULL,
  `dir_time` varchar(128) DEFAULT NULL,
  `dir_http` int DEFAULT NULL,
  `dir_target` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dir_base` (`dir_base`),
  UNIQUE KEY `dir_base_2` (`dir_base`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_dirb
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_domain
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_domain`;
CREATE TABLE `hhsrc_domain` (
  `id` int NOT NULL AUTO_INCREMENT,
  `domain_name` varchar(128) DEFAULT NULL,
  `domain_subdomain_status` tinyint(1) DEFAULT NULL,
  `domain_time` varchar(128) DEFAULT NULL,
  `domain_target` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `domain_name` (`domain_name`),
  UNIQUE KEY `domain_name_2` (`domain_name`),
  CONSTRAINT `hhsrc_domain_chk_1` CHECK ((`domain_subdomain_status` in (0,1))),
  CONSTRAINT `hhsrc_domain_chk_2` CHECK ((`domain_subdomain_status` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_domain
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_http
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_http`;
CREATE TABLE `hhsrc_http` (
  `id` int NOT NULL AUTO_INCREMENT,
  `http_schema` varchar(128) DEFAULT NULL,
  `http_name` varchar(128) DEFAULT NULL,
  `http_title` varchar(128) DEFAULT NULL,
  `http_status` varchar(128) DEFAULT NULL,
  `http_length` varchar(128) DEFAULT NULL,
  `http_screen` longtext,
  `http_dirb_status` tinyint(1) DEFAULT NULL,
  `http_vuln_status` tinyint(1) DEFAULT NULL,
  `http_time` varchar(128) DEFAULT NULL,
  `http_target` int DEFAULT NULL,
  `http_see` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `http_name` (`http_name`),
  UNIQUE KEY `http_name_2` (`http_name`),
  CONSTRAINT `hhsrc_http_chk_1` CHECK ((`http_dirb_status` in (0,1))),
  CONSTRAINT `hhsrc_http_chk_2` CHECK ((`http_vuln_status` in (0,1))),
  CONSTRAINT `hhsrc_http_chk_3` CHECK ((`http_dirb_status` in (0,1))),
  CONSTRAINT `hhsrc_http_chk_4` CHECK ((`http_vuln_status` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_http
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_port
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_port`;
CREATE TABLE `hhsrc_port` (
  `id` int NOT NULL AUTO_INCREMENT,
  `port_domain` varchar(128) DEFAULT NULL,
  `port_ip` varchar(128) DEFAULT NULL,
  `port_port` varchar(128) DEFAULT NULL,
  `port_server` varchar(128) DEFAULT NULL,
  `port_http_status` tinyint(1) DEFAULT NULL,
  `port_time` varchar(128) DEFAULT NULL,
  `port_target` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `hhsrc_port_chk_1` CHECK ((`port_http_status` in (0,1))),
  CONSTRAINT `hhsrc_port_chk_2` CHECK ((`port_http_status` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_port
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_scancorn
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_scancorn`;
CREATE TABLE `hhsrc_scancorn` (
  `id` int NOT NULL AUTO_INCREMENT,
  `scancorn_name` varchar(20) DEFAULT NULL,
  `scancorn_month` varchar(20) DEFAULT NULL,
  `scancorn_week` varchar(20) DEFAULT NULL,
  `scancorn_day` varchar(20) DEFAULT NULL,
  `scancorn_hour` varchar(20) DEFAULT NULL,
  `scancorn_min` varchar(20) DEFAULT NULL,
  `scancorn_time` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_scancorn
-- ----------------------------
BEGIN;
INSERT INTO `hhsrc_scancorn` VALUES (1, 'default', '*', '1', '*', '0', '0', '2021-02-24  17:00:07');
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_scanmethod
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_scanmethod`;
CREATE TABLE `hhsrc_scanmethod` (
  `id` int NOT NULL AUTO_INCREMENT,
  `scanmethod_name` varchar(128) DEFAULT NULL,
  `scanmethod_subdomain` tinyint(1) DEFAULT NULL,
  `scanmethod_port` tinyint(1) DEFAULT NULL,
  `scanmethod_port_portlist` varchar(128) DEFAULT NULL,
  `scanmethod_url` tinyint(1) DEFAULT NULL,
  `scanmethod_dirb` tinyint(1) DEFAULT NULL,
  `scanmethod_dirb_wordlist` varchar(128) DEFAULT NULL,
  `scanmethod_vuln` tinyint(1) DEFAULT NULL,
  `scanmethod_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `hhsrc_scanmethod_chk_1` CHECK ((`scanmethod_subdomain` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_10` CHECK ((`scanmethod_vuln` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_2` CHECK ((`scanmethod_port` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_3` CHECK ((`scanmethod_url` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_4` CHECK ((`scanmethod_dirb` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_5` CHECK ((`scanmethod_vuln` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_6` CHECK ((`scanmethod_subdomain` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_7` CHECK ((`scanmethod_port` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_8` CHECK ((`scanmethod_url` in (0,1))),
  CONSTRAINT `hhsrc_scanmethod_chk_9` CHECK ((`scanmethod_dirb` in (0,1)))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_scanmethod
-- ----------------------------
BEGIN;
INSERT INTO `hhsrc_scanmethod` VALUES (1, 'default', 1, 1, 'top100', 1, 0, 'top1000', 0, '2021-02-24  16:59:58');
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_subdomain
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_subdomain`;
CREATE TABLE `hhsrc_subdomain` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subdomain_name` varchar(128) DEFAULT NULL,
  `subdomain_ip` varchar(128) DEFAULT NULL,
  `subdomain_info` varchar(128) DEFAULT NULL,
  `subdomain_port_status` tinyint(1) DEFAULT NULL,
  `subdomain_http_status` tinyint(1) DEFAULT NULL,
  `subdomain_time` varchar(128) DEFAULT NULL,
  `subdomain_target` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subdomain_name` (`subdomain_name`),
  UNIQUE KEY `subdomain_name_2` (`subdomain_name`),
  CONSTRAINT `hhsrc_subdomain_chk_1` CHECK ((`subdomain_port_status` in (0,1))),
  CONSTRAINT `hhsrc_subdomain_chk_2` CHECK ((`subdomain_http_status` in (0,1))),
  CONSTRAINT `hhsrc_subdomain_chk_3` CHECK ((`subdomain_port_status` in (0,1))),
  CONSTRAINT `hhsrc_subdomain_chk_4` CHECK ((`subdomain_http_status` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_subdomain
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_target
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_target`;
CREATE TABLE `hhsrc_target` (
  `id` int NOT NULL AUTO_INCREMENT,
  `target_name` varchar(128) DEFAULT NULL,
  `target_description` varchar(128) DEFAULT NULL,
  `target_method` varchar(128) DEFAULT NULL,
  `target_level` int DEFAULT NULL,
  `target_corn` tinyint(1) DEFAULT NULL,
  `target_corn_id` varchar(128) DEFAULT NULL,
  `target_status` int DEFAULT NULL,
  `target_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `hhsrc_target_chk_1` CHECK ((`target_corn` in (0,1))),
  CONSTRAINT `hhsrc_target_chk_2` CHECK ((`target_corn` in (0,1)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_target
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_user
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_user`;
CREATE TABLE `hhsrc_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `username_2` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_user
-- ----------------------------
BEGIN;
INSERT INTO `hhsrc_user` VALUES (1, 'admin', 'pbkdf2:sha256:150000$c7P9YSFs$7adc2214bab28233a14211e915dd0ee90d2715a86970988a69b624cb8ef06c1f');
COMMIT;

-- ----------------------------
-- Table structure for hhsrc_vuln
-- ----------------------------
DROP TABLE IF EXISTS `hhsrc_vuln`;
CREATE TABLE `hhsrc_vuln` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vuln_mainkey` varchar(128) DEFAULT NULL,
  `vuln_name` varchar(128) DEFAULT NULL,
  `vuln_info` varchar(128) DEFAULT NULL,
  `vuln_level` varchar(128) DEFAULT NULL,
  `vuln_path` longtext,
  `vuln_http` varchar(128) DEFAULT NULL,
  `vuln_target` int DEFAULT NULL,
  `vuln_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vuln_mainkey` (`vuln_mainkey`),
  UNIQUE KEY `vuln_mainkey_2` (`vuln_mainkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of hhsrc_vuln
-- ----------------------------
BEGIN;
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
