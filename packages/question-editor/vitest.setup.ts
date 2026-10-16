import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());

// ProseMirror measures layout when it scrolls a selection into view; jsdom has no layout.
const emptyRects = () => ({ length: 0, item: () => null, [Symbol.iterator]: function* () {} }) as unknown as DOMRectList;
const zeroRect = () => ({ x: 0, y: 0, top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0, toJSON: () => ({}) }) as DOMRect;
Range.prototype.getClientRects = emptyRects;
Range.prototype.getBoundingClientRect = zeroRect;
Element.prototype.getClientRects = emptyRects;
Element.prototype.scrollIntoView = () => {};
document.elementFromPoint = () => null;
