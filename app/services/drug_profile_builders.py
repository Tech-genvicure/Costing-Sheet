from app.database.repository import DrugRepository


class DrugProfileBuilder:
    """
    Builds a unified Drug Profile by combining data from
    Drugs@FDA and the Orange Book.
    """

    def __init__(self):
        self.repo = DrugRepository()

    def close(self):
        self.repo.close()

    def build(
        self,
        appl_no=None,
        brand_name=None,
        generic_name=None,
    ):
        """
        Build a complete Drug Profile.

        Parameters
        ----------
        appl_no : str
        brand_name : str
        generic_name : str
        """

        # ------------------------------
        # Resolve Application Number
        # ------------------------------

        if appl_no is None:

            appl_no = self._resolve_application_number(
                brand_name=brand_name,
                generic_name=generic_name,
            )

        if appl_no is None:
            return None

        # ------------------------------
        # Fetch raw data
        # ------------------------------

        application = self.repo.get_application(appl_no)

        products = self.repo.get_products(appl_no)

        orange = self.repo.get_orange_product(appl_no)

        patents = self.repo.get_patents(appl_no)

        exclusivities = self.repo.get_exclusivities(appl_no)

        submission = self.repo.get_latest_submission(appl_no)

        marketing = None

        if products:

            first = products[0]

            marketing = self.repo.get_marketing_status(
                appl_no,
                first["ProductNo"],
            )

        # ------------------------------
        # Assemble profile
        # ------------------------------

        profile = self._assemble_profile(
            application,
            products,
            orange,
            patents,
            exclusivities,
            submission,
            marketing,
        )

        return profile
    
    #Resolve Application Number
    def _resolve_application_number(
        self,
        brand_name=None,
        generic_name=None,
    ):
        """
        Resolve a drug into an Application Number.
        """

        if brand_name:

            rows = self.repo.search_drug(brand_name)

        elif generic_name:

            rows = self.repo.search_drug(generic_name)

        else:
            return None

        if not rows:
            return None

        return rows[0]["ApplNo"]
    
    #Assemble the Profile
    def _assemble_profile(
        self,
        application,
        products,
        orange,
        patents,
        exclusivities,
        submission,
        marketing,
    ):

        profile = {

            # =====================================
            # IDENTIFICATION
            # =====================================

            "application_no":
                application["ApplNo"],

            "application_type":
                application["ApplType"],

            "brand_name":
                orange["Trade_Name"] if orange else None,

            "generic_name":
                orange["Ingredient"] if orange else None,

            # =====================================
            # COMPANY
            # =====================================

            "applicant": {

                "short_name":
                    orange["Applicant"] if orange else None,

                "full_name":
                    orange["Applicant_Full_Name"] if orange else None,

            },

            # =====================================
            # REGULATORY
            # =====================================

            "approval_date":
                orange["Approval_Date"] if orange else None,

            "marketing_status":
                marketing,

            "review_priority":
                submission["ReviewPriority"] if submission else None,

            # =====================================
            # ORANGE BOOK
            # =====================================

            "rld":
                orange["RLD"] == "Yes" if orange else False,

            "rs":
                orange["RS"] == "Yes" if orange else False,

            "te_code":
                orange["TE_Code"] if orange else None,

            # =====================================
            # PRODUCTS
            # =====================================

            "products":
                products,

            "strengths":
                self._extract_strengths(products),

            # =====================================
            # RAW REGULATORY DATA
            # =====================================

            "patents_raw":
                patents,

            "exclusivities_raw":
                exclusivities,

            # =====================================
            # NORMALIZED
            # =====================================

            "patents":
                self._unique_patents(patents),

            "exclusivities":
                self._unique_exclusivities(exclusivities),
        }

        return profile
    
    #Normalize Patents
    def _unique_patents(self, patents):

        unique = {}

        for patent in patents:

            key = patent["Patent_No"]

            if key not in unique:

                unique[key] = patent

        return list(unique.values())
    
    #Normalize Exclusivities
    def _unique_exclusivities(self, exclusivities):

        unique = {}

        for item in exclusivities:

            key = (
                item["Exclusivity_Code"],
                item["Exclusivity_Date"],
            )

            if key not in unique:

                unique[key] = item

        return list(unique.values())
    
    #Extract Strengths
    def _extract_strengths(self, products):

        strengths = []

        seen = set()

        for product in products:

            strength = product.get("Strength")

            if strength and strength not in seen:

                strengths.append(strength)

                seen.add(strength)

        return strengths

    def get_variants(self, drug_name):

        rows = self.repo.get_available_variants(drug_name)

        variants = []
        seen = set()

        for row in rows:

            form = row.get("Form", "")

            if ";" in form:
                dosage_form, route = form.split(";", 1)
            else:
                dosage_form = form
                route = ""

            # ---------- Display Name ----------
            display_form = dosage_form.title()

            if dosage_form.upper() == "SOLUTION" and route.upper() == "SUBCUTANEOUS":
                display_form = "Injection"

            elif dosage_form.upper() == "SOLUTION" and route.upper() == "INTRAVENOUS":
                display_form = "Injection"

            elif dosage_form.upper() == "POWDER":
                display_form = "Powder"

            elif dosage_form.upper() == "TABLET":
                display_form = "Tablet"

            elif dosage_form.upper() == "CAPSULE":
                display_form = "Capsule"

            applicant = (
                row.get("Applicant")
                or row.get("Applicant_Full_Name")
                or row.get("SponsorName")
            )

            key = (
                row["ApplNo"],
                display_form,
                applicant,
            )

            if key in seen:
                continue

            seen.add(key)

            variants.append({

                "application_no": row["ApplNo"],
                "product_no": row["ProductNo"],

                "dosage_form": display_form,
                "route": route.title(),

                "applicant": applicant,
                "applicant_full_name": applicant,

                "sponsor": row.get("SponsorName")

            })

        return variants