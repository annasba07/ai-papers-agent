import { redirect } from "next/navigation";

export default function RisingRedirect() {
  redirect("/discovery?tab=rising");
}
