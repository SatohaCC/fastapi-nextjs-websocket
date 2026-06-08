import {
  mentionAvatarStyles,
  mentionDropdownStyles,
  mentionHandleStyles,
  mentionItemFocusedStyles,
  mentionItemStyles,
  mentionUserInfoStyles,
  mentionUsernameStyles,
} from "./MentionDropdown.styles";

interface MentionDropdownProps {
  suggestions: string[];
  focusedIndex: number;
  onSelect: (username: string) => void;
}

export function MentionDropdown({
  suggestions,
  focusedIndex,
  onSelect,
}: MentionDropdownProps) {
  return (
    <div className={mentionDropdownStyles}>
      {suggestions.map((u, i) => (
        <button
          key={u}
          type="button"
          className={`${mentionItemStyles} ${
            i === focusedIndex ? mentionItemFocusedStyles : ""
          }`}
          onMouseDown={(e) => {
            e.preventDefault();
            onSelect(u);
          }}
        >
          <span className={mentionAvatarStyles} aria-hidden="true">
            {u[0]}
          </span>
          <span className={mentionUserInfoStyles}>
            <span className={mentionUsernameStyles}>{u}</span>
            <span className={mentionHandleStyles}>@{u}</span>
          </span>
        </button>
      ))}
    </div>
  );
}
