'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var vue = require('vue');
var index$1 = require('../../icon/index.js');
var avatar = require('./avatar.js');
var constants = require('./constants.js');
var pluginVue_exportHelper = require('../../../_virtual/plugin-vue_export-helper.js');
var index = require('../../../hooks/use-namespace/index.js');
var shared = require('@vue/shared');
var types = require('../../../utils/types.js');
var style = require('../../../utils/dom/style.js');

const _hoisted_1 = ["src", "alt", "srcset"];
const _sfc_main = vue.defineComponent({
  ...{
    name: "ElAvatar"
  },
  __name: "avatar",
  props: avatar.avatarProps,
  emits: avatar.avatarEmits,
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const avatarGroupContext = vue.inject(constants.avatarGroupContextKey, void 0);
    const ns = index.useNamespace("avatar");
    const hasLoadError = vue.ref(false);
    const size = vue.computed(() => {
      var _a;
      return (_a = props.size) != null ? _a : avatarGroupContext == null ? void 0 : avatarGroupContext.size;
    });
    const shape = vue.computed(
      () => {
        var _a, _b;
        return (_b = (_a = props.shape) != null ? _a : avatarGroupContext == null ? void 0 : avatarGroupContext.shape) != null ? _b : "circle";
      }
    );
    const avatarClass = vue.computed(() => {
      const { icon } = props;
      const classList = [ns.b()];
      if (shared.isString(size.value))
        classList.push(ns.m(size.value));
      if (icon)
        classList.push(ns.m("icon"));
      if (shape.value)
        classList.push(ns.m(shape.value));
      return classList;
    });
    const sizeStyle = vue.computed(() => {
      return types.isNumber(size.value) ? ns.cssVarBlock({
        size: style.addUnit(size.value)
      }) : void 0;
    });
    const fitStyle = vue.computed(() => ({
      objectFit: props.fit
    }));
    vue.watch(
      () => props.src,
      () => hasLoadError.value = false
    );
    function handleError(e) {
      hasLoadError.value = true;
      emit("error", e);
    }
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(
        "span",
        {
          class: vue.normalizeClass(avatarClass.value),
          style: vue.normalizeStyle(sizeStyle.value)
        },
        [
          (_ctx.src || _ctx.srcSet) && !hasLoadError.value ? (vue.openBlock(), vue.createElementBlock("img", {
            key: 0,
            src: _ctx.src,
            alt: _ctx.alt,
            srcset: _ctx.srcSet,
            style: vue.normalizeStyle(fitStyle.value),
            onError: handleError
          }, null, 44, _hoisted_1)) : _ctx.icon ? (vue.openBlock(), vue.createBlock(vue.unref(index$1.ElIcon), { key: 1 }, {
            default: vue.withCtx(() => [
              (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.icon)))
            ]),
            _: 1
          })) : vue.renderSlot(_ctx.$slots, "default", { key: 2 })
        ],
        6
      );
    };
  }
});
var Avatar = /* @__PURE__ */ pluginVue_exportHelper["default"](_sfc_main, [["__file", "/home/runner/work/element-plus/element-plus/packages/components/avatar/src/avatar.vue"]]);

exports["default"] = Avatar;
//# sourceMappingURL=avatar2.js.map
