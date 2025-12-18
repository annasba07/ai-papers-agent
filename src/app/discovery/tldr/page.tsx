import { redirect } from "next/navigation";

export default function TLDRRedirect() {
  redirect("/discovery?tab=tldr");
}
