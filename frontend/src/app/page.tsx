import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { LoginFormContainer } from "@/features/auth/components/LoginFormContainer";
import {
  decryptSession,
  REFRESH_COOKIE,
  SESSION_COOKIE,
} from "@/lib/server/session";

export default async function Home() {
  const cookieStore = await cookies();

  const sessionCookie = cookieStore.get(SESSION_COOKIE);
  if (sessionCookie) {
    const token = await decryptSession(sessionCookie.value);
    if (token) redirect("/workspace");
  }

  if (cookieStore.get(REFRESH_COOKIE)) {
    redirect("/workspace");
  }

  return (
    <main>
      <LoginFormContainer />
    </main>
  );
}
