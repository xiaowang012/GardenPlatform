/*
 Navicat Premium Data Transfer

 Source Server         : mysql_localhost
 Source Server Type    : MySQL
 Source Server Version : 80021
 Source Host           : localhost:3306
 Source Schema         : gardenplatform

 Target Server Type    : MySQL
 Target Server Version : 80021
 File Encoding         : 65001

 Date: 21/03/2022 13:54:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for permission
-- ----------------------------
DROP TABLE IF EXISTS `permission`;
CREATE TABLE `permission`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `url` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `description` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 44 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of permission
-- ----------------------------
INSERT INTO `permission` VALUES (44, 'admin', '/home', '主页');
INSERT INTO `permission` VALUES (45, 'admin', '/update_password', '修改密码');
INSERT INTO `permission` VALUES (46, 'admin', '/my_plant', '我的盆摘');
INSERT INTO `permission` VALUES (47, 'admin', '/my_plant/page', '我的盆摘翻页');
INSERT INTO `permission` VALUES (48, 'admin', '/my_plant/search/page', '我的盆摘查询主页(POST)');
INSERT INTO `permission` VALUES (49, 'admin', '/my_plant/search/page', '我的盆摘查询翻页(GET)');
INSERT INTO `permission` VALUES (50, 'admin', '/my_plant/search/type', '我的盆摘分类查询');
INSERT INTO `permission` VALUES (51, 'admin', '/my_plant/AddDevice', '我的盆摘添加设备');
INSERT INTO `permission` VALUES (52, 'admin', '/my_plant/UpdateDevices', '我的盆摘修改设备');
INSERT INTO `permission` VALUES (53, 'admin', '/my_plant/DeleteDevice', '我的盆摘删除设备');
INSERT INTO `permission` VALUES (54, 'admin', '/my_plant/WateringOperation/start', '我的盆摘开始浇水');
INSERT INTO `permission` VALUES (55, 'admin', '/my_plant/WateringOperation/end', '我的盆摘停止浇水');
INSERT INTO `permission` VALUES (56, 'admin', '/my_plant/AutoWatering', '我的盆摘自动浇水');
INSERT INTO `permission` VALUES (57, 'admin', '/my_plant/ImportDevices', '我的盆摘导入设备');
INSERT INTO `permission` VALUES (58, 'admin', '/my_plant/ImportDevices/DownloadTemplateFile', '我的盆摘下载导入设备模板');
INSERT INTO `permission` VALUES (59, 'admin', '/management/refresh', '刷新权限缓存(全局)');
INSERT INTO `permission` VALUES (60, 'admin', '/my_friends', '朋友圈');
INSERT INTO `permission` VALUES (61, 'admin', '/my_friends/send_message', '朋友圈发动态');
INSERT INTO `permission` VALUES (62, 'admin', '/my_friends/delete_message', '朋友圈删除动态');
INSERT INTO `permission` VALUES (63, 'admin', '/my_friends/nextpage', '朋友圈翻页');
INSERT INTO `permission` VALUES (64, 'admin', '/my_friends/send_message/add_comments', '朋友圈添加评论');
INSERT INTO `permission` VALUES (65, 'admin', '/my_friends/send_message/add_likes', '朋友圈点赞');
INSERT INTO `permission` VALUES (66, 'admin', '/my_friends/send_message/get_likes_list', '朋友圈查看点赞列表');
INSERT INTO `permission` VALUES (67, 'admin', '/my_friends/send_message/delete_comments', '朋友圈删除评论');
INSERT INTO `permission` VALUES (68, 'admin', '/management/permissionTable', '后台管理权限表');
INSERT INTO `permission` VALUES (69, 'admin', '/management/permissionTable/page', '后台管理权限表翻页');
INSERT INTO `permission` VALUES (70, 'admin', '/management/permissionTable/add', '后台管理权限表添加权限');
INSERT INTO `permission` VALUES (71, 'admin', '/management/permissionTable/import', '后台管理权限表导入权限');
INSERT INTO `permission` VALUES (72, 'admin', '/management/permissionTable/update', '后台管理权限表修改权限');
INSERT INTO `permission` VALUES (73, 'admin', '/management/permissionTable/delete', '后台管理权限表删除权限');
INSERT INTO `permission` VALUES (74, 'admin', '/management/userTable', '后台管理用户表');
INSERT INTO `permission` VALUES (75, 'admin', '/management/userTable/page', '后台管理用户表翻页');
INSERT INTO `permission` VALUES (76, 'admin', '/management/userTable/add', '后台管理用户表添加用户');
INSERT INTO `permission` VALUES (77, 'admin', '/management/userTable/import', '后台管理用户表导入用户');
INSERT INTO `permission` VALUES (78, 'admin', '/management/userTable/update', '后台管理用户表修改用户');
INSERT INTO `permission` VALUES (79, 'admin', '/management/userTable/delete', '后台管理用户表删除用户');
INSERT INTO `permission` VALUES (80, 'admin', '/management/userTable/import/DownloadTemplateFile', '后台管理用户表下载导入用户模板');
INSERT INTO `permission` VALUES (81, 'admin', '/management/userGroupTable', '后台管理用户组表');
INSERT INTO `permission` VALUES (82, 'admin', '/management/userGroupTable/page', '后台管理用户组表翻页');
INSERT INTO `permission` VALUES (83, 'admin', '/management/userGroupTable/add', '后台管理用户组表添加用户组');
INSERT INTO `permission` VALUES (84, 'admin', '/management/userGroupTable/delete', '后台管理用户组表删除用户组');
INSERT INTO `permission` VALUES (85, 'admin', '/management/userGroupTable/update', '后台管理用户组表修改用户组');
INSERT INTO `permission` VALUES (86, 'admin', '/management/userGroupTable/import', '后台管理用户组表导入用户组');
INSERT INTO `permission` VALUES (87, 'admin', '/management/devicesTable', '后台管理设备表');
INSERT INTO `permission` VALUES (88, 'admin', '/management/devicesTable/page', '后台管理设备表翻页');
INSERT INTO `permission` VALUES (89, 'admin', '/management/devicesTable/add', '后台管理设备表添加设备');
INSERT INTO `permission` VALUES (90, 'admin', '/management/devicesTable/update', '后台管理设备表修改设备');
INSERT INTO `permission` VALUES (91, 'admin', '/management/devicesTable/delete', '后台管理设备表删除设备');
INSERT INTO `permission` VALUES (92, 'admin', '/management/devicesTable/import', '后台管理设备表导入设备');
INSERT INTO `permission` VALUES (93, 'admin', '/management/friendInfoTable', '后台管理朋友动态表');
INSERT INTO `permission` VALUES (94, 'admin', '/management/friendInfoTable/page', '后台管理朋友动态表翻页');
INSERT INTO `permission` VALUES (95, 'admin', '/management/friendInfoTable/add', '后台管理朋友动态表添加动态');
INSERT INTO `permission` VALUES (96, 'admin', '/management/friendInfoTable/update', '后台管理朋友动态表修改动态');
INSERT INTO `permission` VALUES (97, 'admin', '/management/friendInfoTable/delete', '后台管理朋友动态表删除动态');
INSERT INTO `permission` VALUES (98, 'admin', '/management/friendCommentsTable', '后台管理朋友动态评论表');
INSERT INTO `permission` VALUES (99, 'admin', '/management/friendCommentsTable/page', '后台管理朋友动态评论表翻页');
INSERT INTO `permission` VALUES (100, 'admin', '/management/friendCommentsTable/add', '后台管理朋友动态评论表添加评论');
INSERT INTO `permission` VALUES (101, 'admin', '/management/friendCommentsTable/delete', '后台管理朋友动态评论表删除评论');
INSERT INTO `permission` VALUES (102, 'admin', '/management/friendCommentsTable/update', '后台管理朋友动态评论表修改评论');
INSERT INTO `permission` VALUES (103, 'admin', '/management/friendLikesTable', '后台管理朋友动态点赞表');
INSERT INTO `permission` VALUES (104, 'admin', '/management/friendLikesTable/page', '后台管理朋友动态点赞表翻页');
INSERT INTO `permission` VALUES (105, 'admin', '/management/friendLikesTable/add', '后台管理朋友动态点赞表添加点赞数据');
INSERT INTO `permission` VALUES (106, 'admin', '/management/friendLikesTable/delete', '后台管理朋友动态点赞表删除点赞数据');
INSERT INTO `permission` VALUES (107, 'admin', '/management/friendLikesTable/update', '后台管理朋友动态点赞表修改点赞数据');
INSERT INTO `permission` VALUES (108, 'others', '/home', '主页');
INSERT INTO `permission` VALUES (109, 'others', '/update_password', '修改密码');
INSERT INTO `permission` VALUES (110, 'others', '/my_plant', '我的盆摘');
INSERT INTO `permission` VALUES (111, 'others', '/my_plant/page', '我的盆摘翻页');
INSERT INTO `permission` VALUES (112, 'others', '/my_plant/search/page', '我的盆摘查询主页(POST)');
INSERT INTO `permission` VALUES (113, 'others', '/my_plant/search/page', '我的盆摘查询翻页(GET)');
INSERT INTO `permission` VALUES (114, 'others', '/my_plant/search/type', '我的盆摘分类查询');
INSERT INTO `permission` VALUES (115, 'others', '/my_plant/AddDevice', '我的盆摘添加设备');
INSERT INTO `permission` VALUES (116, 'others', '/my_plant/UpdateDevices', '我的盆摘修改设备');
INSERT INTO `permission` VALUES (117, 'others', '/my_plant/DeleteDevice', '我的盆摘删除设备');
INSERT INTO `permission` VALUES (118, 'others', '/my_plant/WateringOperation/start', '我的盆摘开始浇水');
INSERT INTO `permission` VALUES (119, 'others', '/my_plant/WateringOperation/end', '我的盆摘停止浇水');
INSERT INTO `permission` VALUES (120, 'others', '/my_plant/AutoWatering', '我的盆摘自动浇水');
INSERT INTO `permission` VALUES (121, 'others', '/my_plant/ImportDevices', '我的盆摘导入设备');
INSERT INTO `permission` VALUES (122, 'others', '/my_plant/ImportDevices/DownloadTemplateFile', '我的盆摘下载导入设备模板');
INSERT INTO `permission` VALUES (123, 'others', '/my_friends', '朋友圈');
INSERT INTO `permission` VALUES (124, 'others', '/my_friends/send_message', '朋友圈发动态');
INSERT INTO `permission` VALUES (125, 'others', '/my_friends/delete_message', '朋友圈删除动态');
INSERT INTO `permission` VALUES (126, 'others', '/my_friends/nextpage', '朋友圈翻页');
INSERT INTO `permission` VALUES (127, 'others', '/my_friends/send_message/add_comments', '朋友圈添加评论');
INSERT INTO `permission` VALUES (128, 'others', '/my_friends/send_message/add_likes', '朋友圈点赞');
INSERT INTO `permission` VALUES (129, 'others', '/my_friends/send_message/get_likes_list', '朋友圈查看点赞列表');
INSERT INTO `permission` VALUES (130, 'others', '/my_friends/send_message/delete_comments', '朋友圈删除评论');

SET FOREIGN_KEY_CHECKS = 1;
