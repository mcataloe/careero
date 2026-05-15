import { describe, expect, it } from "vitest";

import { MarkdownPreviewBlock } from "./MarkdownPreviewBlock";
import { render, screen } from "../test-utils";

describe("MarkdownPreviewBlock", () => {
  it("renders headings", () => {
    render(<MarkdownPreviewBlock value={"# Profile\n## Experience\n### Details"} />);

    expect(screen.getByRole("heading", { name: "Profile" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Experience" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Details" })).toBeInTheDocument();
  });

  it("renders bullet and numbered lists", () => {
    render(
      <MarkdownPreviewBlock
        value={"- Python\n* PostgreSQL\n\n1. First step\n2. Second step"}
      />,
    );

    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("PostgreSQL")).toBeInTheDocument();
    expect(screen.getByText("First step")).toBeInTheDocument();
    expect(screen.getByText("Second step")).toBeInTheDocument();
  });

  it("renders plain paragraphs and fenced code blocks", () => {
    render(
      <MarkdownPreviewBlock
        value={"Paragraph one.\n\nParagraph two.\n\n```\nconst value = 1;\n```"}
      />,
    );

    expect(screen.getByText("Paragraph one.")).toBeInTheDocument();
    expect(screen.getByText("Paragraph two.")).toBeInTheDocument();
    expect(screen.getByText("const value = 1;")).toBeInTheDocument();
  });

  it("renders raw HTML as text", () => {
    const { container } = render(
      <MarkdownPreviewBlock value={'<img src=x onerror="alert(1)">'} />,
    );

    expect(screen.getByText('<img src=x onerror="alert(1)">')).toBeInTheDocument();
    expect(container.querySelector("img")).toBeNull();
  });
});
