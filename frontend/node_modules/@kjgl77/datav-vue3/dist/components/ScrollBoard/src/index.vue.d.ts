declare const _default: import('vue').DefineComponent<{}, {
    updateRows: typeof updateRows;
    $emit: (event: "click" | "mouseover" | "getFirstRow", ...args: any[]) => void;
    config: Record<string, any>;
    $props: {
        readonly config?: Record<string, any> | undefined;
    };
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<{}> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
declare function updateRows(rows: any, animationIndex: any): void;
