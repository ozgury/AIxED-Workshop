import ReactMarkdown from "react-markdown";

interface Props {
  text: string;
}

export function SummaryDisplay({ text }: Props) {
  return (
    <div className="prose prose-sm max-w-none rounded-lg border border-gray-200 bg-white p-6">
      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  );
}
