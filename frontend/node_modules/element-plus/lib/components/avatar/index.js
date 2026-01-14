'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var avatar$1 = require('./src/avatar2.js');
var avatarGroup = require('./src/avatar-group.js');
var avatar = require('./src/avatar.js');
var constants = require('./src/constants.js');
var avatarGroupProps = require('./src/avatar-group-props.js');
var install = require('../../utils/vue/install.js');

const ElAvatar = install.withInstall(avatar$1["default"], {
  AvatarGroup: avatarGroup["default"]
});
const ElAvatarGroup = install.withNoopInstall(avatarGroup["default"]);

exports.avatarEmits = avatar.avatarEmits;
exports.avatarProps = avatar.avatarProps;
exports.avatarGroupContextKey = constants.avatarGroupContextKey;
exports.avatarGroupProps = avatarGroupProps.avatarGroupProps;
exports.ElAvatar = ElAvatar;
exports.ElAvatarGroup = ElAvatarGroup;
exports["default"] = ElAvatar;
//# sourceMappingURL=index.js.map
