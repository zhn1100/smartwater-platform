import { ExtractPropTypes } from 'vue';

declare const borderBox8Props: {
    reverse: {
        type: BooleanConstructor;
        default: boolean;
    };
    dur: {
        type: NumberConstructor;
        default: number;
    };
    color: {
        type: PropType<Array<string>>;
        default: () => never[];
    };
    backgroundColor: {
        type: StringConstructor;
        default: string;
    };
};
export type BorderBox8Props = ExtractPropTypes<typeof borderBox8Props>;
declare const _default: import('vue').DefineComponent<{
    reverse: boolean;
    color: string[];
    dur: number;
    backgroundColor: string;
}, {
    width: globalThis.Ref<number, number>;
    height: globalThis.Ref<number, number>;
    initWH: (resize?: boolean) => Promise<unknown>;
    state: {
        path: string;
        gradient: string;
        mask: string;
    };
    mergedColor: globalThis.ComputedRef<string[]>;
    pathD: globalThis.ComputedRef<string>;
    length: globalThis.ComputedRef<number>;
    borderBox8: globalThis.Ref<HTMLElement | null, HTMLElement | null>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{
    reverse: boolean;
    color: string[];
    dur: number;
    backgroundColor: string;
}> & Readonly<{}>, {
    reverse: boolean;
    color: string[];
    dur: number;
    backgroundColor: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
