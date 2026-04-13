export default function ReturnsPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-20 space-y-10">
      <div>
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Info</p>
        <h1 className="font-serif text-4xl text-brand-cream">Returns & Refunds</h1>
      </div>

      {[
        {
          title: "Pre-Sourcing Cancellations",
          body: "You may cancel your order within 24 hours of placement for a full refund, provided we have not yet begun sourcing. Email support@strands.co.za with your order reference to cancel.",
        },
        {
          title: "Defective or Incorrect Items",
          body: "If you receive a defective, damaged, or incorrect product, please contact us within 5 business days of delivery with photographic evidence. We will arrange a replacement or full refund at no cost to you.",
        },
        {
          title: "Change of Mind",
          body: "Due to the nature of our order-first business (products are sourced specifically for you), we are unable to accept returns for change of mind. Please review your order carefully before confirming payment.",
        },
        {
          title: "Refund Processing",
          body: "Approved refunds are processed via Stripe back to your original payment method. Please allow 5–10 business days for the refund to reflect on your statement.",
        },
        {
          title: "Hygiene Policy",
          body: "For health and safety reasons, opened hair and beauty products (such as hair extensions, wigs, or treatments) cannot be returned unless defective.",
        },
        {
          title: "Contact Us",
          body: "For returns or refund requests, email support@strands.co.za with your order number and a description of the issue. Our team will respond within 1 business day.",
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
