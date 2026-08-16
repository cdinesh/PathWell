import { z } from "zod";

export const signupSchema = z.object({
  full_name: z.string().min(2, "Enter your full name"),
  email: z.email("Enter a valid email"),
  phone: z.string().regex(/^\+?[0-9 ()-]{7,20}$/, "Enter a valid phone number"),
  date_of_birth: z.string().min(1, "Date of birth is required"),
  password: z.string().min(10, "Use at least 10 characters").regex(/[A-Z]/, "Add an uppercase letter").regex(/[a-z]/, "Add a lowercase letter").regex(/[0-9]/, "Add a number"),
  confirm: z.string(),
  terms_accepted: z.literal(true, { error: "Accept the terms to continue" }),
}).refine(data => data.password === data.confirm, { path: ["confirm"], message: "Passwords do not match" });

export const allowedTypes = ["application/pdf", "image/jpeg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
export function validateFile(file: Pick<File, "type" | "size">): string | null {
  if (!allowedTypes.includes(file.type)) return "Use PDF, JPG, PNG, or DOCX";
  if (file.size > 10 * 1024 * 1024) return "Files must be 10 MB or smaller";
  return null;
}
