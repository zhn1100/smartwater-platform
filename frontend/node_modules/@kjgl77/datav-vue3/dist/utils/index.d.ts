import { Point } from '../types';

export declare function randomExtend(minNum: number, maxNum: number): number;
export declare function debounce<T>(delay: number, callback: (...args: T[]) => void, vm: T): () => void;
export declare function observerDomResize(dom: HTMLElement, callback: () => void): MutationObserver;
export declare function getPointDistance(pointOne: number[], pointTwo: number[]): number;
/**
 * @description Get the coordinates of the specified radian on the circle
 * @param {number} x      Circle x coordinate
 * @param {number} y      Circle y coordinate
 * @param {number} radius Circle radius
 * @param {number} radian Specfied radian
 * @return {Array} Postion of point
 */
export declare function getCircleRadianPoint(x: number, y: number, radius: number, radian: number): number[];
export declare function getPolylineLength(points: Array<Point>): number;
export declare function PointsToString(points: Array<Point>): string;
export declare function uuid(hasHyphen?: boolean): string;
export declare function deepMerge(target: any, merged: any): any;
/**
 * @description Clone an object or array
 * @param {object | Array} object Cloned object
 * @param {boolean} recursion   Whether to use recursive cloning
 * @return {object | Array} Clone object
 */
export declare function deepClone(object: any, recursion: boolean): any;
