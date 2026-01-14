import { ExtractPropTypes } from 'vue';

declare const borderBox4Props: {
    reverse: {
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
export type BorderBox4Props = ExtractPropTypes<typeof borderBox4Props>;
declare const _default: import('vue').DefineComponent<{
    reverse: boolean;
    color: string[];
    backgroundColor: string;
}, {
    width: globalThis.Ref<number, number>;
    height: globalThis.Ref<number, number>;
    initWH: (resize?: boolean) => Promise<unknown>;
    mergedColor: globalThis.ComputedRef<string[]>;
    borderBox4: globalThis.Ref<HTMLElement | null, HTMLElement | null>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{
    reverse: boolean;
    color: string[];
    backgroundColor: string;
}> & Readonly<{}>, {
    reverse: boolean;
    color: string[];
    backgroundColor: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
