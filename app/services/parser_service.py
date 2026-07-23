from itertools import product
import re
from bs4 import BeautifulSoup # type: ignore


from app.utils.strength_normalizer import (
    normalize_strength,
    is_valid_strength
)

from app.utils.canonicalizer import (
    normalize_dosage_form,
    normalize_route
)


# =========================================================
# CLEAN STRENGTHS
# =========================================================

def clean_strengths(strengths):
    """
    Remove duplicates and invalid strengths.
    """

    cleaned = set()

    for strength in strengths:

        if not strength:
            continue

        strength = normalize_strength(strength)

        if not is_valid_strength(strength):
            continue

        # Ignore mL-only values
        if strength.lower().strip() == "ml":
            continue

        try:

            numeric_match = re.findall(
                r"\d+\.?\d*",
                strength
            )

            if numeric_match:

                number = float(numeric_match[0])

                # Ignore unrealistic strengths
                if number > 100:
                    continue

                if number <= 0:
                    continue

        except:
            continue

        cleaned.add(strength)

    return sorted(
        list(cleaned),
        key=lambda x: float(
            re.findall(r"\d+\.?\d*", x)[0]
        )
    )


# =========================================================
# PRIMARY API EXTRACTION (Fallback)
# =========================================================

def extract_primary_api(full_text):

    patterns = [

        r"\(([A-Za-z0-9\s\-]+)\)\s+injection",
        r"\(([A-Za-z0-9\s\-]+)\)\s+tablets",
        r"\(([A-Za-z0-9\s\-]+)\)\s+capsules",
        r"\(([A-Za-z0-9\s\-]+)\)\s+for"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            full_text,
            re.IGNORECASE
        )

        if match:

            return match.group(1).strip().lower()

    return "Unknown API"


# =========================================================
# SPLIT COMBINATION APIs
# =========================================================

def split_active_ingredients(api_name: str):

    if not api_name:
        return []

    separators = [
        " AND ",
        " + ",
        " WITH ",
    ]

    ingredients = [api_name]

    for sep in separators:

        new = []

        for ingredient in ingredients:

            if sep in ingredient.upper():

                parts = re.split(
                    rf"\s*{re.escape(sep.strip())}\s*",
                    ingredient,
                    flags=re.IGNORECASE
                )

                new.extend(parts)

            else:

                new.append(ingredient)

        ingredients = new

    cleaned = []

    seen = set()

    for ingredient in ingredients:

        ingredient = ingredient.strip()

        if not ingredient:
            continue

        if ingredient.upper() in seen:
            continue

        seen.add(ingredient.upper())

        cleaned.append(ingredient)

    return cleaned

# =========================================================
# INACTIVE INGREDIENT EXTRACTION
# =========================================================

