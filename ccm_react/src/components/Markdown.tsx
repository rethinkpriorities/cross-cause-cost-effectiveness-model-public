import { ComponentProps } from "react";
import { default as ReactMarkdown } from "react-markdown";

export default function Markdown(props: ComponentProps<typeof ReactMarkdown>) {
  return (
    <ReactMarkdown className="prose" {...props}>
      {props.children}
    </ReactMarkdown>
  );
}
