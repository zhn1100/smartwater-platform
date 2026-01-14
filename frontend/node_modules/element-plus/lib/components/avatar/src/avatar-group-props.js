'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var core = require('@popperjs/core');
var avatar = require('./avatar.js');
var runtime = require('../../../utils/vue/props/runtime.js');
var content = require('../../tooltip/src/content.js');

const avatarGroupProps = runtime.buildProps({
  size: avatar.avatarProps.size,
  shape: avatar.avatarProps.shape,
  collapseAvatars: Boolean,
  collapseAvatarsTooltip: Boolean,
  maxCollapseAvatars: {
    type: Number,
    default: 1
  },
  effect: {
    type: runtime.definePropType(String),
    default: "light"
  },
  placement: {
    type: runtime.definePropType(String),
    values: core.placements,
    default: "top"
  },
  popperClass: content.useTooltipContentProps.popperClass,
  popperStyle: content.useTooltipContentProps.popperStyle,
  collapseClass: String,
  collapseStyle: {
    type: runtime.definePropType([String, Array, Object])
  }
});

exports.avatarGroupProps = avatarGroupProps;
//# sourceMappingURL=avatar-group-props.js.map
