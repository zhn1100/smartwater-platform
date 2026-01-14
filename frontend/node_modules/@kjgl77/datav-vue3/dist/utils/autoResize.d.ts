import { Ref } from 'vue';

declare function autoResize(dom: Ref<HTMLElement | null>, onResize?: () => void, afterAutoResizeMixinInit?: () => void): {
    width: Ref<number, number>;
    height: Ref<number, number>;
    initWH: (resize?: boolean) => Promise<unknown>;
};
export default autoResize;