def extract_inactive_ingredients(text):

    inactive = []

    match = re.search(
        r"inactive ingredients:(.*?)(?:structural formula|12 clinical pharmacology|mechanism of action)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        section = match.group(1)

        items = section.split(";")

        for item in items:

            item = item.strip()

            item = re.sub(
                r"\d+\.?\d*\s?(mg|g|ml)",
                "",
                item,
                flags=re.IGNORECASE
            )

            item = item.strip(" ,.;:")

            if (
                item
                and len(item) < 100
                and "contains" not in item.lower()
            ):
                inactive.append(item)

    return list(set(inactive))
    
# =========================================================
# PARSER V2
# Replace extract_manufactured_products() completely
# =========================================================

# =========================================================
# EXTRACT MANUFACTURED PRODUCTS (Parser V2)
# =========================================================

def extract_manufactured_products(soup):

    formulations = []
    seen = set()

    # FDA SPL stores every marketed presentation
    # inside manufacturedProduct nodes.
    products = soup.find_all("manufacturedProduct")

    print("\n========== PARSER V2 ==========")
    print("manufacturedProduct nodes:", len(products))

    for product in products:


        print("\n========================")
        print(product.prettify()[:2500])
        

        # --------------------------------------------------
        # API
        # --------------------------------------------------

        api_name = ""

        generic = product.find("genericMedicine")

        if generic:

            name = generic.find("name")

            if name:
                api_name = name.get_text(strip=True)

        if not api_name:

            ingredient = product.find("ingredient")

            if ingredient:

                substance = ingredient.find("ingredientSubstance")

                if substance:

                    name = substance.find("name")

                    if name:
                        api_name = name.get_text(strip=True)

        # --------------------------------------------------
        # DOSAGE FORM
        # --------------------------------------------------

        dosage_form = ""

        form = product.find("formCode")

        if form:

            dosage_form = form.get(
                "displayName",
                ""
            )

        dosage_form = normalize_dosage_form(
            dosage_form
        )

        # --------------------------------------------------
        # ROUTE
        # --------------------------------------------------

        route = ""

        route_tag = product.find("routeCode")

        if route_tag:

            route = route_tag.get(
                "displayName",
                ""
            )

        route = normalize_route(route)
        if not route:
            route = "UNKNOWN"

        # --------------------------------------------------
        # INGREDIENTS
        # --------------------------------------------------

        ingredients = product.find_all(
            "ingredient",
            recursive=False
        )

        if not ingredients:

            ingredients = product.find_all("ingredient")

        for ingredient in ingredients:

            ingredient_name = api_name

            substance = ingredient.find(
                "ingredientSubstance"
            )

            if substance:

                name = substance.find("name")

                if name:

                    ingredient_name = (
                        name.get_text(strip=True)
                    )

            ingredient_list = split_active_ingredients(
                ingredient_name
            )

            quantity = ingredient.find("quantity")

            if not quantity:
                continue

            numerator = quantity.find("numerator")

            if not numerator:
                continue

            value = numerator.get(
                "value",
                ""
            )

            unit = numerator.get(
                "unit",
                ""
            )

            if not value:
                continue

            strength = normalize_strength(
                f"{value} {unit}"
            )

            for api in ingredient_list:

                # Skip UNKNOWN when we already have a better route
                if route == "UNKNOWN":

                    better = any(
                        f["api_name"].upper() == api.upper()
                        and f["dosage_form"] == dosage_form
                        and f["strength"] == strength
                        and f["route"] != "UNKNOWN"
                        for f in formulations
                    )

                    if better:
                        continue

                key = (
                    api.upper(),
                    dosage_form,
                    route,
                    strength
                )

                if key in seen:
                    continue

                seen.add(key)

                formulations.append({

                    "api_name": api,

                    "dosage_form": dosage_form,

                    "route": route,

                    "strength": strength

                })

    print("\nFORMULATIONS FOUND:")
    print(len(formulations))

    for row in formulations:
        print(row)

    return formulations


# =========================================================
# MAIN PARSER
# =========================================================

def parse_spl_xml(xml_path):

    with open(xml_path, "r", encoding="utf-8") as file:
        xml_content = file.read()

    soup = BeautifulSoup(xml_content, "xml")

    full_text = soup.get_text(
        " ",
        strip=True
    )

    # =====================================================
    # TITLE
    # =====================================================

    title_tag = soup.find("title")

    title = (
        title_tag.get_text(strip=True)
        if title_tag
        else "N/A"
    )

    # =====================================================
    # MANUFACTURER
    # =====================================================

    manufacturer = "N/A"

    org = soup.find("representedOrganization")

    if org:

        name = org.find("name")

        if name:

            manufacturer = name.get_text(strip=True)



    # =====================================================
    # INACTIVE INGREDIENTS
    # =====================================================

    

    def extract_inactive_ingredients(soup):

        inactive = []

        for ingredient in soup.find_all("ingredient"):

            if ingredient.get("classCode") != "IACT":
                continue

            name = ingredient.find("name")

            if not name:
                continue

            ingredient_name = name.get_text(strip=True)

            if ingredient_name not in inactive:
                inactive.append(ingredient_name)

        return inactive
    
    inactive_ingredients = extract_inactive_ingredients(soup)

    # =====================================================
    # STRUCTURED PRODUCT PARSER (Parser V2)
    # =====================================================

    formulations = extract_manufactured_products(
        soup
    )

    strengths = sorted(
        list({
            f["strength"]
            for f in formulations
            if f["strength"]
        })
    )

    dosage_forms = sorted(
        list({
            f["dosage_form"]
            for f in formulations
            if f["dosage_form"]
        })
    )

    routes = sorted(
        list({
            f["route"]
            for f in formulations
            if f["route"]
        })
    )

    active_ingredients = sorted(
        list({
            f["api_name"]
            for f in formulations
            if f["api_name"]
        })
    )

    # Fallback if API wasn't found structurally
    if not active_ingredients:

        active_ingredients = [
            extract_primary_api(
                full_text
            )
        ]

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    return {
        "title": title,
        "manufacturer": manufacturer,
        "active_ingredients": active_ingredients,
        "dosage_form": dosage_forms,
        "route": routes,
        "strengths": strengths,
        "inactive_ingredients": inactive_ingredients,
        "formulations": formulations
    }