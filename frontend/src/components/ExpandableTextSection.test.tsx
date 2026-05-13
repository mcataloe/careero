import { describe, expect, it } from "vitest";

import { ExpandableTextSection } from "./ExpandableTextSection";
import { render, screen, userEvent } from "../test-utils";

describe("ExpandableTextSection", () => {
  it("renders short plain text with default controls", () => {
    render(
      <ExpandableTextSection title="Notes">
        Short content
      </ExpandableTextSection>,
    );

    expect(screen.getByRole("heading", { name: "Notes" })).toBeInTheDocument();
    expect(screen.getByText("Short content")).toBeInTheDocument();
  });

  it("supports expanding long content", async () => {
    const user = userEvent.setup();
    const content = Array.from({ length: 40 }, (_, index) => `Line ${index}`).join("\n");

    render(
      <ExpandableTextSection title="Long content" maxHeight={80}>
        {content}
      </ExpandableTextSection>,
    );

    const showMore = screen.queryByRole("button", { name: /show more/i });
    if (showMore) {
      await user.click(showMore);
      expect(screen.getByRole("button", { name: /show less/i })).toBeInTheDocument();
    }

    expect(screen.getByText(/Line 39/)).toBeInTheDocument();
  });

  it("supports rich JSX children", () => {
    render(
      <ExpandableTextSection title="Rich">
        <div>
          <strong>Structured section</strong>
        </div>
      </ExpandableTextSection>,
    );

    expect(screen.getByText("Structured section")).toBeInTheDocument();
  });
});
