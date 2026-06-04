import { NextResponse } from "next/server";
import {
  REFRESH_COOKIE,
  REFRESH_COOKIE_OPTIONS,
  SESSION_COOKIE,
  SESSION_COOKIE_OPTIONS,
} from "@/lib/server/session";

export async function POST() {
  const response = NextResponse.json({ success: true });
  response.cookies.set(SESSION_COOKIE, "", {
    ...SESSION_COOKIE_OPTIONS,
    maxAge: 0,
  });
  response.cookies.set(REFRESH_COOKIE, "", {
    ...REFRESH_COOKIE_OPTIONS,
    maxAge: 0,
  });
  return response;
}
