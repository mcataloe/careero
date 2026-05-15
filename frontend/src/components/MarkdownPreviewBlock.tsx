import { Code, List, Stack, Text, Title } from "@mantine/core";
import type { ReactNode } from "react";

type MarkdownBlock =
  | { type: "heading"; level: 1 | 2 | 3; text: string }
  | { type: "paragraph"; lines: string[] }
  | { type: "unorderedList"; items: string[] }
  | { type: "orderedList"; items: string[] }
  | { type: "code"; lines: string[] };

export function MarkdownPreviewBlock({
  value,
  empty = "No content recorded.",
}: {
  value: string | null | undefined;
  empty?: string;
}) {
  const blocks = parseMarkdownish(value ?? "");

  if (blocks.length === 0) {
    return (
      <Text c="dimmed" fs="italic">
        {empty}
      </Text>
    );
  }

  return (
    <Stack gap="xs" className="markdown-preview-block">
      {blocks.map((block, index) => renderBlock(block, index))}
    </Stack>
  );
}

function renderBlock(block: MarkdownBlock, index: number): ReactNode {
  if (block.type === "heading") {
    const order = Math.min(block.level + 2, 5) as 3 | 4 | 5;
    return (
      <Title key={`heading-${index}`} order={order}>
        {block.text}
      </Title>
    );
  }

  if (block.type === "unorderedList" || block.type === "orderedList") {
    return (
      <List
        key={`${block.type}-${index}`}
        type={block.type === "orderedList" ? "ordered" : "unordered"}
        spacing={4}
        size="sm"
      >
        {block.items.map((item, itemIndex) => (
          <List.Item key={`${item}-${itemIndex}`}>{item}</List.Item>
        ))}
      </List>
    );
  }

  if (block.type === "code") {
    return (
      <Code key={`code-${index}`} block>
        {block.lines.join("\n")}
      </Code>
    );
  }

  return (
    <Text key={`paragraph-${index}`} style={{ whiteSpace: "pre-wrap" }}>
      {block.lines.join("\n")}
    </Text>
  );
}

function parseMarkdownish(value: string): MarkdownBlock[] {
  const lines = value.replace(/\r\n/g, "\n").split("\n");
  const blocks: MarkdownBlock[] = [];
  let paragraph: string[] = [];
  let listItems: string[] = [];
  let listType: "unorderedList" | "orderedList" | null = null;
  let codeLines: string[] = [];
  let inCode = false;

  function flushParagraph() {
    if (paragraph.length > 0) {
      blocks.push({ type: "paragraph", lines: paragraph });
      paragraph = [];
    }
  }

  function flushList() {
    if (listType && listItems.length > 0) {
      blocks.push({ type: listType, items: listItems });
      listItems = [];
      listType = null;
    }
  }

  for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed.startsWith("```")) {
      flushParagraph();
      flushList();
      if (inCode) {
        blocks.push({ type: "code", lines: codeLines });
        codeLines = [];
        inCode = false;
      } else {
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    const headingMatch = /^(#{1,3})\s+(.+)$/.exec(trimmed);
    if (headingMatch) {
      flushParagraph();
      flushList();
      blocks.push({
        type: "heading",
        level: headingMatch[1].length as 1 | 2 | 3,
        text: headingMatch[2],
      });
      continue;
    }

    const unorderedMatch = /^[-*+]\s+(.+)$/.exec(trimmed);
    if (unorderedMatch) {
      flushParagraph();
      if (listType !== "unorderedList") {
        flushList();
        listType = "unorderedList";
      }
      listItems.push(unorderedMatch[1]);
      continue;
    }

    const orderedMatch = /^\d+\.\s+(.+)$/.exec(trimmed);
    if (orderedMatch) {
      flushParagraph();
      if (listType !== "orderedList") {
        flushList();
        listType = "orderedList";
      }
      listItems.push(orderedMatch[1]);
      continue;
    }

    flushList();
    paragraph.push(line);
  }

  if (inCode) {
    blocks.push({ type: "code", lines: codeLines });
  }
  flushParagraph();
  flushList();
  return blocks;
}
