import re
from typing import List, Optional
from sqlalchemy import or_, and_, cast, String
from sqlalchemy.orm import Session
from app.models.product import Product, ProductVariant, Brand, Category, PumpModel, ProductCompatibility

def parse_search_query(raw_query: str):
    cleaned = raw_query.strip().lower()
    
    # Check for part/ref number patterns: "part 11", "ref 11", "part #11", "#11", or standalone digits
    ref_match = re.search(r'(?:part|ref|item|#)?\s*#?\s*(\b\d{1,3}\b)', cleaned)
    ref_number = None
    if ref_match:
        try:
            val = int(ref_match.group(1))
            if 1 <= val <= 100:  # Valid range
                ref_number = val
        except ValueError:
            pass

    # Extract mm dimension pattern (e.g. "120mm", "120 mm", "50mm")
    dim_match = re.search(r'(\d+(?:\.\d+)?)\s*mm', cleaned)
    dim_val = dim_match.group(1) if dim_match else None

    # Detect brand names
    brand_hint = None
    if "psg" in cleaned:
        brand_hint = "psg"
    elif "cri" in cleaned:
        brand_hint = "cri"

    # Clean tokens for text search
    tokens = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned).split()
    # Filter out stopwords
    stopwords = {"part", "ref", "no", "number", "for", "in", "and", "the", "a", "an", "pump", "pumps"}
    filtered_tokens = [t for t in tokens if t not in stopwords and len(t) > 1]

    return {
        "raw": raw_query,
        "ref_number": ref_number,
        "dim_val": dim_val,
        "brand_hint": brand_hint,
        "tokens": filtered_tokens
    }

def search_products(
    db: Session,
    query: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    stock_status: Optional[str] = None,
    published_only: bool = True,
    limit: int = 50,
    offset: int = 0
):
    q = db.query(Product).outerjoin(Brand, Product.brand_id == Brand.id)\
                         .outerjoin(Category, Product.category_id == Category.id)\
                         .outerjoin(ProductVariant, Product.id == ProductVariant.product_id)

    if published_only:
        q = q.filter(Product.published == True)

    if category_id:
        q = q.filter(Product.category_id == category_id)

    if brand_id:
        q = q.filter(Product.brand_id == brand_id)

    if stock_status:
        q = q.filter(Product.stock_status.ilike(f"%{stock_status}%"))

    if query and query.strip():
        parsed = parse_search_query(query)
        conditions = []

        # 1. Exact or matched reference number
        if parsed["ref_number"] is not None:
            conditions.append(Product.reference_number == parsed["ref_number"])

        # 2. Token conditions
        for token in parsed["tokens"]:
            token_like = f"%{token}%"
            token_condition = or_(
                Product.name.ilike(token_like),
                Product.description.ilike(token_like),
                Product.model_number.ilike(token_like),
                Product.manufacturer_part_number.ilike(token_like),
                Brand.name.ilike(token_like),
                Category.name.ilike(token_like),
                ProductVariant.variant_name.ilike(token_like),
                ProductVariant.material.ilike(token_like),
                ProductVariant.compatible_models.ilike(token_like),
                cast(Product.specifications, String).ilike(token_like),
                cast(ProductVariant.dimensions, String).ilike(token_like)
            )
            conditions.append(token_condition)

        # 3. Dimension value search
        if parsed["dim_val"]:
            dim_like = f"%{parsed['dim_val']}%"
            conditions.append(or_(
                Product.name.ilike(dim_like),
                cast(ProductVariant.dimensions, String).ilike(dim_like),
                ProductVariant.variant_name.ilike(dim_like)
            ))

        # 4. Brand hint
        if parsed["brand_hint"]:
            conditions.append(Brand.name.ilike(f"%{parsed['brand_hint']}%"))

        if conditions:
            # We want products matching any strong conditions, or all tokens
            q = q.filter(or_(*conditions))

    # Distinct products
    q = q.distinct(Product.id)
    total = q.count()
    products = q.order_by(Product.reference_number.asc()).offset(offset).limit(limit).all()

    return products, total
