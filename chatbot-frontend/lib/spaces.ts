export type Space = {
  id: string;
  name: string;
  description: string;
};

export const SPACES: Space[] = [
  { id: "general", name: "General", description: "General assistant with RAG" },
  { id: "coding", name: "Coding", description: "Programming-focused assistant" },
  { id: "docs_only", name: "Docs Only", description: "Answers strictly from documents" },
  { id: "chatgpt", name: "ChatGPT-like", description: "Ignore docs, general chat" },
  { id: "summarizer", name: "Summarizer", description: "Summarize document content" },
];