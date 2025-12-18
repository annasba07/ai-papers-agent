import { redirect } from "next/navigation";

export default function LearningPathRedirect() {
  redirect("/discovery?tab=learning-path");
}
