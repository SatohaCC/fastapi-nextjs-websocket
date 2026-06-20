import { useMemo } from "react";

interface UseMentionProps {
  text: string;
  users: string[];
  currentUser: string;
}

interface UseMentionReturn {
  mentionQuery: string | null;
  suggestions: string[];
  insertMention: (username: string) => string;
}

export function useMention({
  text,
  users,
  currentUser,
}: UseMentionProps): UseMentionReturn {
  const mentionQuery = useMemo(() => {
    const match = text.match(/@(\w*)$/);
    return match ? match[1] : null;
  }, [text]);

  const suggestions = useMemo(() => {
    if (mentionQuery === null) return [];
    const query = mentionQuery.toLowerCase();
    return users
      .filter((u) => u !== currentUser && u.toLowerCase().startsWith(query))
      .slice(0, 5);
  }, [mentionQuery, users, currentUser]);

  const insertMention = (username: string): string => {
    return text.replace(/@\w*$/, `@${username} `);
  };

  return { mentionQuery, suggestions, insertMention };
}
