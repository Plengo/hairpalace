"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import toast from "react-hot-toast";
import { Loader2 } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", phone: "" });
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await authApi.register(form);
      toast.success("Account created — please sign in");
      router.push("/login");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg ?? "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-brand-black flex items-center justify-center px-6">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Link href="/" className="font-serif text-3xl tracking-[0.2em] text-brand-cream hover:text-brand-gold transition-colors">
            STRANDS
          </Link>
          <p className="mt-3 text-sm text-brand-muted">Create your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 bg-brand-card border border-brand-border p-8">
          {[
            { key: "full_name", label: "Full Name",       type: "text",     placeholder: "Jane Doe",         required: true  },
            { key: "email",     label: "Email",           type: "email",    placeholder: "you@example.com",  required: true  },
            { key: "password",  label: "Password",        type: "password", placeholder: "Min 8 characters", required: true  },
            { key: "phone",     label: "Phone (optional)",type: "tel",      placeholder: "+27 82 000 0000",  required: false },
          ].map(({ key, label, type, placeholder, required }) => (
            <div key={key}>
              <label className="block text-xs tracking-widest text-brand-muted uppercase mb-1.5">{label}</label>
              <input
                required={required}
                type={type}
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                placeholder={placeholder}
                className="w-full bg-brand-black border border-brand-border px-4 py-3 text-sm text-brand-cream placeholder:text-brand-muted/40 focus:outline-none focus:border-brand-gold transition-colors"
              />
            </div>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-4 bg-brand-gold text-brand-black text-sm font-semibold tracking-widest uppercase hover:bg-brand-cream transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading && <Loader2 size={16} className="animate-spin" />}
            Create Account
          </button>

          <p className="text-center text-xs text-brand-muted pt-2">
            By registering you agree to our{" "}
            <Link href="/terms" className="text-brand-gold hover:underline">Terms of Service</Link>{" "}
            and{" "}
            <Link href="/privacy" className="text-brand-gold hover:underline">Privacy Policy</Link>.
          </p>

          <p className="text-center text-xs text-brand-muted">
            Already have an account?{" "}
            <Link href="/login" className="text-brand-gold hover:underline">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
