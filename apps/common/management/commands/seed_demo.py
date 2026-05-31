"""Seed sample categories, products, vendor, and coupon for development."""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product, ProductImage, ProductVariant
from apps.vendors.models import VendorProfile, CommissionRule
from apps.orders.models import Coupon
from apps.users.models import Address, Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Seed sample data for Printverse"

    def handle(self, *args, **opts):
        # Admin
        admin, _ = User.objects.get_or_create(
            email="admin@printverse.app",
            defaults={"role": "superadmin", "is_staff": True, "is_superuser": True},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.role = "superadmin"
        admin.set_password("admin12345")
        admin.save()
        self.stdout.write(self.style.SUCCESS("Admin:    admin@printverse.app / admin12345"))

        # Customer demo
        customer, _ = User.objects.get_or_create(
            email="customer@printverse.app",
            defaults={"role": "customer", "first_name": "Demo", "last_name": "Customer"},
        )
        customer.set_password("customer12345")
        customer.role = "customer"
        customer.save()
        self.stdout.write(self.style.SUCCESS("Customer: customer@printverse.app / customer12345"))

        # Vendor user
        vendor_user, _ = User.objects.get_or_create(
            email="vendor@printverse.app",
            defaults={"role": "vendor", "first_name": "Demo", "last_name": "Vendor"},
        )
        vendor_user.set_password("vendor12345")
        vendor_user.role = "vendor"
        vendor_user.save()
        self.stdout.write(self.style.SUCCESS("Vendor:   vendor@printverse.app / vendor12345"))

        Profile.objects.get_or_create(user=customer, defaults={"full_name": "Demo Customer"})
        Address.objects.get_or_create(
            user=customer, label="Home",
            defaults={
                "full_name": "Demo Customer",
                "phone": "+919999999999",
                "line1": "12 MG Road",
                "line2": "Indiranagar",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560038",
                "country": "India",
                "is_default": True,
            },
        )
        vp, _ = VendorProfile.objects.get_or_create(
            user=vendor_user,
            defaults={"business_name": "Demo Print House", "status": "approved"},
        )
        CommissionRule.objects.get_or_create(is_default=True, defaults={"percent": 15})

        # Categories
        names = ["Men", "Women", "Kids", "Oversized", "Polo", "Hoodie", "Sweatshirts"]
        cats = {n: Category.objects.get_or_create(name=n)[0] for n in names}
        # Category banner images
        cat_images = {
            "Men": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600",
            "Women": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=600",
            "Kids": "https://images.unsplash.com/photo-1519278409-1f56fdda7fe5?w=600",
            "Oversized": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600",
            "Polo": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=600",
            "Hoodie": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600",
            "Sweatshirts": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600",
        }
        for n, c in cats.items():
            if not c.image:
                c.image = cat_images.get(n, "")
                c.save()

        # Real-looking T-shirt mockup images (Unsplash CDN, no auth required)
        product_images = {
            "Classic Cotton Tee": [
                "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800",
                "https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=800",
                "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800",
            ],
            "Premium Polo": [
                "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=800",
                "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=800",
                "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800",
            ],
            "Cozy Hoodie": [
                "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800",
                "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800",
                "https://images.unsplash.com/photo-1572495641004-28421ae29ed4?w=800",
            ],
            "Kids Fun Tee": [
                "https://images.unsplash.com/photo-1519278409-1f56fdda7fe5?w=800",
                "https://images.unsplash.com/photo-1622445275576-721325763afe?w=800",
                "https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=800",
            ],
            "Oversized Streetwear": [
                "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800",
                "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800",
                "https://images.unsplash.com/photo-1593030103066-0093718efeb9?w=800",
            ],
            "Women's Crop Tee": [
                "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800",
                "https://images.unsplash.com/photo-1554568218-0f1715e72254?w=800",
                "https://images.unsplash.com/photo-1485231183945-fffde7cc051e?w=800",
            ],
        }

        # Products
        seed_products = [
            ("Classic Cotton Tee", "Men", "men", Decimal("499"), True, True),
            ("Premium Polo", "Polo", "men", Decimal("799"), True, False),
            ("Cozy Hoodie", "Hoodie", "unisex", Decimal("1299"), False, True),
            ("Kids Fun Tee", "Kids", "kids", Decimal("399"), False, False),
            ("Oversized Streetwear", "Oversized", "unisex", Decimal("899"), True, True),
            ("Women's Crop Tee", "Women", "women", Decimal("549"), False, True),
        ]
        for name, cat, gender, price, featured, trending in seed_products:
            p, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "vendor": vp,
                    "category": cats[cat],
                    "gender": gender,
                    "base_price": price,
                    "print_cost": Decimal("100"),
                    "description": f"High-quality customizable {name.lower()} — soft 180 GSM cotton, ringspun, pre-shrunk. Perfect canvas for your custom design.",
                    "fabric": "100% Cotton",
                    "is_featured": featured,
                    "is_trending": trending,
                    "is_new_arrival": True,
                    "is_best_seller": featured,
                    "print_areas": ["front", "back", "left_sleeve", "right_sleeve"],
                    "rating": Decimal("4.5"),
                    "review_count": 24,
                },
            )

            # Always refresh images so re-seeding upgrades placeholders to real ones.
            p.images.all().delete()
            for i, url in enumerate(product_images.get(name, [])):
                ProductImage.objects.create(product=p, image_url=url, sort_order=i, alt=name)

            if created:
                for size in ["S", "M", "L", "XL"]:
                    for color, hexv in [("Black", "#000000"), ("White", "#FFFFFF"), ("Navy", "#0A1F44")]:
                        ProductVariant.objects.create(
                            product=p, size=size, color_name=color, color_hex=hexv,
                            sku=f"{p.id.hex[:6]}-{size}-{color[:2].upper()}", stock=50,
                        )

        Coupon.objects.get_or_create(
            code="WELCOME10",
            defaults={"type": "percent", "value": Decimal("10"), "max_discount": Decimal("200"), "min_subtotal": Decimal("499")},
        )

        self.stdout.write(self.style.SUCCESS("Seed complete."))

