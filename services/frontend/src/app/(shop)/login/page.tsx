"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import toast from "react-hot-toast";
import { Loader2 } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await authApi.login(form);
      const me = await authApi.me();
      setAuth(res.data.access_token, me.data);
      toast.success(`Welcome back, ${me.data.full_name.split(" ")[0]}`);
      router.push(me.data.is_admin ? "/admin" : "/");
    } catch {
      toast.error("Invalid email or password");
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
          <p className="mt-3 text-sm text-brand-muted">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 bg-brand-card border border-brand-border p-8">
          {[
            { key: "email",    label: "Email",    type: "email",    placeholder: "you@example.com" },
            { key: "password", label: "Password", type: "password", placeholder: "••••••••" },
          ].map(({ key, label, type, placeholder }) => (
            <div key={key}>
              <label className="block text-xs tracking-widest text-brand-muted uppercase mb-1.5">{label}</label>
              <input
                required
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
            Sign In
          </button>

          <p className="text-center text-xs text-brand-muted pt-2">
            New here?{" "}
            <Link href="/register" className="text-brand-gold hover:underline">Create an account</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
