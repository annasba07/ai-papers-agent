import { redirect } from "next/navigation";

export default function ReproducibleRedirect() {
  redirect("/discovery?tab=reproducible");
}
