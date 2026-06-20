import {
  accountItemActiveStyles,
  accountItemStyles,
  accountNameActiveStyles,
  accountNameStyles,
  accountPasswordStyles,
  accountsLabelStyles,
  accountsStyles,
} from "./AccountList.styles";

interface Account {
  username: string;
  password: string;
}

interface AccountListProps {
  accounts: Account[];
  selectedUsername?: string;
  onSelect: (username: string, password: string) => void;
  label?: string;
}

export function AccountList({
  accounts,
  selectedUsername,
  onSelect,
  label = "テスト用アカウント",
}: AccountListProps) {
  return (
    <div className={accountsStyles}>
      <p className={accountsLabelStyles}>{label}</p>
      {accounts.map((a) => {
        const isActive = selectedUsername === a.username;
        return (
          <button
            key={a.username}
            type="button"
            className={`${accountItemStyles} ${isActive ? accountItemActiveStyles : ""}`.trim()}
            aria-pressed={isActive}
            onClick={() => onSelect(a.username, a.password)}
          >
            <span
              className={`${accountNameStyles} ${isActive ? accountNameActiveStyles : ""}`.trim()}
            >
              {a.username}
            </span>
            <span className={accountPasswordStyles}>{a.password}</span>
          </button>
        );
      })}
    </div>
  );
}
