import { Button } from "@/components/ui/primitives";
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
          <Button
            key={a.username}
            variant="unstyled"
            size="none"
            className={`${accountItemStyles} ${isActive ? accountItemActiveStyles : ""}`.trim()}
            aria-pressed={isActive ? "true" : "false"}
            onPress={() => onSelect(a.username, a.password)}
          >
            <span
              className={`${accountNameStyles} ${isActive ? accountNameActiveStyles : ""}`.trim()}
            >
              {a.username}
            </span>
            <span className={accountPasswordStyles}>{a.password}</span>
          </Button>
        );
      })}
    </div>
  );
}
