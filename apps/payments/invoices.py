"""Generate invoice / receipt PDFs using reportlab."""
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_invoice_pdf(order) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, h - 50, "Printverse — Tax Invoice")
    c.setFont("Helvetica", 10)
    c.drawString(40, h - 75, f"Order: {order.order_number}")
    c.drawString(40, h - 90, f"Customer: {order.user.email}")
    c.drawString(40, h - 105, f"Status: {order.status}")

    y = h - 140
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Item")
    c.drawString(280, y, "Qty")
    c.drawString(340, y, "Unit")
    c.drawString(420, y, "Print")
    c.drawString(490, y, "Total")
    y -= 16
    c.setFont("Helvetica", 10)
    for it in order.items.all():
        c.drawString(40, y, f"{it.product.name} [{it.variant.size}/{it.variant.color_name}]")
        c.drawString(280, y, str(it.quantity))
        c.drawString(340, y, f"{it.unit_price}")
        c.drawString(420, y, f"{it.print_cost}")
        c.drawString(490, y, f"{it.line_total}")
        y -= 14

    y -= 20
    for label, val in [
        ("Subtotal", order.subtotal),
        ("Print", order.print_cost_total),
        ("Shipping", order.shipping),
        ("Tax", order.tax),
        ("Discount", -order.discount),
        ("Total", order.total),
    ]:
        c.drawString(420, y, label)
        c.drawString(490, y, f"{val}")
        y -= 14

    c.showPage()
    c.save()
    return buf.getvalue()

