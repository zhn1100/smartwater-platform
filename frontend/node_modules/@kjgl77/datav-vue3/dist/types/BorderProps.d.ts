import { ExtractPropTypes, PropType } from 'vue';

export declare const borderBoxProps: {
    color: {
        type: PropType<Array<string>>;
        default: () => never[];
    };
    backgroundColor: {
        type: StringConstructor;
        default: string;
    };
};
export type BorderBoxProps = ExtractPropTypes<typeof borderBoxProps>;
