"use client";

import { useState } from "react";
import { useMention } from "./useMention";

interface UseMentionDropdownProps {
  text: string;
  users: string[];
  currentUser: string;
  onTextChange: (value: string) => void;
}

interface UseMentionDropdownReturn {
  isOpen: boolean;
  suggestions: string[];
  focusedIndex: number;
  handleMentionSelect: (username: string) => void;
  handleInputKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  handleInputChange: (value: string) => void;
}

export function useMentionDropdown({
  text,
  users,
  currentUser,
  onTextChange,
}: UseMentionDropdownProps): UseMentionDropdownReturn {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const { mentionQuery, suggestions, insertMention } = useMention({
    text,
    users,
    currentUser,
  });

  const isOpen = mentionQuery !== null && suggestions.length > 0;

  const handleMentionSelect = (username: string) => {
    onTextChange(insertMention(username));
    setFocusedIndex(0);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setFocusedIndex((i) => (i + 1) % suggestions.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setFocusedIndex((i) => (i - 1 + suggestions.length) % suggestions.length);
    } else if (e.key === "Enter") {
      e.preventDefault();
      handleMentionSelect(suggestions[focusedIndex]);
    } else if (e.key === "Escape") {
      onTextChange(text.replace(/@\w*$/, ""));
      setFocusedIndex(0);
    }
  };

  const handleInputChange = (value: string) => {
    onTextChange(value);
    setFocusedIndex(0);
  };

  return {
    isOpen,
    suggestions,
    focusedIndex,
    handleMentionSelect,
    handleInputKeyDown,
    handleInputChange,
  };
}
