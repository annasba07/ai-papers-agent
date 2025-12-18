import { redirect } from "next/navigation";

export default function TechniquesRedirect() {
  redirect("/discovery?tab=techniques");
}
