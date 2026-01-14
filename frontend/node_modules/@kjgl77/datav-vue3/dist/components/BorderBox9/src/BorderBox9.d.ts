
declare const _default: import('vue').DefineComponent<{
    color: string[];
    backgroundColor: string;
}, {
    width: globalThis.Ref<number, number>;
    height: globalThis.Ref<number, number>;
    initWH: (resize?: boolean) => Promise<unknown>;
    state: {
        gradientId: string;
        maskId: string;
    };
    mergedColor: globalThis.ComputedRef<string[]>;
    borderBox9: globalThis.Ref<HTMLElement | null, HTMLElement | null>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{
    color: string[];
    backgroundColor: string;
}> & Readonly<{}>, {
    color: string[];
    backgroundColor: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
