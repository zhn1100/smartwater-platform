import { ExtractPropTypes } from 'vue';

declare const borderBox11Props: {
    title: {
        type: StringConstructor;
        default: string;
    };
    titleWidth: {
        type: NumberConstructor;
        default: number;
    };
    animate: {
        type: BooleanConstructor;
        default: boolean;
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
export type BorderBox11Props = ExtractPropTypes<typeof borderBox11Props>;
declare const _default: import('vue').DefineComponent<{
    title: string;
    animate: boolean;
    color: string[];
    backgroundColor: string;
    titleWidth: number;
}, {
    width: globalThis.Ref<number, number>;
    height: globalThis.Ref<number, number>;
    initWH: (resize?: boolean) => Promise<unknown>;
    filterId: globalThis.Ref<string, string>;
    mergedColor: globalThis.ComputedRef<string[]>;
    borderBox11: globalThis.Ref<null, null>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{
    title: string;
    animate: boolean;
    color: string[];
    backgroundColor: string;
    titleWidth: number;
}> & Readonly<{}>, {
    title: string;
    animate: boolean;
    color: string[];
    backgroundColor: string;
    titleWidth: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
