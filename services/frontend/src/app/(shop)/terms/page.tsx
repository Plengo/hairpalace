export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-20 space-y-10">
      <div>
        <p className="text-[11px] tracking-widest text-brand-gold uppercase mb-2">Legal</p>
        <h1 className="font-serif text-4xl text-brand-cream">Terms of Service</h1>
        <p className="text-xs text-brand-muted mt-2">Last updated: {new Date().toLocaleDateString("en-ZA", { month: "long", year: "numeric" })}</p>
      </div>

      {[
        {
          title: "1. About STRANDS",
          body: "STRANDS is an order-first hair and beauty retailer registered in South Africa. We accept orders, collect payment, source your products from verified suppliers, and deliver to your door. By placing an order you agree to these terms.",
        },
        {
          title: "2. Order Process",
          body: "All products are sourced on request. When you place an order and payment is confirmed, we begin sourcing the items on your behalf. Estimated lead times are displayed on each product page and are indicative only.",
        },
        {
          title: "3. Payment",
          body: "Payment is collected at the time of ordering via Stripe. All prices are displayed in South African Rand (ZAR) inclusive of VAT where applicable. We accept all major credit and debit cards.",
        },
        {
          title: "4. Cancellations & Refunds",
          body: "You may cancel your order within 24 hours of placement for a full refund, provided sourcing has not yet commenced. Once sourcing begins, cancellations will be subject to supplier restocking fees. Please email us at support@strands.co.za.",
        },
        {
          title: "5. Delivery",
          body: "We ship within South Africa. A flat shipping fee of R80 applies to all orders. Estimated delivery is 5–10 business days after order confirmation. We are not liable for delays caused by courier partners.",
        },
        {
          title: "6. Intellectual Property",
          body: "All content on this website including text, images, logos, and product descriptions is the property of STRANDS and may not be reproduced without written consent.",
        },
        {
          title: "7. Limitation of Liability",
          body: "To the maximum extent permitted by South African law, STRANDS shall not be liable for any indirect, incidental, or consequential damages arising from the use of our service.",
        },
        {
          title: "8. Governing Law",
          body: "These terms are governed by the laws of the Republic of South Africa. Disputes shall be resolved in the courts of the Republic.",
        },
        {
          title: "9. Contact",
          body: "For any queries regarding these terms, contact us at support@strands.co.za.",
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
