import { expect, it } from "vitest";
import { availableActions } from "@/lib/decisions";

it("a reviewer can submit a draft", () => {
  expect(availableActions("draft", ["reviewer"], false)).toEqual([{ id: "submit", label: "Submit for review" }]);
});
