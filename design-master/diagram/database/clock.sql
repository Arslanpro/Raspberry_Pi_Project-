/*
 Navicat Premium Data Transfer

 Source Server         : p5
 Source Server Type    : MySQL
 Source Server Version : 100323
 Source Host           : 192.168.137.6:3306
 Source Schema         : clock

 Target Server Type    : MySQL
 Target Server Version : 100323
 File Encoding         : 65001

 Date: 08/10/2020 00:42:51
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alarm
-- ----------------------------
DROP TABLE IF EXISTS `alarm`;
CREATE TABLE `alarm`  (
  `current_time` datetime(6) NOT NULL,
  `alarm_time` datetime(6) NOT NULL,
  `time_range` int NOT NULL,
  `snooze_time` int NOT NULL,
  `current_date` datetime(6) NOT NULL,
  `aid` int NOT NULL AUTO_INCREMENT,
  `auid` int NOT NULL,
  PRIMARY KEY (`aid`) USING BTREE,
  INDEX `auid`(`auid`) USING BTREE,
  CONSTRAINT `alarm_ibfk_1` FOREIGN KEY (`auid`) REFERENCES `person` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alarm
-- ----------------------------

-- ----------------------------
-- Table structure for collection
-- ----------------------------
DROP TABLE IF EXISTS `collection`;
CREATE TABLE `collection`  (
  `gx` double(32, 10) NULL DEFAULT NULL,
  `gy` double(32, 10) NULL DEFAULT NULL,
  `gz` double(32, 10) NULL DEFAULT NULL,
  `ax` double(32, 10) NULL DEFAULT NULL,
  `ay` double(32, 10) NULL DEFAULT NULL,
  `az` double(32, 10) NULL DEFAULT NULL,
  `cid` int NOT NULL AUTO_INCREMENT,
  `caid` int NOT NULL,
  PRIMARY KEY (`cid`) USING BTREE,
  INDEX `caid`(`caid`) USING BTREE,
  CONSTRAINT `collection_ibfk_1` FOREIGN KEY (`caid`) REFERENCES `alarm` (`aid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of collection
-- ----------------------------

-- ----------------------------
-- Table structure for person
-- ----------------------------
DROP TABLE IF EXISTS `person`;
CREATE TABLE `person`  (
  `name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `age` int NOT NULL,
  `gender` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `uid` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of person
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
