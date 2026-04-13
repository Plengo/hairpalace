export default function ShippingPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-20 space-y-10">
      <div>
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Info</p>
        <h1 className="font-serif text-4xl text-brand-cream">Shipping Policy</h1>
      </div>

      {[
        {
          title: "Flat-Rate Shipping",
          body: "We charge a flat shipping fee of R80 on all orders, regardless of size or weight. This fee is displayed at checkout before you confirm payment.",
        },
        {
          title: "Where We Ship",
          body: "We currently ship to all major cities and towns within South Africa, including deliveries to Cape Town, Johannesburg, Durban, Pretoria, and beyond.",
        },
        {
          title: "Delivery Times",
          body: "Because we source products after your order is placed, please allow 3–5 business days for sourcing plus 2–3 business days for courier delivery. Total estimated time: 5–10 business days. You will receive a tracking number once your order is dispatched.",
        },
        {
          title: "Order Tracking",
          body: "Once your order is shipped, a tracking number will be added to your order page and emailed to you. You can track your order at any time by logging in to your account.",
        },
        {
          title: "Delays",
          body: "We do our best to meet estimated timelines. However, we are not liable for delays caused by supplier stock fluctuations or courier service disruptions. We will always communicate delays via email.",
        },
        {
          title: "Questions?",
          body: "Email us at support@strands.co.za and we'll respond within 1 business day.",
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
