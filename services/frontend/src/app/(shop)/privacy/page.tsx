export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-20 space-y-10">
      <div>
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Legal</p>
        <h1 className="font-serif text-4xl text-brand-cream">Privacy Policy</h1>
        <p className="text-xs text-brand-muted mt-2">Last updated: {new Date().toLocaleDateString("en-ZA", { month: "long", year: "numeric" })}</p>
      </div>

      {[
        {
          title: "1. Information We Collect",
          body: "We collect your name, email address, phone number, shipping address, and payment information (processed securely via Stripe — we never store raw card data). We also collect usage data via server logs.",
        },
        {
          title: "2. How We Use Your Information",
          body: "Your information is used to process and fulfil your orders, send order status updates, and improve our service. We do not sell your personal information to third parties.",
        },
        {
          title: "3. Data Storage & Security",
          body: "All personal data is stored on encrypted AWS infrastructure located in the Africa (Cape Town) region. We use industry-standard TLS encryption for all data in transit and AES-256 at rest.",
        },
        {
          title: "4. Third-Party Services",
          body: "We use Stripe for payment processing and AWS for hosting. Both are subject to their own privacy policies. Email Communications are handled via SMTP; we do not use third-party marketing platforms.",
        },
        {
          title: "5. Your Rights (POPIA)",
          body: "Under the Protection of Personal Information Act (POPIA), you have the right to access, correct, or delete your personal information. To exercise these rights, email us at privacy@strands.co.za.",
        },
        {
          title: "6. Cookies",
          body: "We use only essential cookies required for authentication and cart functionality. We do not use tracking or advertising cookies.",
        },
        {
          title: "7. Retention",
          body: "We retain your personal data for as long as your account is active or as required to fulfil outstanding orders. You may request deletion at any time.",
        },
        {
          title: "8. Contact",
          body: "For any privacy-related queries, contact our Information Officer at privacy@strands.co.za.",
        },
      ].map(({ title, body }) => (
        <section key={title} className="space-y-2">
          <h2 className="font-serif text-xl text-brand-cream">{title}</h2>
          <p className="text-sm text-brand-muted leading-7">{body}</p>
        </section>
      ))}
    </div>
  );
}
