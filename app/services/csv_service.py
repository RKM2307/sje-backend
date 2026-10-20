import csv
import io
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.product import Product, ProductVariant, Category, Brand

CSV_COLUMNS = [
    "Reference ID",
    "Product Name",
    "Category",
    "Brand",
    "Manufacturer Part Number",
    "Pump Model",
    "Diameter (mm)",
    "Inner Diameter (mm)",
    "Outer Diameter (mm)",
    "Length (mm)",
    "Thickness (mm)",
    "Material",
    "Selling Price",
    "Stock Quantity",
    "Stock Status",
    "Image URL",
    "Verified",
    "Published"
]

def generate_csv_template(db: Session) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_COLUMNS)

    products = db.query(Product).order_by(Product.reference_number.asc()).all()
    for prod in products:
        category_name = prod.category.name if prod.category else ""
        brand_name = prod.brand.name if prod.brand else ""
        
        # If product has variants, export them or base row
        if prod.variants:
            for v in prod.variants:
                dims = v.dimensions or {}
                writer.writerow([
                    prod.reference_number,
                    prod.name,
                    category_name,
                    brand_name,
                    prod.manufacturer_part_number or "",
                    v.compatible_models or "",
                    dims.get("diameter_mm", ""),
                    dims.get("inner_diameter_mm", ""),
                    dims.get("outer_diameter_mm", ""),
                    dims.get("length_mm", ""),
                    dims.get("thickness_mm", ""),
                    v.material or "",
                    v.price if v.price is not None else "",
                    v.quantity,
                    v.stock_status,
                    v.image_url or prod.primary_image_url or "",
                    "Yes" if prod.published else "No",
                    "Yes" if prod.published else "No"
                ])
        else:
            writer.writerow([
                prod.reference_number,
                prod.name,
                category_name,
                brand_name,
                prod.manufacturer_part_number or "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                0,
                prod.stock_status,
                prod.primary_image_url or "",
                "No",
                "No"
            ])

    return output.getvalue()

def process_csv_import(csv_content: str, db: Session) -> Tuple[int, int, List[str]]:
    f = io.StringIO(csv_content.strip())
    reader = csv.DictReader(f)
    
    updated_count = 0
    variant_count = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        ref_id_str = row.get("Reference ID", "").strip()
        if not ref_id_str:
            continue
        try:
            ref_id = int(ref_id_str)
        except ValueError:
            errors.append(f"Row {row_num}: Invalid Reference ID '{ref_id_str}'")
            continue

        product = db.query(Product).filter(Product.reference_number == ref_id).first()
        if not product:
            errors.append(f"Row {row_num}: Product with Reference ID {ref_id} not found in database.")
            continue

        # Optional updates to product
        prod_name = row.get("Product Name", "").strip()
        if prod_name:
            product.name = prod_name
        
        cat_name = row.get("Category", "").strip()
        if cat_name:
            cat = db.query(Category).filter(Category.name.ilike(cat_name)).first()
            if cat:
                product.category_id = cat.id

        brand_name = row.get("Brand", "").strip()
        if brand_name:
            brand = db.query(Brand).filter(Brand.name.ilike(brand_name)).first()
            if brand:
                product.brand_id = brand.id

        mfg_part = row.get("Manufacturer Part Number", "").strip()
        if mfg_part:
            product.manufacturer_part_number = mfg_part

        img_url = row.get("Image URL", "").strip()
        if img_url:
            product.primary_image_url = img_url

        stock_status = row.get("Stock Status", "").strip()
        if stock_status:
            product.stock_status = stock_status

        published_val = row.get("Published", "").strip().lower()
        if published_val in ["true", "yes", "1", "y"]:
            product.published = True
        elif published_val in ["false", "no", "0", "n"]:
            product.published = False

        # Handle dimensions and variant creation/update
        dia = row.get("Diameter (mm)", "").strip()
        inner_dia = row.get("Inner Diameter (mm)", "").strip()
        outer_dia = row.get("Outer Diameter (mm)", "").strip()
        length = row.get("Length (mm)", "").strip()
        thickness = row.get("Thickness (mm)", "").strip()
        material = row.get("Material", "").strip()
        pump_model = row.get("Pump Model", "").strip()
        price_str = row.get("Selling Price", "").strip()
        qty_str = row.get("Stock Quantity", "").strip()

        # Check if row has variant-specific data
        has_variant_data = any([dia, inner_dia, outer_dia, length, thickness, material, pump_model, price_str])
        
        if has_variant_data:
            dimensions = {}
            if dia: dimensions["diameter_mm"] = dia
            if inner_dia: dimensions["inner_diameter_mm"] = inner_dia
            if outer_dia: dimensions["outer_diameter_mm"] = outer_dia
            if length: dimensions["length_mm"] = length
            if thickness: dimensions["thickness_mm"] = thickness

            price = None
            if price_str:
                try:
                    price = float(price_str.replace("₹", "").replace(",", "").strip())
                except ValueError:
                    pass

            qty = 0
            if qty_str:
                try:
                    qty = int(qty_str)
                except ValueError:
                    pass

            variant_name_parts = [f"Ref {ref_id}"]
            if dia: variant_name_parts.append(f"{dia}mm Dia")
            if inner_dia and outer_dia: variant_name_parts.append(f"ID {inner_dia}mm / OD {outer_dia}mm")
            if material: variant_name_parts.append(material)
            if pump_model: variant_name_parts.append(pump_model)
            
            variant_title = " - ".join(variant_name_parts) if len(variant_name_parts) > 1 else f"Standard Size (Ref {ref_id})"

            # Find or create variant
            existing_variant = db.query(ProductVariant).filter(
                ProductVariant.product_id == product.id,
                ProductVariant.variant_name == variant_title
            ).first()

            if not existing_variant:
                new_variant = ProductVariant(
                    product_id=product.id,
                    variant_name=variant_title,
                    sku=f"SJE-{ref_id:03d}-{len(product.variants) + 1:02d}",
                    dimensions=dimensions,
                    material=material or None,
                    compatible_models=pump_model or None,
                    price=price,
                    quantity=qty,
                    stock_status=stock_status or "Contact for Price",
                    image_url=img_url or None,
                    active=True
                )
                db.add(new_variant)
                variant_count += 1
            else:
                existing_variant.dimensions = dimensions
                if material: existing_variant.material = material
                if pump_model: existing_variant.compatible_models = pump_model
                if price is not None: existing_variant.price = price
                existing_variant.quantity = qty
                if stock_status: existing_variant.stock_status = stock_status
                if img_url: existing_variant.image_url = img_url

        updated_count += 1

    db.commit()
    return updated_count, variant_count, errors
