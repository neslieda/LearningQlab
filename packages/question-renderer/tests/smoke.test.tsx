import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import type { Doc } from "@qlab/api-client";
import { DocView } from "../src";

it("renders a document with one paragraph", () => {
  const doc: Doc = {
    type: "doc",
    content: [{ type: "paragraph", content: [{ type: "text", text: "Hello", marks: [] }] }],
  };
  render(<DocView doc={doc} />);
  expect(screen.getByText("Hello")).toBeInTheDocument();
});
